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



###### M/M/4 model ############################

# Model
class Source(Process):
    """generate random arrivals"""
    def run(self, N, lamb, mu):
        for i in range(N):
            a = Arrival(str(i))
            activate(a, a.run(mu))
            t = random.expovariate(lamb)
            yield hold, self, t


class Arrival(Process):
    """an arrival"""
    n = 0 # class variable (number in system)
    
    def run(self, mu):
        # Event: arrival
        Arrival.n += 1 # number in system
        arrivetime = now()
        G.numbermon.observe(Arrival.n)
        if (Arrival.n>0):
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
        
        Arrival.n-=1
        G.numbermon.observe(Arrival.n)
        if (Arrival.n>0):
            G.busymon.observe(1)
        else:
            G.busymon.observe(0)
        delay = now()-arrivetime
        G.delaymon.observe(delay)


class G:
    server = 'dummy'
    delaymon = 'Monitor'
    numbermon = 'Monitor'
    busymon = 'Monitor'


def model(c, N, lamb, mu, maxtime, rvseed):
    # setup
    initialize()
    random.seed(rvseed)
    G.server = Resource(c, monitored = True)
    G.delaymon = Monitor()
    G.numbermon = Monitor()
    G.busymon = Monitor()
  
    Arrival.n = 0
    
    # simulate
    s = Source('Source')
    activate(s, s.run(N, lamb, mu))
    simulate(until=maxtime)

    # gather performance measures
    W = G.delaymon.mean()
    L = G.numbermon.timeAverage()
    B = G.busymon.mean()
    return(W,L,B)


## Experiment ----------------

# objects to hold performance measures
allW = []
allL= []
allB = []
allLambdaEffective = []
# allBmon = []

# run experiment
for k in range(50):
    seed = 123*k
    result = model(c=4, N=10000, lamb=1/23.02481, mu=1/34.00496, maxtime=2000000, rvseed=seed)
    allW.append(result[0])
    allL.append(result[1])
    allB.append(result[2])
    allLambdaEffective.append(result[1]/result[0])
#     allBmon.append(result[3])

#########################################
# estimate simulated performance measures

m1_W = np.mean(allW)
m1_L = np.mean(allL)
m1_B = np.mean(allB)
print("Estimate of W:", np.mean(allW))
print("Conf in of W:", conf(allW))
print("Estimate of L:", np.mean(allL))
print("Conf in of L:", conf(allL))
print("Estimate of B:", np.mean(allB))
print("Conf int of B:", conf(allB))
print("Estimate of LambdaEffective:", np.mean(allLambdaEffective))
print("Conf int of LambdaEffective:", conf(allLambdaEffective))
# print("Estimate from the Resource monitor: ", np.mean(allBmon))
# print("Conf int of Bmon: ", conf(allBmon))


######## Plot performance measures against baseline estimates ######


plt.plot(allL, color = "darkblue", label = "simulated") # average number of customers in system
plt.axhline(1.663, color = "blue", label = "theoretic", ls = "--")
plt.title("Average number of customers: M/M/4")
plt.legend()
plt.show()

plt.plot(allW, color = "green", label = "simulated") # average time in the system
plt.axhline(38.2559, color = "lime", label = "theoretic", ls = "--")
plt.title("Average time (s) in the system: M/M/4")
plt.legend()
plt.show()

plt.plot(allB, color = "orange", label = "simulated") # average utilisation rate
plt.axhline(0.3699, color = "orangered", label = "theoretic", ls = "--")
plt.title("Average utilisation: M/M/4")
plt.legend()
plt.show()


