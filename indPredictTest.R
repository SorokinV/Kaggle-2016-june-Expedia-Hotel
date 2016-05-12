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

head(tmp.res); nrow(tmp.res)

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

