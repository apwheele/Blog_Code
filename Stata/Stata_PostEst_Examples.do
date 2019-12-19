*******************************************************************.
*Andy Wheeler - any questions email apwheele@gmail.com.
*Using post-estimation stuff


*************************************************.
*Setting up the directory
cd "C:\Users\andrew.wheeler\Dropbox\Documents\BLOG\Stata_Postest"
*logging the results in a text file
log using "PostEst.txt", text replace
*So the output just keeps going
set more off
*************************************************.


*************************************************.
*Example panel data difference in differences.
use "Monthly_Sim_Data.dta", clear 

*Set the panel vars
tsset Exper Ord

*Original model
xtgee Y Exper#Post i.Month, family(poisson) corr(ar1)

*Marginsplot
margins Post#Exper, at( (base) Month )
marginsplot, recast(scatter)

*Tests for multiple variables
test 1.Exper#1.Post = (1.Exper#0.Post + 0.Exper#1.Post)

testparm i.Month

*Linear combinations
lincom 1.Exper#1.Post - 0.Exper#1.Post - 1.Exper#0.Post


*An easier way to estimate the model
xtgee Y i.Exper i.Post Exper#Post i.Month, family(poisson) corr(ar1)

nlcom exp(_b[1.Exper] + _b[1.Post]  + _b[_cons])

*This creates the observed estimates, (at January) - if you want for another month need to add to above
margins Post#Exper, at( (base) Month )
*to show it recreates margins of pre period
nlcom exp(_b[1.Exper] + _b[_cons])

*compare linear model and margins
quietly xtgee Y Exper#Post i.Month, family(gaussian) corr(ar1)
margins Post#Exp, at( (base) Month )
*marginsplot, recast(scatter)
*************************************************.

*************************************************.
*see http://www.culturalcognition.net/contact/ for motivation/data.

*This clears the prior data.
drop _all 

*grab the csv data
import delimited gelman_cup_graphic_reporting_challenge_data

*estimate a similar logit model
logit agw c.left_right##c.religiosity

*graph areas using margins - pretended -1 and 1 are the high/low religious cut-offs
quietly margins, at(left_right=(-1.6(0.1)1.6) religiosity=(-1 1))
marginsplot, xlabel(-1.6(0.4)1.6) recast(line) recastci(rarea) ciopts(color(*.8))
*do areas - https://andrewpwheeler.wordpress.com/2016/03/08/on-overlapping-error-bars-in-charts/
*******************************************************************.

**************.
*Finish the script.
drop _all 
exit, clear
**************.
