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


######################################################
#
# empirical data random variates:  Dr Binh Nguyen
#
######################################################

def draw_empirical(data, r):
    """one draw (for given r ~ U(0,1)) from the
    empirical cdf based on data"""
    
    d = {x: data.count(x) for x in data}
    obs_values, freq = zip( *sorted( zip(d.keys(), d.values())))
    obs_values = list(obs_values)
    freq = list(freq)
    empf = [x*1.0/len(data) for x in freq]
    ecum = np.cumsum(empf).tolist()
    ecum.insert(0, 0)
    obs_values.insert(0,0)
   
    for x in ecum:
         if r <= x:
            rpt = x
            break
    r_end = ecum.index(rpt)
    y = obs_values[r_end] - 1.0*(ecum[r_end]-r)*(obs_values[r_end]-
        obs_values[r_end-1])/(ecum[r_end]-ecum[r_end-1])
    return y



###### Best fit model ############################
#
#  Inter - arrivals = Gamma(2, 2/23)
#  Service times = Exp(1/34)
#
###################################################

# Use draw_empirical function to generate data
class Source3(Process):
    """generate random arrivals"""
    def run(self, N, arr_data, serv_data):
        for i in range(N):
            a = Arrival3(str(i))
            activate(a, a.run(list(serv_data)))
            r = random.random()
            t = draw_empirical(list(arr_data), r)
            yield hold, self, t


 class Arrival3(Process):
    """an arrival"""
    n = 0 # class variable (number in system)
    
    def run(self, serv_data):
        # Event: arrival
        Arrival3.n += 1 # number in system
        arrivetime = now()
        G.numbermon.observe(Arrival3.n)
        
        if (Arrival3.n>0):
            G.busymon.observe(1)
        else:
            G.busymon.observe(0)

        yield request, self, G.server
        # ... waiting in queue for server to be empty (delay) ...

        # Event: service begins
        r = random.random()
        t = draw_empirical(list(serv_data), r)
        
        yield hold, self, t
        # ... now being served (activity) ...

        # Event: service ends
        yield release, self, G.server 

        Arrival3.n-=1
        
        G.numbermon.observe(Arrival3.n)
        if (Arrival3.n>0):
            G.busymon.observe(1)
            
        else:
            G.busymon.observe(0)
            
        delay = now()-arrivetime
        G.delaymon.observe(delay) 
        

        
def model3(c, N, maxtime, rvseed, arr_data, serv_data):
    # setup
    initialize()
    random.seed(rvseed)
    G.server = Resource(c)
    G.delaymon = Monitor()
    G.numbermon = Monitor()
    G.busymon = Monitor()
  
    Arrival3.n = 0
    
    # simulate
    s = Source3('Source')
    activate(s, s.run(N, arr_data, serv_data))
    simulate(until=maxtime)

    # gather performance measures
    W = G.delaymon.mean()
    L = G.numbermon.timeAverage()
    B = G.busymon.timeAverage()
    B_2 = G
    
    return(W,L,B)

class G:
    server = 'dummy'
    delaymon = 'Monitor'
    numbermon = 'Monitor'
    busymon = 'Monitor'


## Experiment ----------------
allW3 = []
allL3= []
allB3 = []
allLambdaEffective3 = []

for k in range(50):
    seed = 123*k
    result = model3(c=4, 
                   N=10000, 
                   arr_data = arr_data,
                   serv_data = serv_data, 
                   maxtime=20000, 
                   rvseed=seed)
    allW3.append(result[0])
    allL3.append(result[1])
    allB3.append(result[2])
    allLambdaEffective3.append(result[1]/result[0])

m3_W = np.mean(allW3)
m3_L = np.mean(allL3)
m3_B = np.mean(allB3)
m3_Leff = np.mean(allLambdaEffective3)
    

#########################################
# estimate simulated performance measures

print("Estimate of W3:", np.mean(allW3))
print("Conf in of W3:", conf(allW3))
print("Estimate of L3:", np.mean(allL3))
print("Conf in of L3:", conf(allL3))
print("Estimate of B3:", np.mean(allB3))
print("Conf int of B3:", conf(allB3))
print("Estimate of LambdaEffective3:", np.mean(allLambdaEffective3))
print("Conf int of LambdaEffective3:", conf(allLambdaEffective3))


######## Plot performance measures against baseline estimates ######


plt.plot(allL3, color = "darkblue", label = "simulated") # average number of customers in system
plt.axhline(1.663, color = "blue", label = "theoretic", ls = "--")
plt.title("Average number of customers: Empirical model")
plt.legend()
plt.show()

plt.plot(allW3, color = "green", label = "simulated") # average time in the system
plt.axhline(38.2559, color = "lime", label = "theoretic", ls = "--")
plt.title("Average time (s) in the system: Empirical model")
plt.legend()
plt.show()

plt.plot(allB3, color = "orange", label = "simulated") # average utilisation rate
plt.axhline(0.3699, color = "orangered", label = "theoretic", ls = "--")
plt.title("Average utilisation: Empirical model")
plt.legend()
plt.show()




################################################################
#
# Comparison plots:  multiple plots
# REQUIRES RUNNING SIMULATION MODELS TO GENERATE OBJECTS
# MM4_simulation.py    Best_fit_simulation.py    Empirical_simulation.py
#
################################################################


####### compare Average number of customers  ######

plt.plot(allL, color = "red", label = "M/M/4 simulated") # average number of customers in system
plt.plot(allL2, color = "blue", label = "Best-fit simulated") # average number of customers in system
plt.plot(allL3, color = "green", label = "Empirical simulated") # average number of customers in system
plt.axhline(1.663, color = "black", label = "theoretic", ls = "--")
plt.title("Average number of customers: All modes")
plt.legend()
plt.show()


####### compare Average time in the system  #######

plt.plot(allW, color = "red", label = "M/M/4 simulated") # average number of customers in system
plt.plot(allW2, color = "blue", label = "Best-fit simulated") # average number of customers in system
plt.plot(allW3, color = "green", label = "Empirical simulated") # average number of customers in system
plt.axhline(38.2559, color = "black", label = "theoretic", ls = "--")
plt.title("Average time (s) in the system: Empirical model")
plt.legend()
plt.show()


####### compare server utilisation  ################

plt.plot(allB, color = "red", label = "M/M/4 simulated") # average number of customers in system
plt.plot(allB2, color = "blue", label = "Best-fit simulated") # average number of customers in system
plt.plot(allB3, color = "green", label = "Empirical simulated") # average number of customers in system
plt.axhline(0.3699, color = "black", label = "theoretic", ls = "--")
plt.title("Average utilisation: Empirical model")
plt.legend(loc = (0.55, 0.55))
plt.show()

