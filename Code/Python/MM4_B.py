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


######## Plot performance measures against baseline estimates ######

plt.plot(allB, color = "orange", label = "simulated") # average utilisation rate
plt.axhline(0.3699, color = "orangered", label = "theoretic", ls = "--")
plt.title("Average utilisation: M/M/4")
plt.legend()
plt.show()
