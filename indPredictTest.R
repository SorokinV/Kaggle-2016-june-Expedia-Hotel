require(xgboost)

#------------------------------------------------------------
#
# build decision from test data (first field == id, no last field)
#
# work in dataset = dtest.b1
#


tmp.countries <- sort(unique(dtest.b1$user_location_country))
tmp.exlude    <- c(3,46,69,77,205,66)
tmp.list0     <- setdiff(tmp.countries,tmp.exlude)

#tmp.res = predictTestList(df.index,tmp.countries[1:6])
#tmp.res = predictTestList(df.index,c(0,2),append="./Temp/df-result.csv")

tmp.res = predictTestList(df.index,tmp.list0,append="./Temp/df-result0.csv")

#tmp.res = predictTestList(df.index,c(3),  append="./Temp/df-result-003.csv")
#tmp.res = predictTestList(df.index,c(46), append="./Temp/df-result-046.csv")
#tmp.res = predictTestList(df.index,c(69), append="./Temp/df-result-069.csv")
#tmp.res = predictTestList(df.index,c(77), append="./Temp/df-result-077.csv")
#tmp.res = predictTestList(df.index,c(205),append="./Temp/df-result-205.csv")

#dtest.66 = dtest.b1

dtest.66.true = rep(FALSE,times=nrow(dtest.66))
i.step    = 200000

i0 = 1;
repeat {
  i1 = min(i0+i.step,nrow(dtest.66))
  tmp.true        <- dtest.66.true
  tmp.true[i0:i1] <- TRUE
  dtest.b1 = subset(dtest.66,tmp.true)
  tmp.res = predictTestList(df.index,c(66), append="./Temp/df-result-066.csv")
  i0 = i1+1;
  if (i0>nrow(dtest.66)) break;
}

#tmp.res = predictTestList(df.index,c(66), append="./Temp/df-result-066.csv")

tmp.res = read.csv("./Temp/df-result0.csv")
tmp.tmp = read.csv("./Temp/df-result-003.csv"); tmp.res = rbind(tmp.res,tmp.tmp)
tmp.tmp = read.csv("./Temp/df-result-046.csv"); tmp.res = rbind(tmp.res,tmp.tmp)
tmp.tmp = read.csv("./Temp/df-result-066.csv"); tmp.res = rbind(tmp.res,tmp.tmp)
tmp.tmp = read.csv("./Temp/df-result-069.csv"); tmp.res = rbind(tmp.res,tmp.tmp)
tmp.tmp = read.csv("./Temp/df-result-077.csv"); tmp.res = rbind(tmp.res,tmp.tmp)
tmp.tmp = read.csv("./Temp/df-result-205.csv"); tmp.res = rbind(tmp.res,tmp.tmp)

head(tmp.res); nrow(tmp.res)
write.csv(tmp.res,file="./Temp/df-result.csv",row.names = FALSE)

require(plyr)

res = arrange(tmp.res,id); head(res); tail(res)
res$country =NULL
write.csv(res,file="./Temp/df-result1.csv",row.names = FALSE)


stop("normal")

#----------------------------------------------

#---------------------- predict for test dataset ------------------

predictTestList <- function(index,listCountries,count=5,append=NULL) {

  res = data.frame()  
  if (!is.null(append)&(file.exists(append))) 
    res = read.csv(append,stringsAsFactors = FALSE)
  
  for (ic in listCountries) {
    print(sprintf("%s country--> %s nrow=%i",format(Sys.time(),"%Y-%m-%d %H:%M:%S"),ic,nrow(res)))
    tmp.res = predictTest1(index,ic,count = count)
    res = rbind(res,tmp.res)
    if (!is.null(append)) write.csv(res,file=append,row.names = FALSE)
  }
  
  print(sprintf("%s ---------> nrow=%i",format(Sys.time(),"%Y-%m-%d %H:%M:%S"),nrow(res)))
  
  return(res)
  
}


predictTest1   <- function (index,country,count=5) {
  
  data    <- subset(dtest.b1,dtest.b1$user_location_country==country)
  dataInd <- data$id
  data    <- data[2:length(data)]
  
  res     <- predictData(index,data)
  
  tmp.res <- max.col(res)-1 # indicate begin with 0, cols begins with 0
  res5    <- as.character(tmp.res)
  for (i in c(1:(count-1))) {
    for (j in c(1:length(tmp.res))) res[j,tmp.res[j]+1] <- -1
    tmp.res <- max.col(res)-1 # indicate begin with 0, cols begins with 0
    res5    <- paste(res5,tmp.res)
    #print(summary(res[1,]))
  }
  
  return(data.frame(country = rep(country,times=nrow(data)),
                    id=dataInd,
                    hotel_cluster=res5, stringsAsFactors = FALSE))
  
}

