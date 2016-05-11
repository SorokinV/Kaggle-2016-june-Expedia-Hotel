require(xgboost)

#
#--------- Exp No. 2: Fragmentation based on country and 66 country (1.5M records) on regions
#

base.list    = sort(unique(dtrain.b1$user_location_country))
base.multi   = 100
base.max     = 150000

base.files   = c()
base.exclude = c(66)

base.list    = setdiff(base.list,base.exclude);

#base.list    = base.list[c(1:20)]

dir.files    = "./Temp/BST-Country/";
bst.files    = c();
bst.country  = rep(-1,times=(max(base.list)+1));


i.set        = 1
repeat {
  if (i.set>length(base.list)) break;
  tmp.list   = c(i.set)
  print(c("repeat1-->",tmp.list))
  i.train    = subset(dtrain.b1,(user_location_country==base.list[i.set]))
  
  if (FALSE) {
  i.set      = i.set+1;
  repeat {
    if (i.set>length(base.list)) break;
    tmp.list   = c(tmp.list,i.set)
    i.train    = rbind(i.train,subset(dtrain.b1,(user_location_country==base.list[i.set])));
    #print(tmp.list)    
    if (nrow(i.train)>base.max) break;
    i.set = i.set+1;
  }
  
  }
  
  print (sprintf("%s work i=%i nrow=%i",
                 format(Sys.time(),"%Y-%m-%d %H:%M:%S"),
                 i.set,nrow(i.train)));
  print(base.list[tmp.list])
  
  if (nrow(i.train)>0) {
    
    bst.train  <- xgb.ttrain(i.train,i.train$hotel_cluster,
                             eta=0.2,nrounds=50,
                             multi=base.multi)
    bst.file  = paste(base.list[tmp.list],sep='X',collapse='X')
    bst.file  = paste(dir.files,bst.file,'.bst',sep='',collapse = "")
    xgb.save(bst.train,bst.file)
    bst.files = c(bst.files,bst.file)
    bst.country[base.list[tmp.list]+1] <- length(bst.files)
    bst.country[base.list[tmp.list]+1] <- bst.file
    
  }
  
  print (sprintf("%s bst end",format(Sys.time(),"%Y-%m-%d %H:%M:%S")));
  
  i.set = i.set+1;
  
}

rm(i.set,i.train,tmp.list)
rm(bst.train,bst.file)

#---------------------------------------------------------------

i=26
train.list     = base.list[base.list>=0]
train.list.res = c()
train.list.len = c()
for (i in train.list) {

  xtrain      <- subset(dtrain.b1,(user_location_country==i)); nnrow=nrow(xtrain)
  ltrain      <- xtrain$hotel_cluster;
  xtrain      <- as.matrix(xtrain[1:(length(xtrain)-1)])
  xtrain[is.na(xtrain)] <- 0
  
  pre.train   <- xgb.ppredict1(bst.country[i+1],xtrain)

  pre.train.m <- max.col(pre.train[,1:base.multi])-1
  
  pre.train.b <- (pre.train.m==ltrain)
  train.list.len = c(train.list.len,length(pre.train.b))
  train.list.res = c(train.list.res,(length(pre.train.b[pre.train.b==TRUE])/length(pre.train.b)))
  print(sprintf("c=%3.0i row=%7.0f acc=%5.2f",i,nnrow,100*length(pre.train.b[pre.train.b==TRUE])/length(pre.train.b)))

}

train.list.city <- rep(-1,times=length(train.list))

train.df = data.frame(country  = train.list, 
                      city     = rep(-1,times=length(train.list)),
                      length   = train.list.len,
                      accuracy = train.list.res, 
                      files    = bst.files)

plot(train.list,train.list.res)

sum(train.df$length)
sum(train.df$length*train.df$accuracy)

sum(train.df$length*train.df$accuracy)/sum(train.df$length)

#image(c(1:nrow(pre.train)),c(1:100),pre.train,useRaster = TRUE,col=gray((0:5)/5))

rm(xtrain,ltrain,pre.train.b)

#-----------------------------------------------------------------

#-----------------------------------------------------------------


xx.train = subset(dtrain.b1,(dtrain.b1$user_location_country==66));
bst.train  <- xgb.ttrain(xx.train,xx.train$hotel_cluster,eta=0.1,nrounds=10)


rm(xx.train)
#----------------------- function --------------------------------

xgb.ttrain <- function(ddata,llabel,eta=0.1,nrounds=50,multi=100) {

  ddata$orig_destination_distance[is.na(ddata$orig_destination_distance)] <- 0
  
  mtrain <- xgb.DMatrix(as.matrix(ddata[1:(length(ddata)-1)]),
                        label=ddata$hotel_cluster)
 
  evalerror <- function(preds,dtrain) {
    labels  <- getinfo(dtrain,"label")
    estimate<- max.col(matrix(preds,ncol=100,nrow=length(labels),byrow=TRUE))-1
    err     <- length(estimate[estimate==labels])/length(labels)
    #if (err>limit) err <- limit
    return(list(metric="boba",value=err))
  } 
  
  param  <- list(objective="multi:softprob", #"rank:pairwise",
                 num_class=100,
                 max.depth=6,
                 eta=eta,
                 eval_metric=evalerror, #c("mae"),
                 #maximaze = TRUE,
                 silent=0)
  
  watchlist <- list(eval=mtrain, train=mtrain)
  
  bst    <- xgb.train(param, mtrain, 
                      watchlist = watchlist,
                      nrounds=nrounds,
                      early.stop.round = 5,
                      maximize = TRUE,
                      print.every.n = 1)
  
  return(bst)
  
}  
  

xgb.ppredict <- function(bstfiles,bstlists,ddata,ncol=100) {
  
  require(xgboost)
  
  pre = matrix(0,ncol=ncol,nrow=nrow(ddata),byrow = TRUE)
  il  = 0
  for (i in bstfiles) { il = il + 1;
    pre.one <- pre.ppredict1(i,ddata)
    xlist   <- bstlists[[il]]     
    #print(xlist)
    for (j in xlist) {
      pre[,j+1] <- pre[,j+1] + pre.one[,j+1]
    }   
    k = xlist[1]
    #print(xlist[1])
    for (j in xlist) { #xlist[2:length(xlist)]) {
      pre[,j+1] <- pre[,j+1] - pre.one[,k+1]
    }   
  }
  
  return(pre)
  
}

xgb.ppredict1 <- function(bstfile,ddata,ncol=100) {
  
  require(xgboost)
  
  bst.pre <- xgb.load(bstfile)
  #print(c("ppedict1 -->",ddata,nrow(ddata)))
  #print("--")
  pre.one <- predict(bst.pre,ddata)
  #print("-- --")
  pre.one <- matrix(pre.one,ncol=ncol,nrow=nrow(ddata),byrow = TRUE)
  #print("-- -- --")
  return(pre.one)
  
}