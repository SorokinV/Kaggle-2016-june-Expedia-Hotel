require(xgboost)
require(caTools)

set.seed(1234)

m.true  <- sample.split(train.m$hotel_cluster,SplitRatio = 0.50)

m.excl  <- c(1,3,4,5,6,16,17,19,21,22,23,24,31,32,36, 30,8,13)
m.excl  <- c(1:28,31,32,33,36) # better
m.excl  <- c(1:33,36) # only hotel
#m.excl  <- c(1:28,31:36) # only srch_destination ---------- badly
m.excl  <- c(1:10,13:36) # badly
m.excl  <- c(1:28,30,31,32,33,36) # better? 
m.excl  <- c(1:17,19:28,31,32,33,36) # better
(names(train.m))
(names(train.m))[m.excl]
(names(train.m))[setdiff(c(1:length(train.m)),m.excl)]

tmp     <- as.matrix(subset(train.m[,-m.excl],m.true));
tmp[is.na(tmp)] <- 0
m.train <- xgb.DMatrix(tmp,label = train.m$hotel_cluster[m.true]);

tmp     <- as.matrix(subset(train.m[,-m.excl],!m.true));
tmp[is.na(tmp)] <- 0
m.test  <- xgb.DMatrix(tmp,label = train.m$hotel_cluster[!m.true]);

eta     <- 0.25
nrounds <- 300
multi   <- 100

  evalerror <- function(preds,dtrain) {
    labels  <- getinfo(dtrain,"label")
    estimate<- max.col(matrix(preds,ncol=100,nrow=length(labels),byrow=TRUE))-1
    err     <- length(estimate[estimate==labels])/length(labels)
    #if (err>limit) err <- limit
    return(list(metric="boba",value=err))
  } 
  
  param  <- list(objective="multi:softprob", #"rank:pairwise",
                 num_class=multi,
                 max.depth=6,
                 eta=eta,
                 eval_metric=evalerror, #c("mae"),
                 maximaze = TRUE,
                 silent=0)
  
  watchlist <- list(eval=m.test) #, train=mtrain)
  
  rm(bst)
  set.seed(1234)
  bst    <- xgb.train(param, m.train, 
                      watchlist = watchlist,
                      nrounds=nrounds,
                      early.stop.round = 5,
                      maximize = TRUE,
                      print.every.n = 1)
  
imp = xgb.importance(colnames(tmp),model=bst)
str(imp)

preds  = predict(bst,m.train)
preds  = matrix(preds,ncol=100,nrow=length(labels),byrow=TRUE)
labels = train.m$hotel_cluster[m.true]
estimate  <- max.col(matrix(preds,ncol=100,nrow=length(labels),byrow=TRUE))-1
err       <- length(estimate[estimate==labels])/length(labels); err
tmp.true  <- (estimate==labels)
tmp.sd    <-  unlist(lapply(c(1:nrow(preds)),function(x){sd(preds[x,])}))
tmp.qt    <-  unlist(lapply(c(1:nrow(preds)),function(x){quantile(preds[x,],names=FALSE)[3]}))
tmp.qt100 <-  unlist(lapply(c(1:nrow(preds)),function(x){quantile(preds[x,],names=FALSE)[5]}))
tmp.qt099 <-  unlist(lapply(c(1:nrow(preds)),
                     function(x){quantile(preds[x,],probs = c(0.98,1.0),names=FALSE)[1]}))



tmp.df    <- data.frame(sd=unlist(tmp.sd),
                        bk=train.m$user_id[m.true],
                        med=unlist(tmp.qt),
                        max=unlist(tmp.qt100),
                        qt099=unlist(tmp.qt099),
                        p01 = ifelse(tmp.true,1,0))

require(ggplot2)

q1 = ggplot(tmp.df,aes(x=sd,y=(max-qt099))) +
     geom_point(aes(color=bk))+
     facet_grid(.~p01)
q1

table(tmp.df$bk[m.true],tmp.true)

preds = predict(bst,m.test)
labels = label = train.m$hotel_cluster[!m.true]
estimate<- max.col(matrix(preds,ncol=100,nrow=length(labels),byrow=TRUE))-1
err     <- length(estimate[estimate==labels])/length(labels); err

rm(imp,preds,tmp,tmp.df)
rm(err,estimate,eta,label,labels)
rm(m.excl,m.test,m.train,multi)
rm(nrounds,param,q1)
rm(tmp.qt,tmp.qt099,tmp.qt100,tmp.qt097)
rm(tmp.sd,watchlist)
