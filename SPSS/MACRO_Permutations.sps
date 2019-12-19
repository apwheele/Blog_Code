*This macro takes an input variable and appends a set of N permutations to the listed dataset.

*************.
*Var = variable you want to permutate.
*N = number of permutations.
*Base = Base string of new permutation variables
        Variables are subsequently Base1 ... BaseN.
*File = name of original data file.
*************.

DEFINE !PermData (Var = !TOKENS(1)
                 /N = !TOKENS(1)
                 /Base = !TOKENS(1) 
                 /File = !TOKENS(1) )
PRESERVE.
SET MXLOOPS=!N.
DATASET ACTIVATE !File.
COMPUTE XX_TempID_XX = $casenum.
MATRIX.
GET z /FILE = * /VARIABLES = !Var.
GET Id /FILE = * /VARIABLES = XX_TempID_XX.
COMMENT generating permutation distributions.
COMPUTE Res = MAKE(NROW(z),!N+1,0).
COMPUTE Res(:,1) = Id.
LOOP #I = 1 TO !N.
 COMPUTE zP = !PERMC(z).
 COMPUTE Res(:,#I+1) = zP.
END LOOP.
SAVE Res 
  /VARIABLES = XX_TempID_XX !CONCAT(!Base,"1") TO !CONCAT(!Base,!N)
  /OUTFILE = *.
END MATRIX.
DATASET NAME XX_TempResults_XX.
DATASET ACTIVATE !File.
MATCH FILES FILE = *
  /FILE = 'XX_TempResults_XX'
  /BY XX_TempID_XX.
DATASET CLOSE XX_TempResults_XX.
MATCH FILES FILE = * /DROP XX_TempID_XX.
RESTORE.
!ENDDEFINE.

*Permutates the order of a column vector (or rows of a matrix).
DEFINE !PERMC (!POSITIONAL !ENCLOSE("(",")") )
(!1(GRADE(UNIFORM(NROW(!1),1)),:))
!ENDDEFINE.  

*Example Use.
 * DATASET CLOSE ALL.
 * OUTPUT CLOSE ALL.
 * DATA LIST FREE /X Y.
 * BEGIN DATA
1 2
3 4
5 6
7 8
END DATA.
 * DATASET NAME Test.

 * SET MPRINT ON.
/* * !PermData Var = X N = 5 Base = Perm File = Test. */
 * SET MPRINT OFF.

