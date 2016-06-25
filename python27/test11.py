import pandas as pd
import numpy as np
from pandas import DataFrame
import scipy
my_series = pd.Series([1,2,2,3,3,3, "fred", 1.8, 1.8])
k1 = my_series.value_counts()
k2 = DataFrame(k1)
#print k2.to_html()
#.value_counts()
#df = pd.DataFrame({'a' : [1, 2, 3, 4, 5], 'b' : ['yes', 'no', 'yes', 'no', 'absent']})
#df['b'] = pd.Categorical.from_array(df.b).labels
#print df['b']
df = pd.read_csv("E:/Default_On_Payment_CHAID.csv")
fit = pd.crosstab(df.Status_Checking_Acc,df.Default_On_Payment)
#print type(fit)
#scipy.stats.chi2_contingency(fit)
#chi2_contingency(data)
s =  scipy.stats.chi2_contingency(fit)
scipy.stats.chi2_contingency
#if(s[1]<0.05):
#print s[1]
chi_key= list()
#chi_key.append()
var = "upl1"
if(not(var=='upl')):
    print "hi"