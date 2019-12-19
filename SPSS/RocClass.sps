*****************************************************.
*This syntax calculates the sensitivity and specificity for a classifier and a target.
*Useful for drawing ROC curves to compare multiple classifiers, or seeing what values of the classifier.
*Correspond to what values of sensitivity or specificity.
*Or calculate precision-recall curves - http://stats.stackexchange.com/q/7207/1036.
*****************************************************.

*Class - should be a numeric classifier - higher values = higher prob of target.
*Target - the outcome variable you are trying to predict, must be coded as 0-1 with 1 being the positive class.
*Suf    - the procedure returns three variables, "Sens[Suf]", "Spec[Suf]" and "Prec[Suf]"where you supply the suffix string.
*       - Sens is the sensitivity, and Spec is the specificity, and Prec is the precision.


DEFINE !Roc (Class = !TOKENS(1)
            /Target = !TOKENS(1)
            /Suf = !TOKENS(1) )
*Overall Number of cases, positive cases, and negative cases.
COMPUTE Const = 1.
AGGREGATE OUTFILE=* MODE=ADDVARIABLES
  /BREAK = Const
  /Total = N
  /TotalP = SUM(!Target).
COMPUTE TotalN = Total - TotalP.
*Calculating sensitivity.
SORT CASES BY !Class (D) !Target (D).
CREATE TP = CSUM(!Target).
*COMPUTE FN = TotalP - TP.
COMPUTE !CONCAT("Sens",!UNQUOTE(!Suf)) = TP/TotalP.
*Calculating specificity.
COMPUTE Op = (!Target = 0).
CREATE FP = CSUM(Op).
COMPUTE TN = TotalN - FP.
COMPUTE !CONCAT("Spec",!UNQUOTE(!Suf)) = TN/TotalN.
*Calculating precision.
COMPUTE !CONCAT("Prec",!UNQUOTE(!Suf)) = TP/(TP + FP).
*Getting rid of extra variables.
MATCH FILES FILE = * /DROP Const Total TotalP TotalN TP Op FP TN.
*Formats for charts.
FORMATS !CONCAT("Spec",!UNQUOTE(!Suf)) !CONCAT("Sens",!UNQUOTE(!Suf)) !CONCAT("Prec",!UNQUOTE(!Suf)) (F2.1).
EXECUTE.
*Note if you want False Negative (FN), True Negative (TN), False Positive (FP), etc. 
*can easily edit to provide these.
!ENDDEFINE.


*Example use.
 * DATASET CLOSE ALL.
 * OUTPUT CLOSE ALL.
 * SET SEED 10.
 * INPUT PROGRAM.
 * LOOP #i = 20 TO 70.
 *   COMPUTE X = #i + RV.UNIFORM(-10,10).
 *   COMPUTE R = RV.NORMAL(45,10).
 *   COMPUTE Out = RV.BERNOULLI(#i/100).
 *   END CASE.
 * END LOOP.
 * END FILE.
 * END INPUT PROGRAM.
 * DATASET NAME RocTest.
 * DATASET ACTIVATE RocTest.
 * EXECUTE.

 * SET MPRINT ON.
 * *Roc Class = X Target = Out Suf = "_X".
 * *Roc Class = R Target = Out Suf = "_R".
 * SET MPRINT OFF.
*Now make a plot with both classifiers on it, technically dont need smooth step, coin flip for ties etc.
 * GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=Spec_X Sens_X Spec_R Sens_R 
  /GRAPHSPEC SOURCE=INLINE.
 * BEGIN GPL
  PAGE: begin(scale(770px,600px))
  SOURCE: s=userSource(id("graphdataset"))
  DATA: Spec_X=col(source(s), name("Spec_X"))
  DATA: Sens_X=col(source(s), name("Sens_X"))
  DATA: Spec_R=col(source(s), name("Spec_R"))
  DATA: Sens_R=col(source(s), name("Sens_R"))
  TRANS: o = eval(0)
  TRANS: e = eval(1)
  TRANS: SpecM_X = eval(1 - Spec_X)
  TRANS: SpecM_R = eval(1 - Spec_R) 
  COORD: rect(dim(1,2), sameRatio())
  GUIDE: axis(dim(1), label("1 - Specificity"), delta(0.1))
  GUIDE: axis(dim(2), label("Sensitivity"), delta(0.1))
  GUIDE: text.title(label("ROC Curve"))
  SCALE: linear(dim(1), min(0), max(1))
  SCALE: linear(dim(2), min(0), max(1))
  ELEMENT: edge(position((o*o)+(e*e)), color(color.lightgrey))
  ELEMENT: line(position(smooth.step.right((o*o)+(SpecM_R*Sens_R)+(e*e))), color("R"))
  ELEMENT: line(position(smooth.step.right((o*o)+(SpecM_X*Sens_X)+(e*e))), color("X"))
  PAGE: end()
END GPL.

*Compare to SPSS's ROC command.
 * ROC R X BY Out (1)
  /PLOT CURVE(REFERENCE)
  /PRINT SE COORDINATES.
*COORDINATES do not seem to be evaluated at the datapoints, SPSS must interpolate.

*Now make precision recall curves.
*To make these plots, need to reshape and sort correctly, so the path follows correctly.
 * VARSTOCASES
  /MAKE Sens FROM Sens_R Sens_X
  /MAKE Prec FROM Prec_R Prec_X
  /MAKE Spec FROM Spec_R Spec_X
  /INDEX Type.
 * VALUE LABELS Type
 1 'R'
 2 'X'.
 * SORT CASES BY Sens (A) Prec (D).
 * GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=Sens Prec Type
  /GRAPHSPEC SOURCE=INLINE.
 * BEGIN GPL
  PAGE: begin(scale(770px,600px))
  SOURCE: s=userSource(id("graphdataset"))
  DATA: Sens=col(source(s), name("Sens"))
  DATA: Prec=col(source(s), name("Prec"))
  DATA: Type=col(source(s), name("Type"), unit.category())
  COORD: rect(dim(1,2), sameRatio())
  GUIDE: axis(dim(1), label("Recall"), delta(0.1))
  GUIDE: axis(dim(2), label("Precision"), delta(0.1))
  GUIDE: text.title(label("Precision-Recall Curve"))
  SCALE: linear(dim(1), min(0), max(1))
  SCALE: linear(dim(2), min(0), max(1))
  ELEMENT: path(position(Sens*Prec), color(Type))
  PAGE: end()
END GPL.
*The sawtooth is typical.



