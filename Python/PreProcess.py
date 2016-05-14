
import math
import os.path
import datetime
from heapq import nlargest

import sys
import gc

import csv
import pickle
import json


class  BigCSVFile :
    
    names = [];

    def __init__ (self,input) :
        self.readHeader(input);
    def readHeader ( self,input ) :
        with open(input, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader :
                 if reader.line_num>1: break; # get only header
                 self.names = row
            csvfile.close();
            return
    def getName ( self,n ) : return(self.names[n]);
    def name    ( self,n ) : return(self.getName(n));
    def getNames( self   ) : return(self.names);
    def count   ( self   ) : return(len(self.names))
        
class PreTrain (BigCSVFile) :

    debug     = False

    inputFile = ""
    outBook0  = "../Data/trainBook0.csv"
    outBook1  = "../Data/trainBook1.csv"

    outD1     = "../Data/DataLeak/leak1.csv"
    
    numBook     = 18
    numDateTime = 0
    numDateBeg  = 11
    numDateEnd  = 12

    # for leak data
    numULC      =  5  # user_location_city
    numODD      =  6  # orig_destination_distance
    numSDI      = 16  # srch_destination_id
    numHCluster = 23  # hotel_cluster
    numHCountry = 21  # hotel_country 
    numHMarket  = 22  # hotel_market
    
    def __init__ (self,input) :
        self.inputFile = input;
        self.readHeader(input)
    def readSplitIsBooking(self) :
        with open(self.inputFile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i0, i1, ie = 0,0,0; le =[]
            for row in reader :
                 if reader.line_num==1:
                     wrt0 = open(self.outBook0,"w")
                     wrt1 = open(self.outBook1,"w")
                     out0 = csv.writer(wrt0,delimiter=',', quotechar='|')
                     out1 = csv.writer(wrt1,delimiter=',', quotechar='|')
                     h01  = ["dty",'dtm','dtd','dtw','dth','dtm']+row[1:self.numDateBeg]+ \
                            ["dt0y",'dt0m','dt0d','dt0w']+ \
                            ["dt1y",'dt1m','dt1d','dt1w']+ \
                            ['dt01n']+row[(self.numDateEnd+1):]
                     out0.writerow(h01)
                     out1.writerow(h01)
                     continue;
                 dateTime = datetime.datetime.strptime(row[self.numDateTime],"%Y-%m-%d %H:%M:%S")
                 
                 try :
                     dateTime = datetime.datetime.strptime(row[self.numDateTime],"%Y-%m-%d %H:%M:%S")
                 except :
                     dateTime = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                 try :
                     dateBeg  = datetime.datetime.strptime(row[self.numDateBeg],"%Y-%m-%d")
                 except :
                     dateBeg  = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                 try :
                     dateEnd  = datetime.datetime.strptime(row[self.numDateEnd],"%Y-%m-%d")
                 except :
                     dateEnd  = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                     
                 if self.debug : print(dateTime,dateBeg,dateEnd)
                 
                 dateTimeV= [dateTime.year,dateTime.month,dateTime.day,dateTime.weekday(),
                             dateTime.hour,dateTime.minute]
                 dateBegV = [dateBeg.year,dateBeg.month,dateBeg.day,dateBeg.weekday()]
                 dateEndV = [dateEnd.year,dateEnd.month,dateEnd.day,dateEnd.weekday()]
                 
                 datesNN  = (dateEnd-dateBeg).days+1
                 if (not((0<=datesNN) and (datesNN<=200))) : datesNN=0
                 datesNN=[datesNN]
                 
                 rowX = dateTimeV+row[1:self.numDateBeg]+dateBegV+dateEndV+datesNN+row[(self.numDateEnd+1):]
                 if self.debug : print(dateTimeV,dateBegV,dateEndV,datesNN)
                 if row[self.numBook]=='0' :
                     out0.writerow(rowX); i0 +=1
                 else :
                     out1.writerow(rowX); i1 +=1
                 #if reader.line_num>100000 : break
                 if reader.line_num%10000==0 : print(reader.line_num)
            csvfile.close();
            wrt0.close();
            wrt1.close();
            print("(0,1)=",i0,i1)
            return
        
    def getLeak(self) :

        d1 = dict();
        d2 = dict();
        d3 = dict();
        d4 = dict();
        cluster0 = [0]*100
        
        with open(self.inputFile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i0, i1, ie = 0,0,0; le =[]
            for row in reader :
                 if reader.line_num==1:
                     #wrt0 = open(self.outBook0,"w")
                     #wrt1 = open(self.outBook1,"w")
                     #out0 = csv.writer(wrt0,delimiter=',', quotechar='|')
                     #out1 = csv.writer(wrt1,delimiter=',', quotechar='|')
                     continue;
                    
                 dateTime = datetime.datetime.strptime(row[self.numDateTime],"%Y-%m-%d %H:%M:%S")
                 
                 try :
                     dateTime = datetime.datetime.strptime(row[self.numDateTime],"%Y-%m-%d %H:%M:%S")
                 except :
                     dateTime = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                 try :
                     dateBeg  = datetime.datetime.strptime(row[self.numDateBeg],"%Y-%m-%d")
                 except :
                     dateBeg  = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                 try :
                     dateEnd  = datetime.datetime.strptime(row[self.numDateEnd],"%Y-%m-%d")
                 except :
                     dateEnd  = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                     
                 if self.debug : print(dateTime,dateBeg,dateEnd)
                 
                 datesNN  = (dateEnd-dateBeg).days+1
                 if (not((0<=datesNN) and (datesNN<=200))) : datesNN=0
                 datesNN=[datesNN]

                 isBooking = int(row[self.numBook])
                 ULC       = row[self.numULC]
                 ODD       = row[self.numODD]
                 SDI       = row[self.numSDI]
                 HMarket   = row[self.numHMarket]
                 HCountry  = row[self.numHCountry]
                 HCluster  = int(row[self.numHCluster])

                 app1      = 3+17*isBooking
                 app2      = 1+ 5*isBooking

                 if ((ULC!="") and (ODD!="")) :
                     key = (ULC,ODD)
                     cluster = d1.get(key,cluster0)
                     cluster[HCluster] += 1
                     d1[key]=cluster

                 if ((SDI!="") and (HCountry!="") and (HMarket!="") and (dateTime.year==2014)) :
                     key = (SDI,HCountry,HMarket)
                     cluster = d2.get(key,cluster0)
                     cluster[HCluster] += app1
                     d2[key]=cluster

                 if ((SDI!="")) :
                     key = (SDI)
                     cluster = d3.get(key,cluster0)
                     cluster[HCluster] += app1
                     d3[key]=cluster

                 if ((HCountry!="")) :
                     key = (HCountry)
                     cluster = d4.get(key,cluster0)
                     cluster[HCluster] += app2
                     d4[key]=cluster

                 if self.debug : print(dateTimeV,dateBegV,dateEndV,datesNN)
                 if reader.line_num>30000 : break
                 if reader.line_num%10000==0 : print(reader.line_num)
            csvfile.close();
            #wrt0.close();
            #wrt1.close();
            print(len(d1),len(d2),len(d3),len(d4))
            print(list(d1.keys())[0:1])
            print(list(d1.values())[0:1])
            print("(0,1)=",i0,i1)

            self.writeDD(self.outD1,d1);
            
            return
        
    def writeDD (self,outFile,dd) :
        wrt0 = open(outFile,"w")
        out0 = csv.writer(wrt0,delimiter=',', quotechar='|')
        h01  = ["user_location_city","orig_destination_distance",'p1','p2','p3','p4',"p5"]
        out0.writerow(h01)
        for i in dd.keys() :
            value  = dd[i]; value.sort(reverse=True)
            row = [i[0],i[1],value[0],value[1],value[2],value[3],value[4]]
            out0.writerow(row)
        wrt0.close();
        
class PreTest (BigCSVFile) :

    debug     = False

    inputFile   = ""
    #outBook0    = "../Data/testBook0.csv"
    outBook1    = "../Data/testBook1.csv"
    
    baseField   = 1
    
    numBook     = 18+baseField
    numCnt      = numBook+1
    numDateTime = 0+baseField
    numDateBeg  = 11+baseField
    numDateEnd  = 12+baseField
    def __init__ (self,input) :
        self.inputFile = input;
        self.readHeader(input)
    def readSplitIsBooking(self) :
        with open(self.inputFile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i0, i1, ie = 0,0,0; le =[]
            for row in reader :
                 if reader.line_num==1:
                     #wrt0 = open(self.outBook0,"w")
                     wrt1 = open(self.outBook1,"w")
                     #out0 = csv.writer(wrt0,delimiter=',', quotechar='|')
                     out1 = csv.writer(wrt1,delimiter=',', quotechar='|')
                     h01  = ["id"]+["dty",'dtm','dtd','dtw','dth','dtm']+row[(self.numDateTime+1):self.numDateBeg]+ \
                            ["dt0y",'dt0m','dt0d','dt0w']+ \
                            ["dt1y",'dt1m','dt1d','dt1w']+ \
                            ['dt01n']+ \
                            row[(self.numDateEnd+1):self.numBook]+ \
                            ["is_booking","cnt"]+ \
                            row[self.numBook:]
                     #out0.writerow(h01)
                     out1.writerow(h01)
                     continue;
                 try :
                     dateTime = datetime.datetime.strptime(row[self.numDateTime],"%Y-%m-%d %H:%M:%S")
                 except :
                     dateTime = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                 try :
                     dateBeg  = datetime.datetime.strptime(row[self.numDateBeg],"%Y-%m-%d")
                 except :
                     dateBeg  = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                 try :
                     dateEnd  = datetime.datetime.strptime(row[self.numDateEnd],"%Y-%m-%d")
                 except :
                     dateEnd  = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                     
                 if self.debug : print(dateTime,dateBeg,dateEnd)
                 dateTimeV= [dateTime.year,dateTime.month,dateTime.day,dateTime.weekday(),
                             dateTime.hour,dateTime.minute]
                 dateBegV = [dateBeg.year,dateBeg.month,dateBeg.day,dateBeg.weekday()]
                 dateEndV = [dateEnd.year,dateEnd.month,dateEnd.day,dateEnd.weekday()]
                 
                 datesNN  = (dateEnd-dateBeg).days+1
                 if (not((0<=datesNN) and (datesNN<=200))) : datesNN=0
                 datesNN=[datesNN]
                 rowX = row[0:self.numDateTime]+dateTimeV+row[(self.numDateTime+1):self.numDateBeg]+dateBegV+dateEndV+datesNN+ \
                            row[(self.numDateEnd+1):self.numBook]+ \
                            [1,1]+ \
                            row[self.numBook:]
                 if self.debug : print(dateTimeV,dateBegV,dateEndV,datesNN)
                 """
                 if row[self.numBook]=='0' :
                     out0.writerow(rowX); i0 +=1
                 else :
                     out1.writerow(rowX); i1 +=1
                 """
                 out1.writerow(rowX); i1 +=1
                 #if reader.line_num>1000 : break
                 if reader.line_num%100000==0 : print(reader.line_num)
            csvfile.close();
            #wrt0.close();
            wrt1.close();
            print("(0,1,e,list_error)=",i0,i1,ie,le)
            return
        
def LeakDecision (trainFile,testFile,out1,out2,dirDict=None,
                  debug=False,debugStop=3000000,
                  printOK=False) :

    #debug     = True
    #print     = True

    # for Train file

    numBook     = 18
    numDateTime = 0
    numDateBeg  = 11
    numDateEnd  = 12

    # for leak data
    numULC      =  5  # user_location_city
    numODD      =  6  # orig_destination_distance
    numSDI      = 16  # srch_destination_id
    numHCluster = 23  # hotel_cluster
    numHCountry = 21  # hotel_country 
    numHMarket  = 22  # hotel_market
    
    cluster0 = [0]*100
    
    d1 = dict();
    d2 = dict();
    d3 = dict();
    d4 = dict();
    
    topCluster = cluster0;
        
    with open(trainFile, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i1, i2, i3, i4, ie = 0,0,0,0,0; le =[]
        for row in reader :
            if reader.line_num==1: continue

            try :
                dateTime = datetime.datetime.strptime(row[self.numDateTime],"%Y-%m-%d %H:%M:%S")
            except :
                dateTime = datetime.datetime(2012,1,1); ie+=1; le.append(reader.line_num)
                     
            isBooking = int(row[numBook])
            ULC       = row[numULC]
            ODD       = row[numODD]
            SDI       = row[numSDI]
            HMarket   = row[numHMarket]
            HCountry  = row[numHCountry]
            HCluster  = int(row[numHCluster])

            app1      = 3+17*isBooking
            app2      = 1+ 5*isBooking

            if ((ULC!="") and (ODD!="")) :
                 key = (ULC,ODD)
                 cluster = d1.get(key,[0]*100)
                 cluster[HCluster] += 1
                 d1[key]=cluster; i1 +=1;

            if ((SDI!="") and (HCountry!="") and (HMarket!="") and (dateTime.year==2014)) :
                 key = (SDI,HCountry,HMarket)
                 cluster = d2.get(key,[0]*100)
                 cluster[HCluster] += app1
                 d2[key]=cluster; i2 +=1

            if ((SDI!="")) :
                 key = (SDI)
                 cluster = d3.get(key,[0]*100)
                 cluster[HCluster] += app1
                 d3[key]=cluster; i3 +=1

            if ((HCountry!="")) :
                 key = (HCountry)
                 cluster = d4.get(key,[0]*100)
                 cluster[HCluster] += app2
                 d4[key]=cluster; i4 +=1

            topCluster[HCluster] += 1

            if (debug and (reader.line_num>debugStop)) : break
            if (reader.line_num%100000==0) :
                print("train :",reader.line_num," d1-4 : ",
                      sys.getsizeof(d1),"-",len(d1),
                      sys.getsizeof(d2),"-",len(d2),
                      sys.getsizeof(d3),"-",len(d3),
                      sys.getsizeof(d4),"-",len(d4))
                
            if (reader.line_num%3000000==0) :
                if (dirDict!=None) :
                    print("dumping")
                    d0 = dict     (line=reader.line_num,
                                   begin=reader.line_num+1,
                                   top=topCluster,
                                   stats=gc.get_stats(),
                                   count=gc.get_count(),
                                   thres=gc.get_threshold()
                                   );
                    f = open(os.path.join(dirDict,"d0.dict"),"w")
                    json.dump(d0,f);
                    f.close();
                    f = open(os.path.join(dirDict,"d1.dict"),"wb")
                    pickle.dump(d1,f); f.close();
                    f = open(os.path.join(dirDict,"d2.dict"),"w")
                    json.dump(d2,f); f.close();
                    f = open(os.path.join(dirDict,"d3.dict"),"w")
                    json.dump(d3,f); f.close();
                    f = open(os.path.join(dirDict,"d4.dict"),"w")
                    json.dump(d4,f); f.close();
                    print("gc",gc.get_count(),gc.get_stats(),gc.get_threshold());
                    print("end dumping")
                
            
        csvfile.close();
        
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

    # for Test file

    numULC      =  6  # user_location_city
    numODD      =  7  # orig_destination_distance
    
    numSDI      = 17  # srch_destination_id
    numHCountry = 20  # hotel_country 
    numHMarket  = 21  # hotel_market
    
    numDateTime = 1
    numID       = 0 

    top5x0      = [ str(x[0]) for x in nlargest(5,enumerate(topCluster),key=lambda x:x[1])]
    print("top5x0",top5x0)
    
        
    with open(testFile, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i1, i2, i3, i4, ie = 0,0,0,0,0; le =[]
        out1f  = open(out1,"w")
        out2f  = open(out2,"w")
        for row in reader :
            if reader.line_num==1:
                print("id,hostel_cluster",file=out1f);
                print("id,hostel_cluster,mark",file=out2f);
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
            
            
            if ((ULC!="") and (ODD!="")) :
                 key = (ULC,ODD)
                 if key in d1 :
                     cluster = d1.get(key)
                     top5 = nlargest(5,enumerate(cluster),key=lambda x:x[1])
                     top5 = [str(x[0]) for x in top5]
                     out  = top5
                     mark = 1
                     
            if ((SDI!="") and (HCountry!="") and (HMarket!="")) :
                 key = (SDI,HCountry,HMarket)
                 if key in d2 :
                     cluster = d2.get(key)
                     top5 = nlargest(5,enumerate(cluster),key=lambda x:x[1])
                     top5 = [str(x[0]) for x in top5]
                     out  = (out + top5)[:5];
                     mark += 2

            if ((SDI!="")) :
                 key = (SDI)
                 if key in d3 :
                     cluster = d3.get(key)
                     top5 = nlargest(5,enumerate(cluster),key=lambda x:x[1])
                     top5 = [str(x[0]) for x in top5]
                     out  = (out + top5)[:5];
                     mark += 4

            if ((HCountry!="")) :
                 key = (HCountry)
                 if key in d4 :
                     cluster = d4.get(key)
                     top5 = nlargest(5,enumerate(cluster),key=lambda x:x[1])
                     top5 = [str(x[0]) for x in top5]
                     out  = (out + top5)[:5];
                     mark += 8
            if (len(out)<5) : out  = (out+top5x0)[:5]; mark += 16;
            if (debug and reader.line_num>200) : break;
            out = (" ".join(out)).strip()
            print(str(id)+',"'+out+'"',file=out1f);
            print(str(id)+',"'+out+'",'+str(mark),file=out2f);
            if (reader.line_num%100000==0) :
                print("test :",reader.line_num)


        csvfile.close()
        out1f.close()
        out2f.close()
            

    return
        

fTrain = '../Data/train.csv';
fTest  = '../Data/test.csv';
fOut1  = '../Result/Leak/df-Leak.csv';
fOut2  = '../Result/Leak/df-LeakExt.csv';
fDict  = '../Result/Leak/'

print('-'*50)

if False :
    strTrain = PreTrain(fTrain);
    print(strTrain.count(),strTrain.getNames())
    #strTrain.readSplitIsBooking();
    strTrain.getLeak();

if True :
    strTest = PreTest(fTest);
    print(strTest.count(),strTest.getNames())
    #strTest.readSplitIsBooking();

LeakDecision(fTrain,fTest,fOut1,fOut2,dirDict=fDict,
             debug=True,debugStop=10000000)
