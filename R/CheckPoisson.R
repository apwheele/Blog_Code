################################################################
#This returns a dataframe with the columns
##Int -- cells with 0, 1, 2, etc.
##Freq -- total sample size in that count
##Prop -- proportion of the sample with that integer value
##PoisD -- the proportion expected via the Poisson distribution
##Resid -- residual between Prop and PoisD
##mu -- mean of the sample
##v  -- variance of the sample [another check, should be close for Poisson
CheckPoisson <- function(counts){
   maxC <- max(counts)
   freqN <- as.data.frame(table(factor(counts,levels=0:maxC)))
   mu <- mean(counts)
   freqN$Prop <- (freqN$Freq/sum(freqN$Freq))*100
   freqN$PoisD <- dpois(0:maxC,mu)*100
   freqN$Resid <- (freqN$Prop - freqN$PoisD)
   freqN$mu <- mu
   freqN$v <- var(counts)
   freqN$Var1 <- as.numeric(as.character(freqN$Var1))
   names(freqN)[1] <- 'Int'
   return(freqN)   
}
################################################################

#Example use
lambda <- 0.2
x <- rpois(10000,lambda)
CheckPoisson(x)
#82% zeroes is not zero inflated -- expected according to Poisson!

######################
#ToDo, this for negative binomial fit
######################