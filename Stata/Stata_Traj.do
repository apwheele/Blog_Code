**************************************************************************
*START UP STUFF
*Set the working directory and plain text log file
cd "C:\Users\axw161530\Dropbox\Documents\BLOG\Posted_Stata\Stata_GroupTraj"
*log the results to a text file
log using "Stata_Traj.txt", text replace
*so the output just keeps going
set more off
*let stata know to search for a new location for stata plug ins
adopath + "C:\Users\axw161530\Documents\Stata_PlugIns"
*to install on your own in the lab it would be
net set ado "C:\Users\axw161530\Documents\Stata_PlugIns"
*previously I downloaded the plug in for Stata, https://www.andrew.cmu.edu/user/bjones/index.htm
*net from http://www.andrew.cmu.edu/user/bjones/traj
*net install traj, force
**************************************************************************

**************************************************************************
*PREPPING THE DATA

*Load in csv file
import delimited GroupTraj_Sim.csv

rename ïid id
**************************************************************************

*Need to generate a set of time variables to pass to traj, just label 1 to 10
forval i = 1/10 { 
  generate t_`i' = `i'
}

*Three group model
*all allow up to quadratic function of time for Poisson part, zero inflation is a constant parameter
traj, var(count_*) indep(t_*) model(zip) order(2 2 2) iorder(0)
trajplot

*************************************************************

*I made a function to print out summary stats
program summary_table_procTraj
    preserve
    *now lets look at the average posterior probability
	gen Mp = 0
	foreach i of varlist _traj_ProbG* {
	    replace Mp = `i' if `i' > Mp 
	}
    sort _traj_Group
    *and the odds of correct classification
    by _traj_Group: gen countG = _N
    by _traj_Group: egen groupAPP = mean(Mp)
    by _traj_Group: gen counter = _n
    gen n = groupAPP/(1 - groupAPP)
    gen p = countG/ _N
    gen d = p/(1-p)
    gen occ = n/d
    *Estimated proportion for each group
    scalar c = 0
    gen TotProb = 0
    foreach i of varlist _traj_ProbG* {
       scalar c = c + 1
       quietly summarize `i'
       replace TotProb = r(sum)/ _N if _traj_Group == c 
    }
	gen d_pp = TotProb/(1 - TotProb)
	gen occ_pp = n/d_pp
    *This displays the group number, the count per group, the average posterior probability for each group,
    *the odds of correct classification, and the observed probability of groups versus the probability 
    *based on the posterior probabilities
    list _traj_Group countG groupAPP occ occ_pp p TotProb if counter == 1
	restore
end

summary_table_procTraj

preserve

*Getting the junk from the model
ereturn list
matrix p = e(plot1)
svmat p, names(col)

*matrix b = e(b)'
*matrix p = e(plot1)
**square root on the diagonal are the standard errors
*matrix v = e(V)
**combining the two
*matrix all_coef = b,v
*matrix list all_coef
**local cnames: colnames all_coef
**local rnames: rownames all_coef
*drop _all
*svmat all_coef, names(col)

*reshape wide to long to make some graphs
preserve
reshape long count_ t_, i(id)
gen count_jit = count_ + ( 0.2*runiform()-0.1 )
graph twoway scatter count_jit t_, c(L) by(_traj_Group) msize(tiny) mcolor(gray) lwidth(vthin) lcolor(gray)

*graph on the log scale
gen count_jit2 = log(count_)
summarize count_jit2
replace count_jit2 = -0.5 if count_ == 0
replace count_jit2 = count_jit2 + ( 0.2*runiform()-0.1 )
graph twoway scatter count_jit2 t_, c(L) by(_traj_Group) msize(tiny) mcolor(gray) lwidth(vthin) lcolor(gray)
*meh this is not that informative with this data

**************.
*Finish the script.
drop _all 
exit, clear
**************.


