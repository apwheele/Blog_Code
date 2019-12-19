#Poisson E-test to calculate p-value for difference in two Poisson means
#See #http://www.ucs.louisiana.edu/~kxk4695/JSPI-04.pdf
#A more powerful test for comparing two Poisson means
#Krishamoorthy & Thomson, 2004, Journal of Stat Planning and Inf 119, 23-35

#Questions? email apwheele@gmail.com
#Andy Wheeler, https://andrewpwheeler.wordpress.com/

#this function finds the integer for poisson
#PMF that has a density of less than eps
#where to terminate the sum
minPMF <- function(r,eps=1e-20){
	p <- 1
	int <- trunc(r) #only evaluate right tail
	while(p > eps){
		int <- int + 1
		p <- dpois(int,r)
	}
	return(int)
}

#Tests the null k1/n1 = k2/n2 + d
#When d = 0, can switch k1/n1 & k2/n2 and still get the same p-value
#with d != 0 though it makes a difference
poisson.etest <- function(k1,k2,n1=1,n2=1,d=0,eps=1e-20){
	r1 <- k1/n1 #rate first process
	r2 <- k2/n2 #rate second process
	lhat <- (k1 + k2)/(n1 + n2) - (d*n1)/(n1 + n2) #mean rate
	Tk <- abs((r1 - r2 - d)/sqrt(lhat)) #test statistic
	d1 <- n2*lhat #updated so termination of sum did not happen too early
	d2 <- n1*(lhat+d) #problem when using lhat instead of d's
	int1 <- minPMF(r=d1,eps=eps) #where to terminate sum
	if (d==0){int2 <- int1} else {int2 <- minPMF(r=d2,eps=eps)}
	df <- expand.grid(x1 = 0:int1,x2 = 0:int2) #for really large lambdas
	df$p1 <- dpois(df$x1,d2)          #this might not fit in memory 
	df$p2 <- dpois(df$x2,d1)     
	df$rp <- (df$x1 + df$x2)/(n1 + n2)
	df$Tx <- abs((df$x1/n1 - df$x2/n2 - d))/sqrt(df$rp)
	df$I <- 1*(df$Tx >= Tk)
	df$ptot <- df$p1 * df$p2 * df$I
	return(sum(df$ptot, na.rm=TRUE)) #x1 = 0 and x2 = 0 produces nulls for Tx, rp=0
}
#Need to update for 0,0 case, which is undefined so should NOT return 0
	
###################################################################################################
#poisson.etest(3,0)
#poisson.etest(3,0,2,2)
#poisson.etest(3,0,100,100) #updated so stopping sums earlier is not a problem
#
#poisson.etest(6,2) #second example from article
#poisson.etest(2,6) #when d=0, can switch arguments and get the same p-value
#
##I would think these two should be the same but they arent
##Might be my error
#poisson.etest(6,2,d=1)
#poisson.etest(2,6,d=-1)
###################################################################################################

