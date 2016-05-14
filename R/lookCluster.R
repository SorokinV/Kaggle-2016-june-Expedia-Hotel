require(fastcluster)

#----------------------------------------------------

nn.train = names(dtrain.b1)
nn.test  = names(dtest.b1)

nn = setdiff(intersect(nn.train,nn.test),c("is_booking","cnt","dt0y","dt1y"))

i=15

tt.diff = rep(0,times=length(nn)); names(tt.diff) <- nn

for (i in c(1:length(nn))) {

  tt.train = table(dtrain.b1[nn[i]]); l.train=length(tt.train)
  tt.test  = table(dtest.b1 [nn[i]]); l.test =length(tt.test)
  tt.nn    = union(names(tt.train),names(tt.test));
  
  tt = rep(0,times=length(tt.nn)); names(tt)=tt.nn;
  tt[names(tt.train)] = tt.train; tt.train=tt;
  
  tt = rep(0,times=length(tt.nn)); names(tt)=tt.nn;
  tt[names(tt.test)] = tt.test; tt.test=tt;
  
  tt.train=tt.train/sum(tt.train)
  tt.test =tt.test/sum(tt.test)
  
  tt.hot  = table(unlist(dtrain.b1[nn[i]]),dtrain.b1$hotel_cluster)
  tt.hot0 = rowSums(tt.hot)

  tt.diff[i] = sum(abs(tt.train-tt.test));
  
  print(sprintf("%i - %s --> %8.6f - %8.6f len=(%i-%i-%i) max=%i",
                i,nn[i],tt.diff[i],tt.diff[i]/length(tt.nn),
                l.train,l.test,length(tt.nn),
                (quantile(tt.hot0))[5]
                ))
  #print(quantile(tt.hot0))
  
}

plot(tt.diff)

rm(nn,nn.train,nn.test)
rm(l.train,l.test)
rm(tt.train,tt.test,tt.nn,tt)
rm(tt.hot,tt.hot0)

i=31
tt.hot  = table(unlist(dtrain.b1[nn[i]]),dtrain.b1$hotel_cluster)
tt.hot0 = rowSums(tt.hot)
tt.hot.n=tt.hot[,c(1:ncol(tt.hot))]/tt.hot0

tt.clust     = hclust(dist(tt.hot.n),method="ward.D")
plot(tt.clust)
tt.memb      = cutree(tt.clust,k=10) # 6-11 clusters
table(tt.memb)
plot(table(tt.memb))

centers <- lapply(sort(unique(tt.memb)),
       function(x){colMeans(tt.hot.n[tt.memb==x,c(1:ncol(tt.hot.n))])})

require(ggplot2)

tt.memb.pca = (tt.memb %in% c(1,3)) #c(1:max(tt.memb)))

pca = prcomp(tt.hot.n[c(1:nrow(tt.hot.n))[tt.memb.pca],])
tt.hot.pca = predict(pca,tt.hot.n)


g1 = ggplot(data = data.frame(pca1=tt.hot.pca[tt.memb.pca,1],
                              pca2=tt.hot.pca[tt.memb.pca,2],
                              cl=tt.memb[tt.memb.pca]),
            aes(x=pca1,y=pca2))+
     geom_jitter(aes(color=cl),alpha=0.5,fill=0.3,shape=0.2)
g1

#plot(tt.hot.pca[,1],tt.hot.pca[,2])

x=3; plot(tt.hot.pca[tt.memb==x,1],tt.hot.pca[tt.memb==x,2])

(sort(abs(pca$rotation[,1]),decreasing = TRUE))[1:10]


stop("Normal end")

#----------------------------------------------------
#image(ll)
#contour(c(1:nrow(mm)),c(1:ncol(mm)),mm,levels = seq(0.01,1.0,by=0.1))
#------------------- function

