#Example of checking observed versus predicted proportions in Poisson regression
#https://stats.stackexchange.com/a/292311/1036
set.seed(10)
n <- 10000
x <- rnorm(n)
l <- exp(0.1 - 0.5*x)
p <- rpois(n,l)
MyData <- data.frame(p,x)

#observed proportion per integer
obs <- as.data.frame(table(factor(MyData$p, levels=0:11)))
obs$Var1 <- as.numeric(as.character(obs$Var1))

#base Poisson model
PoisMod <- glm(p ~ x, family="poisson", data=MyData)
summary(PoisMod)
MyData$pred <- exp(predict(PoisMod))

#looping over integers and predicting integers
obs$PFreq <- NA
nrow <- length(obs$Var1)

for (i in 1:nrow){
  obs$PFreq[i] <- sum(dpois(obs$Var1[i],MyData$pred))
}

#Now calculate the observed versus predictive percentages
obs$OPerc <- obs$Freq/sum(obs$Freq)
obs$PPerc <- obs$PFreq/sum(obs$Freq) #use observed freq for denominator, as there is mass above it
obs
plot(obs$Var1,obs$OPerc,type='b', ylim=c(0,0.35))
points(obs$Var1,obs$PPerc,type='b',col='red')

#for negative binomial, see https://andrewpwheeler.wordpress.com/2014/02/17/negative-binomial-regression-and-predicted-probabilities-in-spss/