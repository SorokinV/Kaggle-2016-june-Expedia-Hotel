import math
import os.path
import datetime

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
    numBook     = 18
    numDateTime = 0
    numDateBeg  = 11
    numDateEnd  = 12
    def __init__ (self,input) :
        self.inputFile = input;
        self.readHeader(input)
    def readSplitIsBooking(self) :
        with open(self.inputFile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i0, i1 = 0,0
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
                 if (row[self.numDateBeg]=="") : dateBeg=datetime.datetime(2000,1,1)
                 else : dateBeg  = datetime.datetime.strptime(row[self.numDateBeg],"%Y-%m-%d")
                 if (row[self.numDateEnd]=="") : dateEnd=datetime.datetime(2000,1,1)
                 else : dateEnd  = datetime.datetime.strptime(row[self.numDateEnd],"%Y-%m-%d")
                 if self.debug : print(dateTime,dateBeg,dateEnd)
                 dateTimeV= [dateTime.year,dateTime.month,dateTime.day,dateTime.weekday(),
                             dateTime.hour,dateTime.minute]
                 dateBegV = [dateBeg.year,dateBeg.month,dateBeg.day,dateBeg.weekday()]
                 dateEndV = [dateEnd.year,dateEnd.month,dateEnd.day,dateEnd.weekday()]
                 datesNN  = [(dateEnd-dateBeg).days+1]
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
        
class PreTest (BigCSVFile) :

    debug     = False

    inputFile   = ""
    #outBook0    = "../Data/testBook0.csv"
    outBook1    = "../Data/testBook1.csv"
    
    baseField   = 1
    
    #numBook     = 18+baseField
    numDateTime = 0+baseField
    numDateBeg  = 11+baseField
    numDateEnd  = 12+baseField
    def __init__ (self,input) :
        self.inputFile = input;
        self.readHeader(input)
    def readSplitIsBooking(self) :
        with open(self.inputFile, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            i0, i1 = 0,0
            for row in reader :
                 if reader.line_num==1:
                     #wrt0 = open(self.outBook0,"w")
                     wrt1 = open(self.outBook1,"w")
                     #out0 = csv.writer(wrt0,delimiter=',', quotechar='|')
                     out1 = csv.writer(wrt1,delimiter=',', quotechar='|')
                     h01  = ["id"]+["dty",'dtm','dtd','dtw','dth','dtm']+row[(self.numDateTime+1):self.numDateBeg]+ \
                            ["dt0y",'dt0m','dt0d','dt0w']+ \
                            ["dt1y",'dt1m','dt1d','dt1w']+ \
                            ['dt01n']+row[(self.numDateEnd+1):]
                     #out0.writerow(h01)
                     out1.writerow(h01)
                     continue;
                 try :
                     dateTime = datetime.datetime.strptime(row[self.numDateTime],"%Y-%m-%d %H:%M:%S")
                 except :
                     dateTime = datetime.datetime(2000,1,1);
                 try :
                     dateBeg  = datetime.datetime.strptime(row[self.numDateBeg],"%Y-%m-%d")
                 except :
                     dateBeg  = datetime.datetime(2000,1,1);
                 try :
                     dateEnd  = datetime.datetime.strptime(row[self.numDateBeg],"%Y-%m-%d")
                 except :
                     dateEnd  = datetime.datetime(2000,1,1);
                     
                 if self.debug : print(dateTime,dateBeg,dateEnd)
                 dateTimeV= [dateTime.year,dateTime.month,dateTime.day,dateTime.weekday(),
                             dateTime.hour,dateTime.minute]
                 dateBegV = [dateBeg.year,dateBeg.month,dateBeg.day,dateBeg.weekday()]
                 dateEndV = [dateEnd.year,dateEnd.month,dateEnd.day,dateEnd.weekday()]
                 datesNN  = [(dateEnd-dateBeg).days+1]
                 rowX = row[0:self.numDateTime]+dateTimeV+row[(self.numDateTime+1):self.numDateBeg]+dateBegV+dateEndV+datesNN+row[(self.numDateEnd+1):]
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
            print("(0,1)=",i0,i1)
            return
        

fTrain = '../Data/train.csv';
fTest  = '../Data/test.csv';

print('-'*50)

strTrain = PreTrain(fTrain);
print(strTrain.count(),strTrain.getNames())
#strTrain.readSplitIsBooking();

strTest = PreTest(fTest);
print(strTest.count(),strTest.getNames())
strTest.readSplitIsBooking();
