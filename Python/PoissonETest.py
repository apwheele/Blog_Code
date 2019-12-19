#Poisson E-test to calculate p-value for difference in two Poisson means
#See #http://www.ucs.louisiana.edu/~kxk4695/JSPI-04.pdf
#A more powerful test for comparing two Poisson means
#Krishamoorthy & Thomson, 2004, Journal of Stat Planning and Inf 119, 23-35

#Questions? email apwheele@gmail.com
#Andy Wheeler, https://andrewpwheeler.wordpress.com/

import math
from scipy.stats import poisson

#this function finds the integer for poisson
#PMF that has a density of less than eps
#where to terminate the sum
def minPMF(r,eps=1e-20):
	p = 1
	high_int = int(r) #only evaluate the right tail
	while(p > eps):
		high_int += 1
		p = poisson.pmf(high_int,mu=r)
	return high_int
#print minPMF(r=3)

#Tests the null k1/n1 = k2/n2 + d
#When d = 0, can switch k1/n1 & k2/n2 and still get the same p-value
#with d != 0 though it makes a difference
def Etest(k1,k2,n1=1,n2=1,d=0,eps=1e-20):
    nf1 = float(n1) #turn denominator into floats 
    nf2 = float(n2) #so all calculations are floats
    r1 = k1/nf1 #rate process 1
    r2 = k2/nf2 #rate process 2
    lhat = (k1 + k2)/(nf1 + nf2) - (d*nf1)/(nf1 + nf2) #average rate
    Tk = abs( (r1 - r2 - d)/math.sqrt(lhat) ) #Test statistic
    d1 = nf2*lhat
    int1 = minPMF(r=d1,eps=eps) #where to stop the sum, update to use d1
    if d==0:
        int2 = int1 #where to stop the second sum
        d2 = d1
    else:
        d2 = nf1*(lhat+d)
        int2 = minPMF(r=d2,eps=eps)
    p = 0 #accumulate density towards the p-value
    for i in range(int1+1):
        for j in range(int2+1):
            if (i+j) > 0:  #if both are zero cannot calculate Tx, as denominator rp is zero
                p1 = poisson.pmf(i,mu=d2)
                p2 = poisson.pmf(j,mu=d1)
                rp = (i + j)/(nf1 + nf2)
                Tx = abs( (i/nf1 - j/nf2 - d)/math.sqrt(rp) )
                if Tx >= Tk:
                    p += p1*p2
    return p
    

#print Etest(3,0)
#print Etest(3,0,2,2) #should be the same as if the rates were both 1
#print Etest(3,0,3,3)
#print Etest(6,0,2,1) #this actually isnt the same, lhat=2 here, whereas lhat=1.5 in earlier

#print Etest(2,6) #second example in article

#I would think these two should be the same but they arent
#Might be my error
#print Etest(6,2,d=1)
#print Etest(2,6,d=-1)
    
#I am getting some funky results for very big numbers, so only use say under 100 
