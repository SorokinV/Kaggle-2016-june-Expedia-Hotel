
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
                 if reader.line_num%10000==0 : print(reader.line_num,"\t",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            csvfile.close();
            wrt0.close();
            wrt1.close();
            print("(0,1)=",i0,i1)
            return
        
    def transform(self,outBook,debug=False,debugStop=1000000) :
        with open(self.inputFile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i0, ie = 0,0; le =[]
            for row in reader :
                 if reader.line_num==1:
                     wrt0 = open(outBook,"w")
                     out0 = csv.writer(wrt0,delimiter=',', quotechar='|')
                     h01  = ["dty",'dtm','dtd','dtw','dth','dtmi']+ \
                             row[1:self.numDateBeg]+ \
                            ["dt0y",'dt0m','dt0d','dt0w']+ \
                            ["dt1y",'dt1m','dt1d','dt1w']+ \
                            ['dt01n']+row[(self.numDateEnd+1):]
                     out0.writerow(h01)
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
                 out0.writerow(rowX); i0 +=1
                 if (debug and (reader.line_num>debugStop)) : break
                 if reader.line_num%100000==0 : print(reader.line_num,"\t",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            csvfile.close();
            wrt0.close();
            print("(0,1)=",i0,ie)
            return

    def select(self, dtmi, inSet, outSet, debug=False,debugStop=1000000) :
        numDtmi = 5
        #print("----",inSet,outSet)
        with open(inSet, newline='\n') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i0, i1 = 0,0;
            for row in reader :
                 if row==[] : continue
                 #print(row)
                 if reader.line_num==1:
                     wrt0 = open(outSet,"w")
                     out0 = csv.writer(wrt0,delimiter=',', quotechar='|')
                     out0.writerow(row)
                     continue;
                 i0 += 1; 
                 if (int(row[numDtmi]) == dtmi) : out0.writerow(row); i1 += 1;
                 
                 if (debug and (reader.line_num>debugStop)) : break
                 if reader.line_num%100000==0 :
                     print(reader.line_num,"\t",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                     wrt0.flush()
                 
            csvfile.close();
            wrt0.close();
            print("(in,out)=",i0,i1)
            return
        
        
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
    def transform(self,outBook,debug=False,debugStop=1000000) :
        with open(self.inputFile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i0, i1, ie = 0,0,0; le =[]
            for row in reader :
                 if reader.line_num==1:
                     #wrt0 = open(self.outBook0,"w")
                     wrt1 = open(outBook,"w")
                     #out0 = csv.writer(wrt0,delimiter=',', quotechar='|')
                     out1 = csv.writer(wrt1,delimiter=',', quotechar='|')
                     h01  = ["id"]+["dty",'dtm','dtd','dtw','dth','dtmi']+row[(self.numDateTime+1):self.numDateBeg]+ \
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
                 if (debug and (reader.line_num>debugStop)) : break
                 if reader.line_num%100000==0 : print(reader.line_num,"\t",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            csvfile.close();
            #wrt0.close();
            wrt1.close();
            print("(0,1,e,list_error)=",i0,i1,ie,le)
            return

if (__name__=="__main__") :
        
    fTrain          = '../Data/train.csv';
    fTrainExt       = '../Data/trainExt.csv';
    fTrainExtMin    = '../Data/trainExtMin.csv';
    
    fTest           = '../Data/test.csv';
    fTestExt        = '../Data/testExt.csv';
    
    fOut1           = '../Result/Leak/df-Leak.csv';
    fOut2           = '../Result/Leak/df-LeakExt.csv';
    
    fDict           = '../Result/Leak/'

    print('-'*50)

    if True :
        strTrain = PreTrain(fTrain);
        print("train:",strTrain.count(),"\n",list(enumerate(strTrain.getNames())))
        #strTrain.transform(fTrainExt,debug=False);
        strTrain.select(13,fTrainExt,fTrainExtMin,debug=False)

    if False :
        strTest = PreTest(fTest);
        print("test:",strTest.count(), "\n",list(enumerate(strTest.getNames())))
        strTest.transform(fTestExt,debug=False);
