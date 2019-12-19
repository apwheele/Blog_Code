*MACRO TO CREATE restricted cubic splines.
*EITHER TAKES input of knot locations or a number of knots (and defaults to calc them at particular quantiles).
*For restricted cubic splines, you need a minimum of 3 knot locations.
*RETURNS VARIABLES that are spline basis, splinex1, splinex2 etc. (will always be 2 less the number of knots).
*I normalize the spline variables by dividing by the range of the knots squared.
*These, along with the original x variable can then be entered as independent variables in regression equations.

*Andy Wheeler, apwheele@gmail.com, https://andrewpwheeler.wordpress.com/,

DEFINE !rcs (x = !TOKENS(1)
                    /n = !TOKENS(1)
                    /loc = !ENCLOSE("[","]") 
                    /group = !DEFAULT ("") !TOKENS(1)).

*********************************************************************************.
*If you only pass n and no loc, knot locations will be determined by quantiles.
*group only makes sense if you only specify n and not locations.
*Default quantiles are
*n |
*3 |.1 .5 .9
*4 |.05 .35 .65 .95
*5 |.05 .275 .5 .725 .95
*6 |.05 .23 .41 .59 .77 .95
*7 |.025 .1833 .3417 .5 .6583 .8167 .975

!IF (!loc = !NULL) !THEN

*Defining sets of quantiles.
!IF (!n = 3) !THEN
!LET !quant = ".1 .5 .9"
!IFEND
!IF (!n = 4) !THEN
!LET !quant = ".05 .35 .65 .95"
!IFEND
!IF (!n = 5) !THEN
!LET !quant = ".05 .275 .5 .725 .95"
!IFEND
!IF (!n = 6) !THEN
!LET !quant = ".05 .23 .41 .59 .77 .95"
!IFEND
!IF (!n = 7) !THEN
!LET !quant = ".025 .1833 .3417 .5 .6583 .8167 .975"
!IFEND

!LET !KnotE = !CONCAT("Knot",!n)
*Compute fractional rank.
compute const = 1.
compute x2 = !x + RV.NORMAL(0,0.000000001).
RANK
  VARIABLES=x2 (A) BY const !group /RFRACTION /PRINT=NO
  /TIES=CONDENSE.
sort cases by !group x2.
vector Knot(!n).
do repeat Knot = Knot1 to !KnotE / quant = !UNQUOTE(!quant) .
if lag(Rx2) < quant and Rx2 >= quant Knot = !x.
end repeat.
*now aggregate.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES OVERWRITEVARS=YES
  /BREAK=const !group
  /Knot1 to !KnotE = FIRST(Knot1 to !KnotE).
match files file = * /drop Rx2 const x2.
!LET !beg = !NULL
!DO !i = 1 !TO !n
!LET !beg = !CONCAT(" ",!beg)
!DOEND
!LET !k = !LENGTH(!beg)
!LET !k_1 = !LENGTH(!SUBSTR(!beg,2))
!LET !k_2 = !LENGTH(!SUBSTR(!beg,3))
vector Knot = Knot1 to !KnotE.
!IFEND
*********************************************************************************.

*********************************************************************************.
*If you pass the location of the knots in the loc token, n will be ignored.
!IF (!loc <> !NULL) !THEN
!LET !beg = !NULL
!DO !i !IN (!loc)
!LET !beg = !CONCAT(" ",!beg)
!DOEND
!LET !k = !LENGTH(!beg)
!LET !k_1 = !LENGTH(!SUBSTR(!beg,2))
!LET !k_2 = !LENGTH(!SUBSTR(!beg,3))

*this computes the vector for the knots.
!LET !KnotE = !CONCAT("Knot",!k)
vector Knot(!k).
do repeat Knot = Knot1 to !KnotE /loc = !loc.
    compute Knot = loc.
end repeat.
!IFEND
*********************************************************************************.

*Now making the splines.
vector splinex(!k_2).
*vector Knot = Knot1 to !KnotE.
loop #i = 1 to !k_2.
*Constants.
compute #t = Knot(#i).
compute #denom = Knot(!k) - Knot(!k_1).
compute #n1 = (Knot(!k) - #t)/#denom.
compute #n2 = (Knot(!k) - #t)/#denom.
*Determining values above or below zero.
compute #part1 = 0.
compute #part2 = 0.
compute #part3 = 0.
if !x > #t #part1 = (!x - #t)**3.
if !x > Knot(!k_1) #part2 = ((!x - Knot(!k_1))**3)*#n1.
if !x > Knot(!k) #part3 = ((!x - Knot(!k))**3)*#n2.
*Normalizing.
compute #norm = (Knot(!k) - Knot(1))**2.
*Making Values.
compute splinex(#i) = (#part1 - #part2 + #part3)/#norm.
end loop.
*Clean Up.
match files file = *
/drop Knot1 to !KnotE.
exe.
!ENDDEFINE.


*******************************************************************************************************************************************************.
*Example of there use - data example taken from http://www-01.ibm.com/support/docview.wss?uid=swg21476694.
*dataset close ALL.
*output close ALL.
*SET SEED = 2000000.
*INPUT PROGRAM.
*LOOP xa = 1 TO 35.
*LOOP rep = 1 TO 3.
*LEAVE xa.
*END case.
*END LOOP.
*END LOOP.
*END file.
*END INPUT PROGRAM.
*EXECUTE.
* EXAMPLE 1.
*COMPUTE y1=3 + 3*xa + normal(2).
*IF (xa gt 15) y1=y1 - 4*(xa-15).
*IF (xa gt 25) y1=y1 + 2*(xa-25).
*GRAPH
*/SCATTERPLOT(BIVAR)=xa WITH y1.
*Make spline basis.
*set mprint on.
*rcs x = xa n = 4.
*Estimate regression equation.
*REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10) CIN(95)
  /NOORIGIN
  /DEPENDENT y1
  /METHOD=ENTER xa  /METHOD=ENTER splinex1 splinex2
  /SAVE PRED ICIN .
*formats y1 xa PRE_1 LICI_1 UICI_1 (F2.0).
*Now I can plot the observed, predicted, and the intervals.
*GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=xa y1 PRE_1 LICI_1 UICI_1
  /GRAPHSPEC SOURCE=INLINE.
*BEGIN GPL
 SOURCE: s=userSource(id("graphdataset"))
 DATA: xa=col(source(s), name("xa"))
 DATA: y1=col(source(s), name("y1"))
 DATA: PRE_1=col(source(s), name("PRE_1"))
 DATA: LICI_1=col(source(s), name("LICI_1"))
 DATA: UICI_1=col(source(s), name("UICI_1"))
 GUIDE: axis(dim(1), label("xa"))
 GUIDE: axis(dim(2), label("y1"))
 ELEMENT: area.difference(position(region.spread.range(xa*(LICI_1+UICI_1))), color.interior(color.lightgrey), transparency.interior(transparency."0.5"))
 ELEMENT: point(position(xa*y1))
 ELEMENT: line(position(xa*PRE_1), color(color.red))
END GPL.
*Can make the splines at known knot locations.
*match files file = *
/drop splinex1 to UICI_1.

*For restricted cubic splines, you need a minimum of three knots.
*rcs x = xa loc = [10 20 30]. 
*Estimate regression equation.
*REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA
  /CRITERIA=PIN(.05) POUT(.10) CIN(95)
  /NOORIGIN
  /DEPENDENT y1
  /METHOD=ENTER xa  /METHOD=ENTER splinex1
  /SAVE PRED ICIN .
*formats y1 xa PRE_1 LICI_1 UICI_1 (F2.0).
*Now I can plot the observed, predicted, and the intervals.
*GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=xa y1 PRE_1 LICI_1 UICI_1
  /GRAPHSPEC SOURCE=INLINE.
*BEGIN GPL
 SOURCE: s=userSource(id("graphdataset"))
 DATA: xa=col(source(s), name("xa"))
 DATA: y1=col(source(s), name("y1"))
 DATA: PRE_1=col(source(s), name("PRE_1"))
 DATA: LICI_1=col(source(s), name("LICI_1"))
 DATA: UICI_1=col(source(s), name("UICI_1"))
 GUIDE: axis(dim(1), label("xa"))
 GUIDE: axis(dim(2), label("y1"))
 ELEMENT: area.difference(position(region.spread.range(xa*(LICI_1+UICI_1))), color.interior(color.lightgrey), transparency.interior(transparency."0.5"))
 ELEMENT: point(position(xa*y1))
 ELEMENT: line(position(xa*PRE_1), color(color.red))
END GPL.
*******************************************************************************************************************************************************.

