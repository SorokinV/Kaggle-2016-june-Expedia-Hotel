# coding: utf-8

# In[63]:

#from azureml import Workspace

import datetime
import os

import numpy  as np
import pandas as pd
import matplotlib.pyplot as plt

'''
ws = Workspace()
ws


# In[64]:

experiment = ws.experiments['98f3d81e0f3e44318315e91dbe6a8b97.f-id.919377ae893b4ef99bd07f7701df8680']
ds = experiment.get_intermediate_dataset(
    node_id='f35c5a8b-2b91-410f-a278-e36f8594bf69-76673',
    port_name='Results dataset',
    data_type_id='GenericCSV'
)
frame = ds.to_dataframe()
print(frame.shape)
'''

# In[65]:

pickleDir = '../Data/Pickle'

print('1 :',datetime.datetime.now())

frame = pd.read_csv('../Data/Fields/D11.csv')

print('2 :',datetime.datetime.now())

print(frame.tail())

print('3 :',datetime.datetime.now())

#grouped=frame.groupby(['user_id','is_booking','dt0m']); print('user+book+dt0m =',len(grouped))
grouped=frame.groupby(['user_id','is_booking']); print('user+book =',len(grouped))
#grouped=frame.groupby(['user_id']); print('user =',len(grouped))

grouped.to_pickle(os.path.join(pickleDir,'grouped.pck'))

print('4 :',datetime.datetime.now())

i = -1
n =  5
dcol = ['count','countCnt'] + ['n'+str(i) for i in range(5)] + ['cc'+str(i) for i in range(100)]
dcol = ['count','countCnt'] + ['n'+str(i) for i in range(n)] # + ['cc'+str(i) for i in range(100)]
def f (xgroup) :
    global i,n
    d00  = np.zeros((100));d00[xgroup['hotel_cluster']]+=xgroup['count']
    dsum = xgroup['countCnt'].sum()
    dcnt = xgroup['count'].sum()
    d05  = pd.Series(d00); d05=d05[d05>0].nlargest(n).index.tolist()+[-1]*n; d05=d05[0:n];
    ddd  = [dcnt,dsum] + d05 # + d00.tolist()
    i   += 1
    if (i%10000==0) : print('5 :',datetime.datetime.now()," i = ",i)

    
    return(pd.DataFrame(ddd,index=dcol).T)

trans = grouped.apply(f)

trans.to_pickle(os.path.join(pickleDir,'trans.pck'))

print('6 :',datetime.datetime.now())

print(len(trans),trans.shape)
trans.head(6)


a=a

# In[ ]:

print(len(trans),trans.shape)
trans.head(6)


# In[ ]:

trans0 = transx.query('is_booking==0')[['user_id','is_booking','count','countCnt']+['n'+str(i) for i in range(5)]]
trans0.index = trans0['hotel_country']
trans0.head()

trans0.to_pickle(os.path.join(pickleDir,'trans0.pck'))


# In[ ]:

trans1 = transx.query('is_booking==1')[['hotel_country','is_booking','count','countCnt']+['n'+str(i) for i in range(5)]]
trans1.index = trans1['hotel_country']
trans1.head()

trans1.to_pickle(os.path.join(pickleDir,'trans1.pck'))


# In[ ]:

trans01 = pd.concat([trans0,trans1],axis=1)

trans01.to_pickle(os.path.join(pickleDir,'trans01.pck'))

trans01.columns = ['user_id','bo0','count0','countCnt0']+['b0n'+str(i) for i in range(5)]+                 ['h1','bo1','count1','countCnt1']+['b1n'+str(i) for i in range(5)]
trans01 = trans01[['user_id','count0','countCnt0','count1','countCnt1']+['b0n'+str(i) for i in range(5)]+['b1n'+str(i) for i in range(5)]]
print('max,min =',trans01.countCnt0.max(),trans01.countCnt1.max(),trans01.countCnt0.min(),trans01.countCnt1.min())
print('5max,5min =',trans01.count0.nlargest(5),trans01.countCnt1.nlargest(5))
trans01.head()

a=a

# In[ ]:

import matplotlib
matplotlib.style.use('ggplot')
#pd.notnull(trans01).plot().scatter(x='count0',y='count1')
#trans01[pd.notnull(trans01['count1']) and pd.notnull(trans01['count0'])].plot().scatter(x='count0',y='count1')
trans01[trans01.countCnt0<40000].plot(kind='scatter',x='count0',y='count1')


# In[ ]:

print(trans01[pd.isnull(trans01.count1)].shape)
trans01[pd.isnull(trans01.count1)]


# In[ ]:

