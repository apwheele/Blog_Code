*macro to take a long data format and turn it into an edge list with selected variables.
*Needs numeric Person ID, incident id does not matter.
*But the incident id + person id need to be unique, otherwise will get a data error.

*StaticVars are those that dont vary by incident level (e.g. date, offense).
*PersonVars are those that do vary by incident/person (e.g. victim/offender).

*Any questions, email apwheele@gmail.com, Andy Wheeler.

DEFINE !EdgeList (IncId = !TOKENS(1)
                 /PerId = !TOKENS(1) 
                 /StaticVars = !ENCLOSE("[","]")
                 /PerVars = !CMDEND )
DATASET COPY EdgeInfo.
DATASET ACTIVATE EdgeInfo.
MATCH FILES FILE = * /KEEP !IncId !PerId !StaticVars !PerVars.
SORT CASES BY !IncId !PerId.
DATASET COPY EdgeData.
DATASET COPY Wide.
DATASET ACTIVATE Wide.
MATCH FILES FILE = * /KEEP !IncId !PerId.
CASESTOVARS /ID = !IncId.
NUMERIC @End (F1.0).
!LET !P1 = !CONCAT(!PerId,".1").
DATASET ACTIVATE EdgeData.
MATCH FILES FILE = * /DROP !PerVars.
DO IF ($casenum = 1).
  COMPUTE OrdId = 1.
ELSE IF !IncId <> LAG(!IncId).
  COMPUTE OrdId = 1.
ELSE.
  COMPUTE OrdId = LAG(OrdId) + 1.
END IF.
MATCH FILES FILE = * /TABLE = 'Wide' /BY !IncId.
DATASET CLOSE Wide.
VECTOR v = !P1 TO @End.
LOOP #i = 1 TO NVALID(!P1 TO @End).
  IF OrdId <= #i v(#i) = $SYSMIS.
END LOOP.
VARSTOCASES /MAKE Id2 FROM !P1 TO @End.
DO IF !PerId < Id2.
  COMPUTE Id.1 = !PerId.
  COMPUTE Id.2 = Id2.
ELSE.
  COMPUTE Id.1 = Id2.
  COMPUTE Id.2 = !PerId.
END IF.
MATCH FILES FILE = * /KEEP !IncId Id.1 Id.2 !StaticVars.
DATASET ACTIVATE EdgeInfo.
MATCH FILES FILE = * /DROP !StaticVars.
RENAME VARIABLES (!PerId = Id.1).
!DO !V !IN (!PerVars)
  !LET !VNew = !CONCAT(!V,".1")
  RENAME VARIABLES (!V = !VNew).
!DOEND
DATASET ACTIVATE EdgeData.
SORT CASES BY !IncId Id.1.
MATCH FILES FILE = * /TABLE = 'EdgeInfo' /BY !IncId Id.1.
DATASET ACTIVATE EdgeInfo.
RENAME VARIABLES (Id.1 = Id.2).
!DO !V !IN (!PerVars)
  !LET !VOld = !CONCAT(!V,".1")
  !LET !VNew = !CONCAT(!V,".2")
  RENAME VARIABLES (!VOld = !VNew).
!DOEND
DATASET ACTIVATE EdgeData.
SORT CASES BY !IncId Id.2.
MATCH FILES FILE = * /TABLE = 'EdgeInfo' /BY !IncId Id.2.
DATASET CLOSE EdgeInfo.
!ENDDEFINE.

*Example use.
 * DATASET CLOSE ALL.
 * OUTPUT CLOSE ALL.
 * DATA LIST FREE / Incident PersonID X1 X2 X3 X4.
 * BEGIN DATA
1 1 1 2 1 0
1 2 1 2 1 0
1 3 1 2 3 1
2 4 3 3 0 2
2 1 3 3 3 2
3 2 3 3 2 1
3 8 2 4 3 2
3 1 2 4 3 3
3 6 2 4 1 0
END DATA.
 * DATASET NAME Orig.

 * SET MPRINT ON.
 * *EdgeList IncId = Incident PerId = PersonID StaticVars = [X1 X2] PerVars = X3 X4.
 * SET MPRINT OFF.
