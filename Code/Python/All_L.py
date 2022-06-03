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


####### compare Average number of customers  ######

plt.plot(allL, color = "red", label = "M/M/4 simulated") # average number of customers in system
plt.plot(allL2, color = "blue", label = "Best-fit simulated") # average number of customers in system
plt.plot(allL3, color = "green", label = "Empirical simulated") # average number of customers in system
plt.axhline(1.663, color = "black", label = "theoretic", ls = "--")
plt.title("Average number of customers: All modes")
plt.legend()
plt.show()

