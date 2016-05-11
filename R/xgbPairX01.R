require(xgboost)

base.cluster = 91
base.cluster = 0
stop.cluster = 100
stop.cluster = 100
max.cluster  = 150000

train.base   = subset(dtrain.b1,(hotel_cluster==base.cluster))

dirfiles     = "./Temp/BST/"
bstfiles     = c()
bstlists     = list()

i.cluster = 0; if (i.cluster==base.cluster) i.cluster <- i.cluster + 1
repeat {
  train.i = train.base; train.list = c(base.cluster)
  repeat {
    train.i = rbind(train.i,subset(dtrain.b1,(hotel_cluster==i.cluster)));
    train.list = c(train.list,i.cluster)
    if (nrow(train.i)>max.cluster) break;
    i.cluster = i.cluster+1;
    if (i.cluster==base.cluster) i.cluster=i.cluster+1
    if (i.cluster>=stop.cluster) break;
  }
  
  print (sprintf("%s work i=%i nrow=%i",format(Sys.time(),"%Y-%m-%d %H:%M:%S"),
                 i.cluster,nrow(train.i)));
  print(train.list)
  
  if (nrow(train.i)>nrow(train.base)) {
    
    bst.train  <- xgb.ttrain(train.i,train.i$hotel_cluster,eta=0.1,nrounds=10)
    bstfile  = paste(train.list,sep='X',collapse='X')
    bstfile  = paste(dirfiles,bstfile,'.bst',sep='',collapse = "")
    xgb.save(bst.train,bstfile)
    bstfiles = c(bstfiles,bstfile)
    bstlists[[length(bstlists)+1]] <- train.list
    
  }
  
  print (sprintf("%s bst end",format(Sys.time(),"%Y-%m-%d %H:%M:%S")));
  
  i.cluster = i.cluster + 1
  
  if (i.cluster>=stop.cluster) break;
    
}

#---------------------------------------------------------------

i=26
train.list     = c(0:(stop.cluster-1))
train.list.res = c()
for (i in train.list) {

  xtrain      <- subset(dtrain.b1,(hotel_cluster==i)); nnrow=nrow(xtrain)
  ltrain      <- xtrain$hotel_cluster;
  xtrain      <- as.matrix(xtrain[1:(length(xtrain)-1)])
  xtrain[is.na(xtrain)] <- 0
  
  pre.train   <- xgb.ppredict(bstfiles,bstlists,xtrain)
  
  pre.train.m <- max.col(pre.train[,1:stop.cluster])-1
  
  pre.train.b <- (pre.train.m==ltrain)
  train.list.res = c(train.list.res,(length(pre.train.b[pre.train.b==TRUE])/length(pre.train.b)))
  print(c(i,nnrow,length(pre.train.b[pre.train.b==TRUE])/length(pre.train.b)))

}

plot(train.list,train.list.res)

#-----------------------------------------------------------------

if (FALSE) {
  bstmap = matrix(0,nrow = length(train.list),ncol=1)
  for (l in c(1:length(bstlists))) {bstmap[bstlists[[l]]+1]=l}
  i = 18; i.file = bstfiles[bstmap[i+1]]; i.file
  xtrain      <- subset(dtrain.b1,(hotel_cluster==i)); nnrow=nrow(xtrain)
  ltrain      <- xtrain$hotel_cluster;
  xtrain      <- as.matrix(xtrain[1:(length(xtrain)-1)])
  xtrain[is.na(xtrain)] <- 0
  
  pre.train1  <- xgb.ppredict1(i.file,xtrain)

  pre.train.m <- max.col(pre.train1)-1
  pre.train1.p<- c()
  for (l in c(1:nrow(pre.train1))) pre.train1.p[l]=pre.train1[l,pre.train.m[l]+1]
  plot(sort(pre.train1.p))
  hist(pre.train1.p); nnrow
  
  pre.train.b <- (pre.train.m==ltrain)
  train.res = length(pre.train.b[pre.train.b==TRUE])/length(pre.train.b)
  train.res; length(pre.train.b[pre.train.b==TRUE])
}

#-----------------------------------------------------------------


xx.train = subset(dtrain.b1,(dtrain.b1$user_location_country==66));
bst.train  <- xgb.ttrain(xx.train,xx.train$hotel_cluster,eta=0.1,nrounds=10)


rm(xx.train)
#----------------------- function --------------------------------

xgb.ttrain <- function(ddata,llabel,eta=0.1,nrounds=50) {

  ddata$orig_destination_distance[is.na(ddata$orig_destination_distance)] <- 0
  
  mtrain <- xgb.DMatrix(as.matrix(ddata[1:(length(ddata)-1)]),
                        label=ddata$hotel_cluster)
 
  evalerror <- function(preds,dtrain) {
    labels  <- getinfo(dtrain,"label")
    estimate<- max.col(matrix(preds,ncol=100,nrow=length(labels),byrow=TRUE))-1
    err     <- length(estimate[estimate==labels])/length(labels)
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
  pre.one <- matrix(predict(bst.pre,ddata),ncol=ncol,nrow=nrow(ddata),byrow = TRUE)
  return(pre.one)
  
}