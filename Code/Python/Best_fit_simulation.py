##############################
#
# Queueing system in action
# Bueno, G and Kakau, C
#
##############################

# source code for reading in data and establishing SimPy simulations of observed
# queueing system:  Wellington Railway Station, ticket booths, Wellington NZ, April 2022


# import libraries

from SimPy.Simulation import *
import random
import numpy as np
import math
import pandas as pd
import statsmodels.distributions.empirical_distribution as st
import matplotlib.pyplot as plt

## confidence intervals

## Useful extras
def conf(L):
    """confidence interval"""
    lower = np.mean(L) - 1.96*np.std(L)/math.sqrt(len(L))
    upper = np.mean(L) + 1.96*np.std(L)/math.sqrt(len(L))
    return lower, upper


##################################################


# read in data
# read in empirical data,
# read in raw data
# script in the same directory as datafile

raw_data = pd.read_csv("DATA474_Proj_data.csv", 
                      parse_dates =[
                          ["Date", "Arrive"],
                          ["Date", "Serv_start"],
                          ["Date", "Serv_end"]
                      ])

# extract and store inter-arrival times for use with the draw_empirical function
arr_data = []
for i in range(len(raw_data["Date_Arrive"])):
    if i == 0:
        arr_data.append(0)
    else:
        inter = (raw_data.loc[i, "Date_Arrive"] - raw_data.loc[i-1,"Date_Arrive"]).seconds
        arr_data.append(inter)
        
# store the serving time data for use with the draw_empirical() function
serv_data = raw_data.loc[:,"Serv_time_sec"]



###### Best fit model ############################
#
#  Inter - arrivals = Gamma(2, 2/23)
#  Service times = Exp(1/34)
#
###################################################

# Model 2
class Source2(Process):
    """generate random arrivals"""
    def run(self, N, lamb, mu):
        for i in range(N):
            a = Arrival2(str(i))
            activate(a, a.run(mu))
#             t = random.expovariate(lamb)
            t = np.random.gamma(2, 2/lamb)
            yield hold, self, t


class Arrival2(Process):
    """an arrival"""
    n = 0 # class variable (number in system)
    
    def run(self, mu):
        # Event: arrival
        Arrival2.n += 1 # number in system
        arrivetime = now()
        G.numbermon.observe(Arrival2.n)
        if (Arrival2.n>0):
            G.busymon.observe(1)
        else:
            G.busymon.observe(0)
        
        yield request, self, G.server
        # ... waiting in queue for server to be empty (delay) ...

        # Event: service begins
        t = random.expovariate(mu)
        
        yield hold, self, t
        # ... now being served (activity) ...
        
        # Event: service ends
        yield release, self, G.server 
        
        Arrival2.n-=1
        G.numbermon.observe(Arrival2.n)
        if (Arrival2.n>0):
            G.busymon.observe(1)
        else:
            G.busymon.observe(0)
        delay = now()-arrivetime
        G.delaymon.observe(delay)
        
def model2(c, N, lamb, mu, maxtime, rvseed):
    # setup
    initialize()
    random.seed(rvseed)
    G.server = Resource(c)
    G.delaymon = Monitor()
    G.numbermon = Monitor()
    G.busymon = Monitor()
  
    Arrival2.n = 0
    
    # simulate
    s = Source2('Source')
    activate(s, s.run(N, lamb, mu))
    simulate(until=maxtime)

    # gather performance measures
    W = G.delaymon.mean()
    L = G.numbermon.timeAverage()
    B = G.busymon.timeAverage()
    
    return(W,L,B)

class G:
    server = 'dummy'
    delaymon = 'Monitor'
    numbermon = 'Monitor'
    busymon = 'Monitor'


## Experiment ----------------
allW2 = []
allL2= []
allB2 = []
allLambdaEffective2 = []
for k in range(50):
    seed = 123*k
    result = model2(c=4, N=10000, lamb=1/23, mu=1/34, maxtime=2000000, rvseed=seed)
    allW2.append(result[0])
    allL2.append(result[1])
    allB2.append(result[2])
    allLambdaEffective2.append(result[1]/result[0])

#########################################
# estimate simulated performance measures

m2_W = np.mean(allW2)
m2_L = np.mean(allL2)
m2_B = np.mean(allB2)
m2_Leff = np.mean(allLambdaEffective2)
    
print("Estimate of W2:", np.mean(allW2))
print("Conf in of W2:", conf(allW2))
print("Estimate of L2:", np.mean(allL2))
print("Conf in of L2:", conf(allL2))
print("Estimate of B2:", np.mean(allB2))
print("Conf int of B2:", conf(allB2))
print("Estimate of LambdaEffective:", np.mean(allLambdaEffective2))
print("Conf int of LambdaEffective:", conf(allLambdaEffective2))





