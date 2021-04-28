*Macro to return data in format to make spineplot.
*For a reference on what a spineplot (or Mosaic plot) is
*see "Speaking Stata: Spineplot and their kin" Cox (2008) in The Stata Journal.

*Cat1 and Cat2 just need to be categorical variables.
*Cat1 ends up being the stacked variable, and Cat2 ends up being.
*the width variable.

*sort either sorts the categories by base size, so left-most Cat2 is the biggest 
and bottom category is the biggest (by default) - or sorts by however the variables are
coded in ascending order.
*so if you want a different sort order - you just need to recode the categories appropriately.


DEFINE !makespine (Cat1 = !TOKENS(1)
                    /Cat2 = !TOKENS(1)
					/sort = !DEFAULT ("Y") !TOKENS(1) ).
					
*Aggregate Counts to all pairwise categories.
compute Count = 1.
DATASET DECLARE spinedata.
AGGREGATE
  /OUTFILE='spinedata'
  /BREAK=!Cat1 !Cat2
  /Count = SUM(Count).
match files file = *
/drop Count.
DATASET activate spinedata.

*Aggregate Total in Cat2.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=!Cat2
  /Cat2Sum = SUM(Count).

*Compute Y proportions (Cat2).
*Sorting Y Position by max X category.
*Aggregate Total in Cat1.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=!Cat1
  /Cat1Sum = SUM(Count).
  
compute Ydens = Count/Cat2Sum.
!IF (!sort = "Y") !THEN
sort cases by !Cat2 (A) Cat1Sum (D).
!ELSE
sort cases by !Cat2 (A).
!IFEND
DO IF MISSING(lag(!Cat2)) = 1 or lag(!Cat2) <> !Cat2.
    compute Y1 = 0.
    compute Y2 = Y1 + Ydens.
ELSE IF lag(!Cat2) = !Cat2.
    compute Y1 = lag(Y2).
    compute Y2 = Y1 + Ydens.
END IF.

*Aggregate Total Overall.
compute Const = 1.
AGGREGATE
  /OUTFILE=* MODE=ADDVARIABLES
  /BREAK=Const
  /Total_Count = SUM(Count).

*Now to compute the X proportions.
compute Xdens = Cat2Sum/Total_Count.
!IF (!sort = "Y") !THEN
sort cases by !Cat1 (A) Cat2Sum (D).
!ELSE
sort cases by !Cat1 (A).
!IFEND
DO IF MISSING(lag(!Cat1)) = 1 or lag(!Cat1) <> !Cat1.
    compute X1 = 0.
    compute X2 = X1 + Xdens.
ELSE IF lag(!Cat1) = !Cat1.
    compute X1 = lag(X2).
    compute X2 = X1 + Xdens.
END IF.

*Now should be able to make similar Mosaic plots.
compute myID = $casenum.
compute Xmiddle2 = X2 - ((X2 - X1)/2).
sort cases by Xmiddle2.
do if Xmiddle2 <> lag(Xmiddle2) or $casenum = 1.
    compute Xmiddle = Xmiddle2.
else if Xmiddle2 = lag(Xmiddle2).
    compute Xmiddle = $SYSMIS.
end if.
sort cases by myID.
match files file = *
/keep !Cat1 !Cat2 Ydens Y1 Y2 X1 X2 Xdens myID Xmiddle.
exe.

!ENDDEFINE.

*Below is an example use - you will need to uncomment to run.
*Making random categorical data.
*set seed 14.
*input program.
*loop #i = 1 to 1000.
*    compute Dim1 = RV.BINOM(4,.6).
*    compute Dim2 = TRUNC(RV.UNIFORM(1,4)).
*    end case.
*end loop.
*end file.
*end input program.
*dataset name cats.
*exe.
*value labels Dim1
1 'Dim1 Cat1'
2 'Dim1 Cat2'
3 'Dim1 Cat3'
4 'Dim1 Cat4'.
*value labels Dim2
1 'Dim2 Cat1'
2 'Dim2 Cat2'
3 'Dim2 Cat3'.
*set mprint on.
*makespine Cat1 = Dim1 Cat2 = Dim2.
*Example Graph - need to just replace Cat1 and Cat2 where appropriate.
*dataset activate spinedata.
*rename variables (Dim1 = Cat1)(Dim2 = Cat2).
*GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=X2 X1 Y1 Y2 myID Cat1 Cat2 Xmiddle
  MISSING = VARIABLEWISE
  /GRAPHSPEC SOURCE=INLINE.
*BEGIN GPL
 SOURCE: s=userSource(id("graphdataset"))
 DATA: Y2=col(source(s), name("Y2"))
 DATA: Y1=col(source(s), name("Y1"))
 DATA: X2=col(source(s), name("X2"))
 DATA: X1=col(source(s), name("X1"))
 DATA: Xmiddle=col(source(s), name("Xmiddle"))
 DATA: myID=col(source(s), name("myID"), unit.category())
 DATA: Cat1=col(source(s), name("Cat1"), unit.category())
 DATA: Cat2=col(source(s), name("Cat2"), unit.category())
 TRANS: y_temp = eval(1)
 SCALE: linear(dim(2), min(0), max(1.05))
 GUIDE: axis(dim(1), label("Prop. Cat 2"))
 GUIDE: axis(dim(2), label("Prop. Cat 1"))
 ELEMENT: polygon(position(link.hull((X1 + X2)*(Y1 + Y2))), color.interior(Cat1), split(Cat2))
 ELEMENT: point(position(Xmiddle*y_temp), label(Cat2), transparency.exterior(transparency."1"))
END GPL.

*dataset activate cats.
*dataset close spinedata.
*makespine Cat1 = Dim1 Cat2 = Dim2 sort = N.
*dataset activate spinedata.
*rename variables (Dim1 = Cat1)(Dim2 = Cat2).
*GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=X2 X1 Y1 Y2 myID Cat1 Cat2 Xmiddle
  MISSING = VARIABLEWISE
  /GRAPHSPEC SOURCE=INLINE.
*BEGIN GPL
 SOURCE: s=userSource(id("graphdataset"))
 DATA: Y2=col(source(s), name("Y2"))
 DATA: Y1=col(source(s), name("Y1"))
 DATA: X2=col(source(s), name("X2"))
 DATA: X1=col(source(s), name("X1"))
 DATA: Xmiddle=col(source(s), name("Xmiddle"))
 DATA: myID=col(source(s), name("myID"), unit.category())
 DATA: Cat1=col(source(s), name("Cat1"), unit.category())
 DATA: Cat2=col(source(s), name("Cat2"), unit.category())
 TRANS: y_temp = eval(1)
 SCALE: linear(dim(2), min(0), max(1.05))
 GUIDE: axis(dim(1), label("Prop. Cat 2"))
 GUIDE: axis(dim(2), label("Prop. Cat 1"))
 ELEMENT: polygon(position(link.hull((X1 + X2)*(Y1 + Y2))), color.interior(Cat1), split(Cat2))
 ELEMENT: point(position(Xmiddle*y_temp), label(Cat2), transparency.exterior(transparency."1"))
END GPL.