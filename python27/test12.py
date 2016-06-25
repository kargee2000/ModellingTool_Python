# -*- coding: utf-8 -*-
"""
Created on Thu Sep 04 17:05:23 2014

@author: karthik.ganapathy
"""
import numpy as np
import pandas as pd
from pandas import DataFrame
from pandas import Series
df = DataFrame({'name':['karthik',np.NAN,'amrita','karthik','gana','santh','viji','ram','sudha'],'age':[32,32,2,20,45,56,78,82,35],'salary':[1500,1200,3200,3500,2000,1000,5000,500,560]})
#df['name'] = df['name'].fillna('miss')
#print df
#x = True
#print x
#print 25/7
k1 = [0,2]
#k1.append(1)
#k1.append(3)
df1 = df.iloc[:,k1]

#print df1
kd = df['age'].describe()

#print kd
#print kd[0]
#print np.percentile(df['age'],15)
#print type(pd.crosstab(df['name'],df['age']))

k =  pd.qcut(df['age'],3)
#print k
k2 = k.levels
#print type(k[1])
z = Series(k)
#print type(z)
df4 = df.columns[1:]
#print df4

