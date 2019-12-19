#Data taken from this article, https://news.vice.com/en_us/article/xwvv3a/shot-by-cops
#Specifically google sheet, https://docs.google.com/spreadsheets/d/1CaOQ7FUYsGFCHEqGzA2hlfj69sx3GE9GoJ40OcqI9KY/edit#gid=1271324584
#Also see Justin's blog post, https://jnix.netlify.com/post/post2-fatality-rates/

library(ggplot2)
library(ggrepel)

MyDir <- 'C:\\Users\\axw161530\\Desktop\\Funnel_Deaths'
setwd(MyDir)

#Original incident level data
IncDat <- read.csv('ViceNews_FullOISData.csv', stringsAsFactors = FALSE)

#Aggregating to counts, getting rid of unknown
IncDat$Fatal <- trimws(IncDat$Fatal)
IncDat$DeathN <- ifelse(IncDat$Fatal=='F',1,0)
IncDat <- IncDat[IncDat$Fatal != 'U',]

#City here is a bit simpler, some are dual departments
AggDat <- aggregate(cbind(DeathN,NumberOfSubjects) ~ City,data=IncDat,FUN=sum)
AggDat$Prop <- AggDat$DeathN/AggDat$NumberOfSubjects

#Overall % and funnel bounds
tot_prop <- sum(AggDat$DeathN)/sum(AggDat$NumberOfSubjects)

#Function to return a nice data frame with the funnel
funnel_bounds <- function(pop_prop,vec_n,alpha){
	suc <- vec_n*pop_prop
	low <- qbeta(alpha/2,suc,vec_n-suc+1)
	high <- qbeta(1-alpha/2,suc+1,vec_n-suc)
	bound_df <- data.frame(pop_prop,vec_n,alpha,low,high)
	return(bound_df)
}

lev <- 0.01
lh <- funnel_bounds(pop_prop=tot_prop,vec_n=1:500,alpha=lev)
test_bound <- funnel_bounds(pop_prop=tot_prop,vec_n=AggDat$NumberOfSubjects,alpha=lev)

outside <- AggDat[AggDat$Prop < test_bound$low | AggDat$Prop > test_bound$high,]


fun <- ggplot() + 
       geom_point(data=AggDat, aes(x=NumberOfSubjects,y=Prop)) +
	   geom_line(data=lh,aes(x=vec_n,y=pop_prop)) + 
	   geom_line(data=lh,aes(x=vec_n,y=low)) + 
	   geom_line(data=lh,aes(x=vec_n,y=high)) +
	   geom_text_repel(data=outside,aes(x=NumberOfSubjects,y=Prop,label=City)) +
	   scale_y_continuous(breaks=seq(0,1,0.1)) +
	   ylab('Proportion of Deaths from OIS') + 
	   xlab('Number of OIS') +
	   theme_bw()
fun

