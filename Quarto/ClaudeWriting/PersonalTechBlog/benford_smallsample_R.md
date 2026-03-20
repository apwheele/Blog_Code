<!---
Using the exact reference distribution for small sample Benford tests
-->

I recently came across another potential application related to my [testing small samples](https://andrewpwheeler.wordpress.com/2015/12/17/testing-day-of-week-crime-randomness-paper-published/) for randomness in day-of-week patterns. Testing digit frequencies for [Benford's law](https://en.wikipedia.org/wiki/Benford%27s_law) basically works on the same principles as my day-of-week bins. So here I will show an example in R. 

First, download my functions [here](https://github.com/apwheele/ExactDistR/blob/master/Exact_Dist.R) and save them to your local machine. The only library dependency for this code to work is the `partitions` library, so install that. Now for the code, you can source my functions and load the `partitions` library. The second part of the code shows how to generate the null distribution for Benford's digits -- the idea is that lower digits will have a higher probability of occurring.

    #Example using small sample tests for Benfords law
    library(partitions)
	#switch to wherever you downloaded the functions to your local machine
    source("C:\\Users\\axw161530\\Dropbox\\PublicCode_Git\\ExactDist\\Exact_Dist.R")
    
    f <- 1:9
    p_fd <- log10(1 + (1/f)) #first digit probabilities
	
And so if you do `cbind(f,p_fd)` at the console it prints out:

          f       p_fd
     [1,] 1 0.30103000
     [2,] 2 0.17609126
     [3,] 3 0.12493874
     [4,] 4 0.09691001
     [5,] 5 0.07918125
     [6,] 6 0.06694679
     [7,] 7 0.05799195
     [8,] 8 0.05115252
     [9,] 9 0.04575749

So we expect over 30% of the first digits to be 1's, just under 18% to be 2's, etc. To show how we can use this for small samples, I take an example of fraudulent checks from Mark Nigrini's book, *Digital Analysis using Benford's law* (I can't find a google books link to this older one -- it is the 2000 one published by Global Audit Press I took the numbers from).

    #check data from Nigrini page 84
    checks <- c(1927.48,
               27902.31,
               86241.90,
               72117.46,
               81321.75,
               97473.96,
               93249.11,
               89658.17,
               87776.89,
               92105.83,
               79949.16,
               87602.93,
               96879.27,
               91806.47,
               84991.67,
               90831.83,
               93766.67,
               88338.72,
               94639.49,
               83709.28,
               96412.21,
               88432.86,
               71552.16)
    
    #extracting the first digits
    fd <- substr(format(checks,trim=TRUE),1,1)
    tot <- table(factor(fd, levels=paste(f)))

Now Nigrini says this is too small of a sample to perform actual statistical tests, so he just looks at it at face value. If you print out the `tot` object you will see that we have mostly upper values in the series, three 7's, nine 8's, and nine 9's.

    > tot
    
    1 2 3 4 5 6 7 8 9 
    1 1 0 0 0 0 3 9 9 
	
Now, my work on small samples for day-of-week crime sprees showed that given reasonably expected offender behavior, you only needed as few as 8 crimes to have pretty good power to test for randomness in the series. So given that I would expect the check series of 23 is not totally impossible to detect significant deviations from the null Benford's distribution. But first we need to figure out if I can actually generate the exact distribution for 23 digits in 9 bins in memory.

    m <- length(tot)
    n <- sum(tot)
    choose(m+n-1,m-1)
	
Which prints out just under 8 million, `[1] 7888725`. So we should be able to hold that in memory.

So now comes the actual test, and as my comment says this takes a few minutes for R to figure out -- so feel free to go get a coffee.

    #Takes a few minutes
    resG <- SmallSampTest(d=tot,p=p_fd,type="G")
    resG
	
Here I use the [likelihood ratio G test](https://en.wikipedia.org/wiki/G-test) instead of the more usual Chi-Square test, as I found that always had more power in the day-of-the-week paper. From our print out of `resG` we subsequently get:

    > resG
    Small Sample Test Object 
    Test Type is G 
    Statistic is 73.4505062784174 
    p-value is:  2.319579e-14  
    Data are:  1 1 0 0 0 0 3 9 9 
    Null probabilities are:  0.3 0.18 0.12 0.097 0.079 0.067 0.058 0.051 0.046 
    Total permutations are:  7888725 
	
So since the p-value is incredibly small, we would reject the null that the first digit distribution of these checks follows Benford's law. So on its face we can reject the null with this dataset, but it would take more investigation in general to give recommendations of how many observations in practice you would need before you can reasonably even use the small sample distribution. I have code that allows you to test the power given an alternative distribution in those functions, so for a quick and quite conservative test I see the power if the alternative distribution were uniform instead of Benford's with our 23 observations. The idea is if people make up numbers uniformly instead of according to Benford's law, what is the probability we would catch them with 23 observations. I label this as conservative, because I doubt people even do a good job of making them uniform -- most number fudging cases will be much more egregious I imagine.

    #power under null of equal probability
    p_alt <- rep(1/8,8)
    PowUni <- PowAlt(SST=resG,p_alt=p_alt) #again takes a few minutes
    PowUni

So based on that we get a power estimate of:

    > PowUni
    Power for Small Sample Test 
    Test statistic is: G  
    Power is: 21.34428  
    Null is: 0.3 0.18 0.12 0.097 0.079 0.067 0.058 0.051 0.046  
    Alt is: 0.12 0.12 0.12 0.12 0.12 0.12 0.12 0.12  
    Alpha is: 0.05  
    Number of Bins: 9  
    Number of Observations: 23
	
Only 21. Since you want to aim for ~80, this shows that you are not likely to uncover more subtle patterns of manipulation with this few of observations. The power would go up for more realistic deviations though -- so I don't think this idea is totally dead in the water.

If you are like me and find it annoying to wait for a few minutes to get the results, a quick and dirty way to make the test go faster is to collapse bins that have zero observations. So our first digits have zero observations in the 3,4,5 and 6 bins. So I collapse those and do the test with only 6 bins, which makes the results return in around ~10 seconds instead of a few minutes. Note that collapsing bins is better suited for the G or the Chi-Square test, because the KS test or Kuiper's test the order of the observations matter.

    #Smaller subset
    UpProb <- c(p_fd[c(1,2,7,8,9)],sum(p_fd[c(3,4,5,6)]))
    ZeroAdd <- c(table(fd),0)
    
    resSmall <- SmallSampTest(d=ZeroAdd,p=UpProb,type="G")
    resSmall
	
When you do this for the G and the Chi-square test you will get the same test statistics, but in this example the p-value is larger (but is still quite small).

    > resSmall
    Small Sample Test Object 
    Test Type is G 
    Statistic is 73.4505062784174 
    p-value is:  1.527991e-15  
    Data are:  1 1 3 9 9 0 
    Null probabilities are:  0.3 0.18 0.058 0.051 0.046 0.37 
    Total permutations are:  98280  
   
I can't say for sure the behavior of the tests when collapsing categories, but I think it is reasonable offhand, especially if you have some substantive reason to collapse them before looking at the data.

In practice, they way I expect this would work is not just for testing one individual, but as a way to prioritize audits of many individuals. Say you had a large company, and you wanted to check the invoices for 1,000's of managers, but each manager may only have 20 some invoices. You would compute this test for each manager then, and then subsequently rank them by the p-values (or do some correction like the [false-discovery-rate](https://en.wikipedia.org/wiki/False_discovery_rate)) for further scrutiny. That takes a bit more work to code that up efficiently than what I have here though. Like I may pre-compute the exact CDF's for each test statistic, aggregate them alittle so they fit in memory, and then check the test against the relevant CDF.

But feel free to bug me if you want to use this idea in your own work and want some help implementing it.

--------------------------------------

For some additional examples, here is some code to get the second digit expected probabilities: 

    #second digit probabilities
    s <- 0:9
    x <- expand.grid(f*10,s)
    x$end <- log10(1 + (1/(x[,1]+x[,2])))
    p_sd <- aggregate(end ~ Var2, data=x, sum)
    p_sd

which are expected to be much more uniform than the first digits:	
	
    > p_sd
       Var2        end
    1     0 0.11967927
    2     1 0.11389010
    3     2 0.10882150
    4     3 0.10432956
    5     4 0.10030820
    6     5 0.09667724
    7     6 0.09337474
    8     7 0.09035199
    9     8 0.08757005
    10    9 0.08499735

And we can subsequently also test the check sample for deviation from Benford's law in the second digits. Here I show an example of using the exact distribution for the Chi-Square test. (There may be reasonable arguments for using Kuiper's test with digits as well, and the Kolmogorov-Smirnov test would apply as well, but you need to make sure the bins are in the correct order to conduct those tests.) To speed up the computation I only test the first 18 checks.

    #second digits test for sample checks, but with smaller subset
    sd <- substr(format(checks[1:18],trim=TRUE),2,2)
    tot_sd <- table(factor(sd, levels=paste(s)))
    resK_2 <- SmallSampTest(d=tot_sd,p=p_sd,type="Chi")
    resK_2

And the test results are:

    > resK_2
    Small Sample Test Object 
    Test Type is KS 
    Statistic is 0.222222222222222 
    p-value is:  0.7603276  
    Data are:  1 2 2 2 1 0 2 4 1 3 
    Null probabilities are:  0.12 0.11 0.11 0.1 0.1 0.097 0.093 0.09 0.088 0.085 
    Total permutations are:  4686825 

So for the second digits of our checks we would fail to reject the null that the data follow Benford's distribution.

The final example I will give is with another small example dataset -- the last 12 purchases on my credit card. 

    #My last 12 purchases on credit card
    purch <- c( 72.00,
               328.36,
    		    11.57,
    		    90.80,
    		    21.47,
    		     7.31,
    		     9.99,
    		     2.78,
    		    10.17,
    		     2.96,
    		    27.92,
    		    14.49)
    #artificial numbers, 72.00 is parking at DFW, 9.99 is Netflix	
	
In reality, digits can deviate from Benford's law for reasons that do not have to do with fraud -- such as artificial constraints to the system. But, when I test this set of values, I fail to reject the null that they follow Benford's distribution, 

    fdP <- substr(format(purch,trim=TRUE),1,1)
    totP <- table(factor(fdP, levels=paste(f)))
    
    resG_P <- SmallSampTest(d=totP,p=p_fd,type="G")
    resG_P
	
So for a quick test the first digits of my credit card purchases do approximately follow Benford's law.
	
    > resG_P
    Small Sample Test Object 
    Test Type is G 
    Statistic is 12.5740089945434 
    p-value is:  0.1469451  
    Data are:  3 4 1 0 0 0 2 0 2 
    Null probabilities are:  0.3 0.18 0.12 0.097 0.079 0.067 0.058 0.051 0.046 
    Total permutations are:  125970  