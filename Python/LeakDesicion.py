#
#  idea from kaggle forum 2016-05-15
#
#

import os.path
import datetime
from heapq import nlargest

import sys
import csv

#----------------------------------------------------------------
#
#  
#
#
#  leak decision with 3 steps:
#
#  1. select all keys from test file with initialization dictionary
#  2. filling dictionary stats on keys/values from train file
#  3. build decision from test file and filling dictionary
#
#
        
def LeakDecision (trainFile,testFile,
                  out1,out2,
                  debug=False,debugStop=3000000,
                  printOK=False) :

    #------------------------------------------------------------
    # First step on test data. Select and save keys in dictionary
    #
    #
    
    numID       = 0
    numDateTime = 1

    numULC      =  6  # user_location_city
    numODD      =  7  # orig_destination_distance
    
    numSDI      = 17  # srch_destination_id
    numHCountry = 20  # hotel_country 
    numHMarket  = 21  # hotel_market
    

    d1 = dict()
    d2 = dict()
    d3 = dict()
    d4 = dict()

    with open(testFile, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader :
            if reader.line_num==1:
                continue
                    
            id        = row[numID]  
            ULC       = row[numULC]
            ODD       = row[numODD]
            SDI       = row[numSDI]
            HMarket   = row[numHMarket]
            HCountry  = row[numHCountry]

            if ((ULC!="") and (ODD!="")) :
                 key = hash("-".join(["1",ULC,"2",ODD]))
                 d1[key] = [0]*100

            if ((SDI!="") and (HCountry!="") and (HMarket!="")) :
                 #key = (SDI,HCountry,HMarket)
                 key = hash("-".join(["1",SDI,"2",HCountry,"3",HMarket]))
                 d2[key] = [0]*100

            if ((SDI!="")) :
                 key = (SDI)
                 d3[key] = [0]*100

            if ((HCountry!="")) :
                 key = (HCountry)
                 d4[key] = [0]*100
                 
            if (reader.line_num%100000==0) :
                print("look-test :",reader.line_num," d1-4 (size-count): ",
                      sys.getsizeof(d1),"-",len(d1),
                      sys.getsizeof(d2),"-",len(d2),
                      sys.getsizeof(d3),"-",len(d3),
                      sys.getsizeof(d4),"-",len(d4))

            
    #------------------------------------------------------------
    #
    # Second step: go through train file and stats fill keys value
    #

    numDateTime = 0   # event date time
    numBook     = 18  # event booking

    numULC      =  5  # user_location_city
    numODD      =  6  # orig_destination_distance
    numSDI      = 16  # srch_destination_id
    numHCountry = 21  # hotel_country 
    numHMarket  = 22  # hotel_market
    numHCluster = 23  # hotel_cluster

    topCluster = [0]*100;
        
    with open(trainFile, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i1, i2, i3, i4, ie = 0,0,0,0,0; le =[]
        for row in reader :
            if reader.line_num==1: continue

            dateTime  = row[numDateTime]
            isBooking = int(row[numBook])
            ULC       = row[numULC]
            ODD       = row[numODD]
            SDI       = row[numSDI]
            HMarket   = row[numHMarket]
            HCountry  = row[numHCountry]
            HCluster  = int(row[numHCluster])

            app1      = 3+17*isBooking
            app2      = 1+ 5*isBooking

            try :
                dateTime = datetime.datetime.strptime(dateTime,"%Y-%m-%d %H:%M:%S")
            except :
                dateTime = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                     
            if ((ULC!="") and (ODD!="")) :
                 #key = (ULC,ODD)
                 key = hash("-".join(["1",ULC,"2",ODD]))
                 if key in d1 :
                     cluster = d1.get(key,[0]*100)
                     cluster[HCluster] += 1
                     d1[key]=cluster; i1 +=1;

            if ((SDI!="") and (HCountry!="") and (HMarket!="") and (dateTime.year==2014)) :
                 #key = (SDI,HCountry,HMarket)
                 key = hash("-".join(["1",SDI,"2",HCountry,"3",HMarket]))
                 if key in d2 :
                     cluster = d2.get(key,[0]*100)
                     cluster[HCluster] += app1
                     d2[key]=cluster; i2 +=1

            if ((SDI!="")) :
                 key = (SDI)
                 if key in d3 :
                     cluster = d3.get(key,[0]*100)
                     cluster[HCluster] += app1
                     d3[key]=cluster; i3 +=1

            if ((HCountry!="")) :
                 key = (HCountry)
                 if key in d4 :
                     cluster = d4.get(key,[0]*100)
                     cluster[HCluster] += app2
                     d4[key]=cluster; i4 +=1

            topCluster[HCluster] += 1

            if (debug and (reader.line_num>debugStop)) : break
            if (reader.line_num%100000==0) :
                print("train :",reader.line_num,"  ",
                      datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                #print("train :",reader.line_num," d1-4 (size-count): ",
                #      sys.getsizeof(d1),"-",len(d1),
                #      sys.getsizeof(d2),"-",len(d2),
                #      sys.getsizeof(d3),"-",len(d3),
                #      sys.getsizeof(d4),"-",len(d4))
                
            
        csvfile.close();

    if printOK :        
        print(len(d1),len(d2),len(d3),len(d4))
        print("dictionary 1",list(d1.keys())[0:1])
        print(list(d1.values())[0:1])
        print("dictionary 2",list(d2.keys())[0:1])
        print(list(d2.values())[0:1])
        print("dictionary 3",list(d3.keys())[0:1])
        print(list(d3.values())[0:1])
        print("dictionary 4",list(d4.keys())[0:1])
        print(list(d4.values())[0:1])
        print("topCluster:\n",topCluster)

        print("(0-4)=",i1,i2,i3,i4)

    #------------------------------------------------------------------
    #
    # Second and half step: transform and clearing working dictionaries
    #
    #   transform values from 100 array[100] to 5-point list
    #

    for key in d1.keys() :
        v = nlargest(5,enumerate(d1[key]),key=lambda x:x[1])
        l = [str(x[0]) for x in v]
        for k5 in range(0,len(v)) :
             if (v[k5][1]==0) : l = l[:k5]; break;
        d1[key] = l

    for key in d2.keys() :
        v = nlargest(5,enumerate(d2[key]),key=lambda x:x[1])
        l = [str(x[0]) for x in v]
        for k5 in range(0,len(v)) :
             if (v[k5][1]==0) : l = l[:k5]; break;
        d2[key] = l

    for key in d3.keys() :
        v = nlargest(5,enumerate(d3[key]),key=lambda x:x[1])
        l = [str(x[0]) for x in v]
        for k5 in range(0,len(v)) :
             if (v[k5][1]==0) : l = l[:k5]; break;
        d3[key] = l
        

    for key in d4.keys() :
        v = nlargest(5,enumerate(d4[key]),key=lambda x:x[1])
        l = [str(x[0]) for x in v]
        for k5 in range(0,len(v)) :
             if (v[k5][1]==0) : l = l[:k5]; break;
        d4[key] = l

    if printOK :
        print("dictionary 1",list(d1.keys())[0:4])
        print(list(d1.values())[0:4])
        print("dictionary 2",list(d2.keys())[0:4])
        print(list(d2.values())[0:4])
        print("dictionary 3",list(d3.keys())[0:4])
        print(list(d3.values())[0:4])
        print("dictionary 4",list(d4.keys())[0:4])
        print(list(d4.values())[0:4])
    
    #-------------------------------------------------------------------------
    #
    # Third step: build finally decision from test file and working dictionaries
    #
    #

    numULC      =  6  # user_location_city
    numODD      =  7  # orig_destination_distance
    
    numSDI      = 17  # srch_destination_id
    numHCountry = 20  # hotel_country 
    numHMarket  = 21  # hotel_market
    
    numDateTime = 1
    numID       = 0 

    top5x0      = [ str(x[0]) for x in nlargest(5,enumerate(topCluster),key=lambda x:x[1])]
    if printOK : print("top5x0",top5x0)
    
        
    with open(testFile, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i1, i2, i3, i4, ie = 0,0,0,0,0; le =[]
        out1f  = open(out1,"w")
        out2f  = open(out2,"w")
        for row in reader :
            if reader.line_num==1:
                print("id,hotel_cluster",file=out1f);
                print("id,hotel_cluster,mark",file=out2f);
                continue
                    
            try :
                dateTime = datetime.datetime.strptime(row[self.numDateTime],"%Y-%m-%d %H:%M:%S")
            except :
                dateTime = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)

            id        = row[numID]  
            ULC       = row[numULC]
            ODD       = row[numODD]
            SDI       = row[numSDI]
            HMarket   = row[numHMarket]
            HCountry  = row[numHCountry]

            out       = []
            mark      = 0
            outs      = set()
            
            
            if ((ULC!="") and (ODD!="")) :
                 #key = (ULC,ODD)
                 key = hash("-".join(["1",ULC,"2",ODD]))
                 if key in d1 :
                     if (len(d1[key])>0) : mark = 1;  out = d1.get(key)
                     
            if ((SDI!="") and (HCountry!="") and (HMarket!="")) :
                 #key = (SDI,HCountry,HMarket)
                 key = hash("-".join(["1",SDI,"2",HCountry,"3",HMarket]))
                 if key in d2 :
                     if (len(d2[key])>0) :
                         mark += 2;
                         out = out + [x for x in d2.get(key) if x not in out]

            if ((SDI!="")) :
                 key = (SDI)
                 if key in d3 :
                     if (len(d3[key])>0) :
                         mark += 4;
                         out = out + [x for x in d3.get(key) if x not in out]

            if ((HCountry!="")) :
                 key = (HCountry)
                 if key in d4 :
                     if (len(d4[key])>0) :
                         mark += 8;
                         out = out + [x for x in d4.get(key) if x not in out]
                 
            if (len(out)<5) :
                mark += 16;
                out  = out+[x for x in top5x0 if x not in out]
            out = out[:5]
            
            out = (" ".join(out)).strip()
            print(str(id)+',"'+out+'"',file=out1f);
            print(str(id)+',"'+out+'",'+str(mark),file=out2f);
            
            if (debug and reader.line_num>30000) : break;
            if (reader.line_num%100000==0) :
                print("test :",reader.line_num)


        csvfile.close()
        out1f.close()
        out2f.close()

    #------------------------------------------------------------
    #
    # The End
    #

    return
        

if __name__ == "__main__" :

    dateBegin = datetime.datetime.now()

    step   = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

    fTrain = '../Data/train.csv';  # train file
    fTest  = '../Data/test.csv';   # test  file
    fOut1  = '../Result/Leak/df-Leak-'   +step+'.csv';  # decision
    fOut2  = '../Result/Leak/df-LeakExt-'+step+'.csv';  # decision with case marks

    LeakDecision(fTrain,fTest,fOut1,fOut2,
                 debug=False,debugStop=2000000)

    dateEnd = datetime.datetime.now()

    print("begin :",dateBegin.strftime("%Y-%m-%d %H:%M:%S"))
    print("end   :",dateEnd.strftime("%Y-%m-%d %H:%M:%S"))


