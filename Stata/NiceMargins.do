**************************************************************************
*START UP STUFF

*Set the working directory and plain text log file
cd "C:\Users\axw161530\Dropbox\Documents\BLOG\Stata_NiceMargins\Analysis"

*log the results to a text file
log using "LogitModels.txt", text replace

*so the output just keeps going
set more off

*let stata know to search for a new location for stata plug ins
adopath + "C:\Users\axw161530\Documents\Stata_PlugIns\V15"
net set ado "C:\Users\axw161530\Documents\Stata_PlugIns\V15"

*In this script I use 
*net install http://www.stata-journal.com/software/sj18-3/gr0073/
*ssc install grstyle, replace
*ssc install palettes, replace
**************************************************************************

**************************************************************************
*DATA PREP

*Getting the data
import delimited CrimeStrings_withData.csv

*For dummy variables
set matsize 800

*Making the previous densities per time period
generate buff_1000_1 = buff_1000 * (7/1611)

*control variables used in the regression
global ContVars "d1 d2 d3 d4 d5 d6 d7 d8 d9 d10 d11 d12 d13 d14 d15 d16 d17 d18 whiteperc blackperc hispperc asianperc under17 propmove perpoverty perfemheadhouse perunemploy perassist i.month c.dateint"

*For here I am just examining burglary incidents 
keep if crimetype == 3
**************************************************************************

**************************************************************************
*Graph Settings
grstyle clear
set scheme s2color
grstyle init
grstyle set plain, box
grstyle color background white
grstyle set color Set1
grstyle yesno draw_major_hgrid yes
grstyle yesno draw_major_ygrid yes
grstyle color major_grid gs8
grstyle linepattern major_grid dot
grstyle set legend 4, box inside
grstyle color ci_area gs12%50
grstyle color ci_area gs12%0
**************************************************************************

**************************************************************************
*REGRESSION & MARGINSPLOTS

*I will need this later to draw the margins over the support
*Of the prior crime density
summarize buff_1000_1
global MyMin = r(min)
global MyMax = r(max)
global Grid = ($MyMax-$MyMin)/100

*Now estimate the logit model
logit future0_1000_7 i.arrest c.buff_1000_1 i.arrest#c.buff_1000_1 $ContVars

*Create the two margin plots
quietly margins arrest, at(c.buff_1000_1=($MyMin ($Grid) $MyMax))
marginsplot, recast(line) noci title("Residential Burglary, Predictive Margins") xtitle("Historical Crime Density") ytitle("Pr(Future Crime = 1)") plot1opts(lcolor(black)) plot2opts(lcolor(gs6) lpattern("--")) legend(on order(1 "no arrest" 2 "arrest")) name(main)
graph export "BurglaryMain.png", replace

quietly margins, dydx(arrest) at(c.buff_1000_1=($MyMin ($Grid) $MyMax))
marginsplot, recast(line) plot1opts(lcolor(gs8)) ciopt(color(black%20)) recastci(rarea) title("Residential Burglary, Average Marginal Effects of Arrest") xtitle("Historical Crime Density") ytitle("Effects on Pr(Future Crime)") name(diff)
graph export "BurglaryDiff.png", replace

*Now combining the plots together
graph combine main diff, xsize(6.5) ysize(2.7) iscale(.8) name(comb)
graph close main diff
graph export "BurglaryMarginPlot.png", width(6000) replace
graph close comb

*This is necessary if you want to reuse the plot names 
graph drop _all 

*Finish the script.
drop _all 
exit, clear
**************************************************************************
