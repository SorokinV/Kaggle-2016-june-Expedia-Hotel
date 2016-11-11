import numpy  as np
import pandas as pd
import matplotlib.pyplot as plt

xx = pd.DataFrame([[0,0,0],[1,2,3]],columns=['a1','a2','xx'])
print(xx)
print(type(xx))
print(type(xx['a1']))
print(type(xx.columns),xx.columns)

yd = {'A':pd.Series([1,2,1,2,1,2,1,2,1,2])}
yy = pd.DataFrame(yd)
yy['B']=[1,2,3,2,1,2,3,2,1,2]
yy['C']=[1,1,1,1,1,1,1,1,1,1]
yy['D']=[1,1,1,1,1,1,1,1,1,1]
print(yy)

gr = yy.groupby(['A','B']); print(type(gr))

print('before\n')
for name,group in gr : print('name=',name,'\n',group)

def f(x) :
    dx0 = np.zeros((1,100))
    return(pd.DataFrame(dx0,columns=['v'+str(i) for i in range(dx0.shape[1])]))

zz = gr['D','C'].apply(f)
print('after apply\n',zz)
zz = zz.reset_index()
print()
print('\nafter reset\n',zz)

dx5 = pd.Series(np.random.randn(10)).nlargest(5,keep='first'); print(dx5)

del zz['level_2']
print('\nafter del\n',zz)

ind = ['v'+str(i) for i in range(5)]; print(ind)


zz.columns = ['A1','B1']+['A1B1x'+str(i) for i in range(100)]
print(zz)

zz.plot(); plt.show();

#------------------------------------------------------------------------

dcol = ['count'] + ['n'+str(i) for i in range(5)] + ['x'+str(i) for i in range(100)]
def f (xgroup) :
    d00  = np.zeros((100));d00[xgroup['hotel_cluster']]+=xgroup['count']
    dsum = xgroup['count'].sum()
    d05  = pd.Series(d00); d05=d05[d05>0].nlargest(5).index.tolist()+[-1]*5; d05=d05[0:5];
    ddd  = [dsum] + d05 + d00.tolist()
    return(pd.DataFrame(ddd,index=dcol).T)

trans = grouped4.apply(f)
len(trans)

#------------------------------------------------------------------------
