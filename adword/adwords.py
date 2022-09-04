#!/usr/bin/env python
# coding: utf-8

# In[15]:


import sys
import pandas as pd
import random
import numpy as np


# In[16]:


def greedy(dataset, queries, bdict):
    qdict = {}
    for q in queries.values:
        if q[0] not in qdict.keys():
            qdict[q[0]] = dataset.loc[(dataset.Keyword == q[0])].sort_values(by = 'Bid Value', ascending = False).values
            
    calc_rev = 0
    revenue = 0
    new_budget = bdict.copy()
    queries_new = queries[0].values
    for q in queries_new:
        for b in qdict[q]:
            if new_budget[b[0]] - b[2] >= 0:
                new_budget[b[0]] -= b[2]
                revenue += b[2]
                break
    calc_rev += revenue
    return calc_rev


# In[17]:


def msvv(dataset, queries, bdict):
    qdict = {}
    for q in queries[0].values:
        if q not in qdict.keys():
            qdict[q] = dataset.loc[(dataset.Keyword == q)].values

    calc_rev = 0
    spentbdict = dict.fromkeys(bdict, 0)
    revenue = 0	
    queries_new = queries[0].values
    for q in queries_new:
        m_bid, m_adv = 0, 0
        msvv = 0
        for b in qdict[q]:
            cmsvv = (b[2] * (1 - np.exp((spentbdict[b[0]] / bdict[b[0]]) - 1)))
            if (msvv < cmsvv) and ((spentbdict[b[0]] + b[2]) <= bdict[b[0]]):
                msvv = cmsvv
                mbid = b[2]
                madv = b[0]
        spentbdict[madv] += mbid
        revenue += mbid
    calc_rev += revenue
    return calc_rev


# In[18]:


def balance(bidder_dataset, queries, budget_dict):
    qdict = {}
    for q in queries[0].values:
        if q not in qdict.keys():
            qdict[q] = dataset.loc[(dataset.Keyword == q)].values

    calc_rev = 0
    revenue = 0
    new_budget = bdict.copy()
    queries_new = queries[0].values
    for q in queries_new:
        m, mbid, madv = 0, 0, 0
        for b in qdict[q]:
            if m < new_budget[b[0]] and new_budget[b[0]] >= b[2]:
                m = new_budget[b[0]]
                mbid = b[2]
                madv = b[0]
        new_budget[madv] -= mbid
        revenue += mbid
    calc_rev += revenue	
    return calc_rev


# In[19]:


dataset = pd.read_csv('bidder_dataset.csv')
queries = pd.read_csv('queries.txt', header = None)
algo = sys.argv[1]


# In[24]:

budget =  dataset.loc[(dataset.Budget > 0)]
bdict = budget.set_index('Advertiser')['Budget'].to_dict()
random.seed(0)


# In[ ]:


avg_rev = 0
if (algo == "greedy"):
    calc_rev = greedy(dataset, queries, bdict)
    for i in range(100):
        queries_new = queries.sample(frac=1)
        calc_rev1 = greedy(dataset, queries_new, bdict)
        avg_rev += calc_rev1
    avg_rev = avg_rev/100
elif (algo == "msvv"):
    calc_rev = msvv(dataset, queries, bdict)
    for i in range(100):
        queries_new = queries.sample(frac=1)
        calc_rev1 = msvv(dataset, queries_new, bdict)
        avg_rev += calc_rev1
    avg_rev = avg_rev/100
elif (algo == "balance"):
    calc_rev = balance(dataset, queries, bdict)
    for i in range(100):
        queries_new = queries.sample(frac=1)
        calc_rev1 = balance(dataset, queries_new, bdict)
        avg_rev += calc_rev1
    avg_rev = avg_rev/100
    
print (round(calc_rev,2))
print (round(avg_rev/sum(bdict.values()),2))



