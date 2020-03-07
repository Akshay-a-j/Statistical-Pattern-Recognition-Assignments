#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 12:09:54 2020

@author: sawan
"""

#%% MODULE IMPORT
import os
from glob import glob
from pandas import read_csv
import numpy as np
from scipy.stats import multivariate_normal

class GMM(object):
    def __init__(self,K,mu,cov,prop):
        self.K=K
        self.mu=mu
        self.cov=cov
        self.prop=prop
        self.responsibility=[]
        self.tes=[]
        
    @property
    def theta(self):
        return [self.mu, self.cov, self.prop]
#%% OLD FAITHFUL DATASET
def Get_Old_Faithful():
    path_to_data=os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'Data'))
    csv_data=glob(os.path.join(path_to_data, "*.csv"))
    iter=0
    data=[]
    for files in csv_data:
        temp = read_csv(csv_data[iter])
        temp=temp.values
        data.append(temp)
        iter=iter+10
    # converting it into a float array
    data=np.squeeze(np.asarray(data))
 
    #% Normalizing
    data_mean=np.mean(data,axis=0)
    data_std=np.std(data,axis=0)
    data=data-data_mean
    data=data/data_std
    #Creating a data label column to say which cluster a point lies in
    data[:,0]=0  
    return data    
#%% SYNTHETIC DATASET
def Get_Sythetic(K,d,N,**kwargs):   
    means=kwargs.get('means',np.random.randint(-100,100,size=[d,K]))
    covariance=kwargs.get('cov', get_random_cov(K,d))
    # covariance=kwargs.get('cov', np.dstack([np.eye(d)]*K))
    data=np.zeros((N,d+1))
    
    for n in range(N):
        k=np.random.randint(0,K)
        data[:,0]=k
        data[n,1:]=np.random.multivariate_normal(means[:,k],covariance[:,:,k],size=1)
            
    #%% Normalizing
    data_mean=np.mean(data[:,1:],axis=0)
    data_std=np.std(data[:,1:],axis=0)
    data[:,1:]=data[:,1:]-data_mean
    data[:,1:]=data[:,1:]/data_std    
    return data
#%% Random covariance matricies            
def get_random_cov(K,d):
    from sklearn import datasets
    cov=[]
    for i in range(K):
        temp=np.dstack([datasets.make_spd_matrix(d)*8])
        cov.append(temp)
    return np.dstack(cov)
#%% MNIST
"""Seema's Code 
req_class= list of numbers to be input
eg [1,2,3]
Function returns a matrix with the first column as all 0's and all rows containing
the binarized numbers  requested
"""
def get_mnist_data(req_class):
    
    #%
    #from mnist import MNIST
    import numpy as np
    from sklearn.utils import shuffle   
    
    #%
    from keras.datasets import mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    img_rows, img_cols = 28, 28
    
    #%
    # req_class=[2, 3]
    train_com = []
    train_lab = []
        #%   
    for i in req_class:
        print(i)
        cl1 = i
        i, = np.where(y_train == cl1)
        cl1_train = x_train[i,:,:]        # pull out the data corresponds to class1
        cl1_label = y_train[i]            # pull out the data labels corresponds to class1        
        
        cl1_train = cl1_train.astype('float32')
        cl1_train /= 255
        cl1_train=cl1_train.reshape(cl1_label.shape[0],img_rows*img_cols)  # flattern the input data   
        cl1_train[cl1_train>=0.5] = 1
        cl1_train[cl1_train<0.5] = 0
        
        train_com.append(cl1_train) # Merge the data
        train_lab.append(cl1_label)   # Merge the labels 
        
        
    #%
    train_df_lab = np.concatenate(train_lab, axis = 0)
    train_df_data = np.concatenate(train_com, axis = 0)
    train_df_data = np.concatenate([np.zeros((train_df_lab.shape[0], 1), dtype=int), train_df_data], axis = 1)
    [train_sff,train_labs] = shuffle(train_df_data, train_df_lab)     # Shuffle the data and label (to properly train the network)
    
    return(train_sff)
#%% E-Step
def E_Step(data,K,theta):
    means=theta[0]
    Covariance=theta[1]
    proportions=theta[2]
    #Computing responsibility coefficients of each point for each cluster.
    responsibility=np.zeros((len(data),K))
    for i in range(K):
        itr=0    
        for x in data[:,1:]:
            normalising=0
            N_xn=multivariate_normal.pdf(x,mean=means[:,i], cov=Covariance[:,:,i])
            responsibility[itr][i]=proportions[i]*N_xn
            for j in range(K):
                normalising+=proportions[j]*multivariate_normal.pdf(x,mean=means[:,j], cov=Covariance[:,:,j])
            responsibility[itr][i]=responsibility[itr][i]/normalising
            itr+=1      
    return responsibility
#%% M-STEP
def M_Step(data,responsibility):
    [N,K]=np.shape(responsibility) #N is number of data points
    [_,d]=np.shape(data[:,1:]) #Data dimension
    
    #Compute Proportions
    Nk=np.sum(responsibility,axis=0)
    proportions=Nk/N
        
    #Compute Means
    means=np.zeros((K,d))        
    for k in range(K):
        temp1=data[:,1:]
        temp2=responsibility[:,k]
        temp=temp1*temp2[:,None] #multiplying a vector with multiple columns
        means[k]=(1/Nk[k])*np.sum(temp,axis=0)  
    means=np.transpose(means)
        
    #Compute Covariance
    Covariance=np.zeros((d,d,K))        
    for k in range(K):
        for n in range(N):
            temp1=data[n,1:]-means[:,k]
            temp2=np.outer(temp1,np.transpose(temp1))
            temp=responsibility[n,k]*temp2
            Covariance[:,:,k]+=temp
        Covariance[:,:,k]=(1/Nk[k])*Covariance[:,:,k]
    
    theta=[means,Covariance,proportions]
    Likelihood=0
    log_likelihood=0
    for n in range(N):
        for k in range(K):
            Likelihood+=proportions[k]*multivariate_normal.pdf(data[n,1:],mean=means[:,k], cov=Covariance[:,:,k])
        log_likelihood+=np.log(Likelihood)
            
    return theta, log_likelihood

#%% PLOTS

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
def Plot_Figs(theta_history,cluster_label_hist,data,K,iterations,title_name,x_name,y_name):
    # plt.figure(num=None, figsize=(18, 12), dpi=100, facecolor='w', edgecolor='k')    
    # plt.plot(range(1,iterations+1),liklihood_history)   
    itr=0
    # step_size=int(np.ceil(iterations/20))
    step_size=1

    fig, axs = plt.subplots(6,3, figsize=(20, 20), facecolor='w', edgecolor='k',sharex=True,sharey=True)
    fig.subplots_adjust(hspace = .5, wspace=.001)
    axs = axs.ravel()
    ptr=0
    for i in range(0,iterations,step_size):
        # plt.figure(num=itr, figsize=(18, 12), dpi=100, facecolor='w', edgecolor='k')  
        # plt.subplots(6, 3, sharey=True,sharex=True)
        itr+=0
        x=[]
        y=[]
        for k in range(K):
            mean1=theta_history[i+1][0][:,k][0]
            mean2=theta_history[i+1][0][:,k][1]
            plot_data=data[cluster_label_hist[i]==k,1:]
            x=plot_data[:,0]
            y=plot_data[:,1]
            colormap = plt.cm.get_cmap("Set1")                       
        
            if i<=17 or i>=iterations-2:
                axs[ptr].scatter(x,y,color=colormap(k),s=5)
                axs[ptr].scatter(mean1,mean2,color=colormap(k),marker="x",s=50)     
                draw_ellipse((mean1,mean2),theta_history[i+1][1][:,:,k],alpha=0.2, color=colormap(k),ax=axs[ptr])
                axs[ptr].set_title("Iteration "+str(i))  
                                  
                final_title_name=title_name

                flag_plot=1
         
        if i<iterations-step_size and flag_plot==1 and i<17:
            flag_plot=0
            ptr+=1
            # plt.show()
    fig.text(0.5, 0.9, final_title_name, ha='center',fontsize=21)
    fig.text(0.5, 0.1, x_name, ha='center',fontsize=21)
    fig.text(0.10, 0.5, y_name, va='center', rotation='vertical',fontsize=21)
    # fig.xlabel(x_name,fontsize=21)
    # fig.ylabel(y_name,fontsize=21)
    # plt.suptitle(final_title_name,fontsize=21)            
    print("Done")
    
def Plot_SubPlots(theta_history,cluster_label_hist,data,K,iterations,title_name,x_name,y_name):
    itr=0
    step_size=1
    fig, axs = plt.subplots(6,3, figsize=(20, 20), facecolor='w', edgecolor='k',sharex=True,sharey=True)
    fig.subplots_adjust(hspace = .5, wspace=.001)
    axs = axs.ravel()
    ptr=0
    for i in range(0,iterations,step_size):
        itr+=0
        x=[]
        y=[]
        for k in range(K):
            mean1=theta_history[i+1][0][:,k][0]
            mean2=theta_history[i+1][0][:,k][1]
            plot_data=data[cluster_label_hist[i]==k,1:]
            x=plot_data[:,0]
            y=plot_data[:,1]
            colormap = plt.cm.get_cmap("Set1")                       
        
            if i<=17 or i>=iterations-2:
                axs[ptr].scatter(x,y,color=colormap(k),s=5)
                axs[ptr].scatter(mean1,mean2,color=colormap(k),marker="x",s=20)     
                draw_ellipse((mean1,mean2),theta_history[i+1][1][:,:,k],alpha=0.2, color=colormap(k),ax=axs[ptr])
                axs[ptr].set_title("Iteration "+str(i))  
                                  
                final_title_name=title_name

                flag_plot=1
         
        if i<iterations-step_size and flag_plot==1 and i<17:
            flag_plot=0
            ptr+=1
            # plt.show()
    fig.text(0.5, 0.9, final_title_name, ha='center',fontsize=21)
    fig.text(0.5, 0.1, x_name, ha='center',fontsize=21)
    fig.text(0.10, 0.5, y_name, va='center', rotation='vertical',fontsize=21)         
    print("Done")   


#%% TO DRAW ELLIPSE
def draw_ellipse(position, covariance, ax=None, **kwargs):
# taken from
# https://github.com/DFoly/Gaussian-Mixture-Modelling/blob/master/gaussian-mixture-model.ipynb
    """Draw an ellipse with a given position and covariance"""
    ax = ax or plt.gca()
    
    # Convert covariance to principal axes
    if covariance.shape == (2, 2):
        U, s, Vt = np.linalg.svd(covariance)
        angle = np.degrees(np.arctan2(U[1, 0], U[0, 0]))
        width, height = 2 * np.sqrt(s)
    else:
        angle = 0
        width, height = 2 * np.sqrt(covariance)
    
    # Draw the Ellipse
    for nsig in range(1, 4):
        ax.add_patch(Ellipse(position, nsig * width, nsig * height,
                             angle, **kwargs))
        