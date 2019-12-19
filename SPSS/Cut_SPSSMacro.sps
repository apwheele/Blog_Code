* Encoding: UTF-8.
*These are bins where the left is closed and the right is open (exceptions end points).
DEFINE !LBins (Var = !TOKENS(1)
             /Out = !TOKENS(1)
             /Cuts = !CMDEND ) 
!LET !Base = ""
!LET !Lag = !HEAD(!Cuts)
IF !Var < !Lag !Out = 0.
!LET !Lab = !QUOTE(!CONCAT("< ",!Lag))
ADD VALUE LABELS !Out 0 !Lab.
!DO !I !IN (!TAIL(!Cuts))
  !LET !Base = !CONCAT(!Base,"_")
  IF !Var >= !Lag AND !Var < !I !Out = !LENGTH(!Base).
  !LET !Lab = !QUOTE(!CONCAT("[",!Lag,"-",!I,")"))
  ADD VALUE LABELS !Out !LENGTH(!Base) !Lab.
  !LET !Lag = !I
!DOEND
!LET !Base = !CONCAT(!Base,"_")
IF !Var >= !Lag !Out = !LENGTH(!Base).
ADD VALUE LABELS !Out !LENGTH(!Base) !QUOTE(!CONCAT(">= ",!Lag)).
FORMATS !Out !CONCAT("(F",!LENGTH(!LENGTH(!Base)),".0)").
!ENDDEFINE.

*These are bins where the right is closed and the left is open (exceptions end points).
DEFINE !RBins (Var = !TOKENS(1)
             /Out = !TOKENS(1)
             /Cuts = !CMDEND ) 
!LET !Base = ""
!LET !Lag = !HEAD(!Cuts)
IF !Var <= !Lag !Out = 0.
!LET !Lab = !QUOTE(!CONCAT("<= ",!Lag))
ADD VALUE LABELS !Out 0 !Lab.
!DO !I !IN (!TAIL(!Cuts))
  !LET !Base = !CONCAT(!Base,"_")
  IF !Var > !Lag AND !Var <= !I !Out = !LENGTH(!Base).
  !LET !Lab = !QUOTE(!CONCAT("(",!Lag,"-",!I,"]"))
  ADD VALUE LABELS !Out !LENGTH(!Base) !Lab.
  !LET !Lag = !I
!DOEND
!LET !Base = !CONCAT(!Base,"_")
IF !Var > !Lag !Out = !LENGTH(!Base).
ADD VALUE LABELS !Out !LENGTH(!Base) !QUOTE(!CONCAT("> ",!Lag)).
FORMATS !Out !CONCAT("(F",!LENGTH(!LENGTH(!Base)),".0)").
!ENDDEFINE.

*EXAMPLE USE.
 * DATA LIST FREE / X.
 * BEGIN DATA
1.5
5.0
3.1
2.6
4.5
9.1
END DATA.
 * DATASET NAME Test.
*LBins Var = X Out = LC Cuts = 1 3 5 8.
*RBins Var = X Out = RC Cuts = 1 3 5 8.
 * PRINT /X LC RC.
 * EXECUTE.