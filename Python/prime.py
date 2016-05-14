import datetime
out1=[5,7,3,4,8,5]
out2=[8,9,4,2]

outx = out1 + [x for x in out2 if x not in out1]
print(outx)
print(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
