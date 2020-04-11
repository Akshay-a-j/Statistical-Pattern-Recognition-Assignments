#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 18:15:23 2020

@author: sa1
"""
#PART a)
import my_help_functions as mf
import numpy as np
K=2 #How many distributions
N_train=2000 #How many Samples
N_test=1000 #How many Samples
d=2 #How many dimensions
p=0.5
priors=[p,1-p] #Prior probability of selecting a distribution
means=[[300,6], [3,-2]]
means=np.squeeze(np.asarray(means)).T
covariance=[[[2,0],[0,2]],[[0.5,0],[0,2]]]
[y_train, x_train]=mf.Get_Sythetic(K,d,N_train, priors=priors,means=means,covariance=covariance)
[y_test, x_test]=mf.Get_Sythetic(K,d,N_test, priors=priors,means=means,covariance=covariance)
#%%PERCEPTRON
from sklearn.linear_model import Perceptron

clf = Perceptron(tol=1e-3) #Create perceptron Object
clf.fit(x_train, y_train) #Train it 
clf.score(x_test, y_test) #Test it
#%% PLOTS
mf.Plot_Figs(y_train,x_train,K,1,"TEST","x1","x2")
# Plot_SubPlots(cluster_label_hist,data,K,iterations,title_name,x_name,y_name)