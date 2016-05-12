require(xgboost)

#df.city = buildCitiesList(c(3,46,69))

#df.city = buildCitiesList(c(66),dir.files = "./Temp/BST-Cities-66/")

df.true = (dtrain.b1$user_location_country==77)
df.data = subset(dtrain.b1[1:(length(dtrain.b1)-1)],df.true)

df.pred = predictData(df.city,df.data)

df.max = ((max.col(df.pred)-1)==dtrain.b1$hotel_cluster[df.true])

rm(df.data,df.pred)

xx=table(df.max); 
xx; unlist(xx[2]/sum(xx))

table(max.col(df.pred)-1)

#------------------------ common index ------------------------------------

df.index = rbind(df.index,df.city)

write.csv(df.index,file="./Temp/df-index.csv",row.names = FALSE)

#----------------------- function  predict --------------------------------

predictData     <- function (index,data) {
  res           <- matrix(0,ncol=100,nrow=nrow(data),byrow = TRUE)
  countries     <- sort(unique(data$user_location_country))
  for (ic in countries) {
    icTrue      <- (data$user_location_country==ic)
    tmp.res     <- predictCountry(index,ic,subset(data,icTrue))
    res[icTrue,] <- tmp.res[,]
  }
  return (res)
}

predictCountry  <- function (index,ic,data) {
  
  cities        <- sort(unique(data$user_location_city))
  indCities     <- sort(unique(index$city[index$country==ic]))
  xdata         <- as.matrix(data)
  xdata[is.na(xdata)] <- 0
  xdata         <- xgb.DMatrix(xdata)
  
  if (length(indCities)==1) {
    bst.file <- as.character(index$files[index$country==ic]); 
#    print(c("1-->",bst.file,dim(xdata)))
    res = xgb.ppredict1(bst.file,xdata)
    return(res)
  }
  
  res           <- matrix(0,ncol=100,nrow=nrow(data))
  for (icts in cities) {
    icTrue      <- (data$user_location_city==icts)
    bst.file    <- as.character(index$files[(index$country==ic)&(index$city==icts)]); 
    
#    print(c("2-->",bst.file,icts,"--",cities,indCities,dim(data),length(icTrue[icTrue==TRUE])))
    
    tmp.res     <- xgb.ppredict1(bst.file,slice(xdata,c(1:nrow(data))[icTrue]))
    res[icTrue,] <- tmp.res[,]
  }
  
  return (res)
}

#----------------------- function build --------------------------------

buildCitiesList <- function( countries,dir.files="./Temp/BST-Cities/" ) {
  
  tmp.res = data.frame()
  
  for (ic in countries) {
    tmp.city <- buildCitiesCountry(ic,dir.files=dir.files)
    tmp.res  <- rbind(tmp.res,tmp.city) 
  }
  
  return(tmp.res)
}


#
#--------- Exp No. 3: Fragmentation based on country and city
#


buildCitiesCountry <- function(user_l_country,
                               dir.files="./Temp/BST-Cities/") {
  
  trueCountry  <- (dtrain.b1$user_location_country==user_l_country)

  base.list    = sort(unique(dtrain.b1$user_location_city[trueCountry]))
  base.multi   = 100
  base.max     = 7000 # 9000 # 6000
  
  base.files   = c()
  base.exclude = c()
  
  base.list    = setdiff(base.list,base.exclude);
  
  #base.list   = base.list[c(1:20)]
  
  bst.files    = c();
  aaccuracy    = c();
  llength      = c();
  
  #base.list   = base.list[c(846:length(base.list))]
  i.set        = 0
  
  repeat {
    i.set = i.set+1;
    if (i.set>length(base.list)) break;
    tmp.list   = c(i.set)
    print(c("repeat1 (i.set,length,size) -->",tmp.list,length(base.list),length(trueCountry[trueCountry])))
    i.train    = subset(dtrain.b1,
                        (trueCountry&(user_location_city==base.list[i.set])))
    
    repeat {
      i.set      = i.set+1;
      if (i.set>length(base.list)) break;
      tmp.list   = c(tmp.list,i.set)
      i.train    = rbind(i.train,subset(dtrain.b1,
                            (trueCountry&(user_location_city==base.list[i.set]))))
      #print(tmp.list)    
      if (nrow(i.train)>base.max) break;
    }
    
    print (sprintf("%s work i=%i nrow=%i",
                   format(Sys.time(),"%Y-%m-%d %H:%M:%S"),
                   i.set,nrow(i.train)));
    print(c("min,max,len -->",min(base.list[tmp.list]),max(base.list[tmp.list]),length(tmp.list)))
    
    if (nrow(i.train)>0) {
      
      bst.train  <- xgb.ttrain(i.train,i.train$hotel_cluster,
                               eta=0.2,nrounds=50,
                               multi=base.multi)
      
      bst.file  = paste(base.list[tmp.list[1]],sep='X',collapse='X')
      bst.file  = paste(user_l_country,bst.file,sep='-',collapse='-')
      
      bst.file  = paste(dir.files,bst.file,'.bst',sep='',collapse = "")
      xgb.save(bst.train,bst.file)
      bst.files = c(bst.files,rep(bst.file,times=length(tmp.list)))
    }
    
    if (TRUE) {
      ltrain          <- i.train$hotel_cluster;
      xtrain          <- as.matrix(i.train[1:(length(i.train)-1)])
      xtrain[is.na(xtrain)] <- 0
      
      pre.train       <- xgb.ppredict1(bst.file,xtrain)
      pre.train.m     <- max.col(pre.train[,1:base.multi])-1
      pre.train.b     <- (pre.train.m==ltrain)
      llength         <- c(llength,  rep(length(pre.train.b),
                                         times=length(tmp.list)))
      aaccuracy       <- c(aaccuracy,rep(length(pre.train.b[pre.train.b==TRUE])/length(pre.train.b),
                                         times=length(tmp.list)))
      rm(pre.train,pre.train.b,pre.train.m)
      rm(xtrain,ltrain)
    }
    
    print (sprintf("%s bst end",format(Sys.time(),"%Y-%m-%d %H:%M:%S")));

  }
  
  
  
  df.res = data.frame(country   = rep(user_l_country,times=length(base.list)),
                      city      = base.list,
                      length    = llength,
                      accuracy  = aaccuracy,
                      files     = bst.files)
  
  rm(i.set,i.train,tmp.list)
  rm(bst.train,bst.file)
  
  return(df.res)
  
}
  
