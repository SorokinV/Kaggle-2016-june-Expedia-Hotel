require(plyr)
{
leak.eff=read.csv('./Result/Leak/df-LeakExt-2016-05-15-03-55.csv',stringsAsFactors = FALSE)
str(leak.eff)
#
# rules:
#
# r1    +1   -> user_location_city+orig_destination_distance
# r2    +2   -> srch_destination_id+hotel_country+hotel_market
# r3    +4   -> srch_destination_id
# r4    +8   -> hotel_country
# rTop  +16  -> top clusters
#
leak.eff$rTop <- ifelse(leak.eff$mark>=16,1,0)
leak.eff$r4   <- ifelse((leak.eff$mark%%16)>=8,1,0)
leak.eff$r3   <- ifelse(((leak.eff$mark%%16)%%8)>=4,1,0)
leak.eff$r2   <- ifelse((((leak.eff$mark%%16)%%8)%%4)>=2,1,0)
leak.eff$r1   <- ifelse(((((leak.eff$mark%%16)%%8)%%4)%%2)>=1,1,0)

#leak.mark     <- table(leak.eff$mark); leak.mark
leak.mark     <- tapply(leak.eff$mark,leak.eff$mark,length);
leak.mark.names  <- c("r...4.","r1..4.","r..34.", # 8,9,12
                      "r1.34.","r.234.","r1234.", # 13,14,15
                      "r...4T","r..34T",          # 24,28
                      "r.234T","r1234T")          # 30,31
#names(leak.mark) <- paste(leak.mark.names,names(leak.mark),sep="="); leak.mark
names(leak.mark) <- leak.mark.names;
df.leak.mark     <- data.frame(rules=as.character(names(leak.mark)),count=unlist(leak.mark))
print(arrange(df.leak.mark,rules))
print("")
leak.rules    <- colSums(leak.eff[,-c(1,2,3)]);
df.leak.rule     <- data.frame(rules=as.character(names(leak.rules)),count=unlist(leak.rules))
print(arrange(df.leak.rule,rules))
}