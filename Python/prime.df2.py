import numpy  as np
import pandas as pd
import matplotlib.pyplot as plt

xx = pd.DataFrame([[0,0,0],[1,2,3]],columns=['a1','a2','xx'])
print(xx)
print(type(xx))
print(type(xx['a1']))
print(type(xx.columns),xx.columns)

yd = {'A':pd.Series([i for i in range(10,0,-1)])}
yy = pd.DataFrame(yd)
yy['B']=[i for i in range(10)]
yy['C']=[1,1,1,1,1,1,1,1,1,1]
yy['D']=[1,1,1,1,1,1,1,1,1,1]
print(yy)

tmp = ['B','A']

print(yy[tmp])
print(yy[['A','C']])

za=yy[['A','C']]; za.index=yy['A']; print(za)
zb=yy[['B','C']]; zb.index=yy['B']; print(zb)

zab=pd.concat([za,zb],axis=1); print('\n'+"-"*10,'\n',zab)


