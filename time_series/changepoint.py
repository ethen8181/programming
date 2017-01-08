
"""
@author: Claudio Bellei
"""

import numpy as np
import csv
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import bernoulli, norm, poisson
import sys

matplotlib.rc('font', size=20)
matplotlib.rc('font', family='Arial')

np.random.seed(100)

class cpt:
    def __init__(self,type="normal-mean"):
        self.type = type
        self.data = []
        #define size of two regions (changepoint occurring at the middle)
        size1 = 2500
        size2 = 2500
        if type=="normal-mean":
            scale = 50 #standard deviation of distribution function
            loc1 = 1000 #mean of normal for first part
            loc2 = 1020 #mean of normal for second part
            d1 = norm.rvs(loc=loc1,size=size1,scale=scale)
            d2 = norm.rvs(loc=loc2,size=size2,scale=scale)
            self.labels = {"xlabel":"Days","ylabel":"Visits"}
            self.data = np.concatenate((d1,d2),axis=0)
        elif type=="normal-var":
            scale1 = 10 #standard deviation of normal distribution function
            scale2 = 20 #standard deviation of normal distribution function
            loc = 1000 #mean of normal for first part
            #define random variates
            d1 = norm.rvs(loc=loc,size=size1,scale=scale1)
            d2 = norm.rvs(loc=loc,size=size2,scale=scale2)
            self.labels = {"xlabel":"Days","ylabel":"Visits"}
            self.data = np.concatenate((d1,d2),axis=0)
        elif type=="bernoulli-mean":
            p1 = 0.9 #probability of passing the test
            p2 = 0.85 #probability of passing the test
            #define random variates
            d1 = bernoulli.rvs(p1,size=size1)
            d2 = bernoulli.rvs(p2,size=size2)
            self.labels = {"xlabel":"Test number","ylabel":"Product fails test"}
            #probability of failing the test
            self.data = 1 - np.concatenate((d1,d2),axis=0)
        elif type=="poisson-mean":
            mu1 = 12 #expected event rate
            mu2 = 10 #expected event rate
            #define random variates
            d1 = poisson.rvs(mu=mu1,size=size1)
            d2 = poisson.rvs(mu=mu2,size=size2)
            self.labels = {"xlabel":"Minutes","ylabel":"Hits"}
            self.data = np.concatenate((d1,d2),axis=0)
        else:
            print("invalid choice of type")
            print("options are: normal-mean, normal-var,bernoulli-mean, poisson-mean")

    def plot_data(self,type="ts",p=None):
        fig = plt.figure(figsize=(10,6))
        n = len(self.data)
        if self.type=="bernoulli-mean":
            marker = 'o'
            linestyle = 'None'
        else:
            marker = ''
            linestyle = '-'
        plt.plot(np.arange(1,n+1),self.data,ls=linestyle,marker=marker)
        plt.xlabel(self.labels["xlabel"])
        plt.ylabel(self.labels["ylabel"])
        plt.ylim([0.9*np.min(self.data),1.1*np.max(self.data)])
        fig.set_tight_layout(True)
        if type=="cpt":
            tau = p[0]
            m1 = p[1]
            m2 = p[2]
            plt.plot([0,tau-1],[m1,m1],'r',lw=2)
            plt.plot([tau,n],[m2,m2],'r',lw=2)
            plt.plot([tau,tau],[0.9*np.min(self.data),1.1*np.max(self.data)],'r--',lw=2)
            filename = self.type + "-cpt.png"
            plt.savefig(filename,format="png")
        filename = self.type + ".png"
        plt.savefig(filename,format="png")
        plt.show()

    def plot_score(self):
        fig = plt.figure(figsize=(10,6))
        plt.plot(self.score)
        plt.xlabel(self.labels["xlabel"])
        plt.ylabel("Score")
        fig.set_tight_layout(True)
        filename = self.type + "-score.png"
        plt.ylim([0.,1.1*np.max(self.score)])
        plt.savefig(filename,format="png")
        plt.show()

    def find_changepoint(self):
        data = self.data
        n = len(data)
        tau = np.arange(1,n)
        lmbd = 2*np.log(n) #Bayesian Information Criterion
        eps = 1.e-8 #to avoid zeros in denominator
        if self.type=="normal-mean":
            mu0 = np.mean(data)
            s0 = np.sum((data-mu0)**2)
            s1 = np.asarray([np.sum((data[0:i]-np.mean(data[0:i]))**2) for i in range(1,n)])
            s2 = np.asarray([np.sum((data[i:]-np.mean(data[i:]))**2) for i in range(1,n)])
            R  = s0-s1-s2
            G  = np.max(R)
            taustar = int(np.where(R==G)[0]) + 1
            sd1 = np.std(data[0:taustar-1])
            sd2 = np.std(data[taustar-1:])
            #use pooled standard deviation
            var = ( taustar*sd1**2 + (n-taustar)*sd2**2 ) / n
            self.test_decision(2*G,var*lmbd,data,taustar)
        elif self.type=="normal-var":
            std0 = np.std(data)
            std1 = np.asarray([np.std(data[0:i]) for i in range(1,n)],dtype=float) + eps
            std2 = np.asarray([np.std(data[i:]) for i in range(1,n)],dtype=float) + eps
            R = n*np.log(std0) - tau*np.log(std1) - (n-tau)*np.log(std2)
            G  = np.max(R)
            taustar = int(np.where(R==G)[0]) + 1
            self.test_decision(2*G,lmbd,data,taustar)
        elif self.type=="bernoulli-mean":
            m0 = np.sum(data)
            p0 = np.mean(data)
            m1 = np.cumsum(data)[:-1]
            m2 = m0 - m1
            p1 = m1 / tau
            p2 = m2 / (n-tau+1)
            #take care of possible NaN
            p1 = p1 + eps
            p1[p1>1] = 1. - eps
            p2 = p2 + eps #to avoid zero
            p2[p2>1] = 1. - eps
            R  = m1*np.log(p1) + (tau-m1)*np.log(1-p1) + m2*np.log(p2) \
                + (n-tau-m2)*np.log(1-p2) - m0*np.log(p0) - (n-m0)*np.log(1-p0)
            G  = np.max(R)
            taustar = int(np.where(R==G)[0]) + 1
            self.test_decision(2*G,lmbd,data,taustar)
        elif self.type=="poisson-mean":
            lambda0 = np.mean(data)
            lambda1 = np.asarray([np.mean(data[0:i]) for i in range(1,n)],dtype=float) + eps
            lambda2 = np.asarray([np.mean(data[i:]) for i in range(1,n)],dtype=float) + eps
            m0 = np.sum(data)
            m1 = np.cumsum(data)[:-1]
            m2 = m0 - m1
            R  = m1*np.log(lambda1) + m2*np.log(lambda2) - m0*np.log(lambda0)
            G  = np.max(R)
            taustar = int(np.where(R==G)[0]) + 1
            self.test_decision(2*G,lmbd,data,taustar)
        self.score = R
    def test_decision(self,teststat,criterion,data,tau):
        print("---------------------")
        print("2G = %e"%(teststat))
        print("sigma**2*lambda = %e"%(criterion))
        if teststat > criterion:
            print("-->H0 rejected")
            print("Changepoint detected at position: %d"%tau)
            m1 = np.mean(data[0:tau])
            std1 = np.std(data[0:tau])
            m2 = np.mean(data[tau:])
            std2 = np.std(data[tau:])
            if "mean" in self.type:
                print("m1 = %f"%m1)
                print("m2 = %f"%m2)
            else:
                print("std1 = %f"%std1)
                print("std2 = %f"%std2)
            self.plot_data(type="cpt",p=[tau,m1,m2])
        else:
            print("-->H0 not rejected")
        print("---------------------")
