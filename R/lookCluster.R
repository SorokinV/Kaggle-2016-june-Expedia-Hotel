require(fastcluster)


cl.i = 9 # user_location_city


cl.x = 36 # hotel_cluster

xx = table(dtrain.b1[[35]])
plot(xx)
hist(xx)
quantile(xx); length(xx[is.na(xx)])

ll = table(dtrain.b1$hotel_market,dtrain.b1$hotel_cluster)
image(ll)
llx = rowSums(ll)
hist(llx)
plot(llx)
summary(llx)

mm = ll
mm[,c(1:ncol(ll))]=mm[,c(1:ncol(ll))]/llx

contour(c(1:nrow(mm)),c(1:ncol(mm)),mm,levels = seq(0.01,1.0,by=0.1))


#------------------- function

