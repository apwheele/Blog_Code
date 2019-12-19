* Encoding: UTF-8.
*This macro draws groups according to a multinomial probability.
*input takes a set of numbers, and calculates a new variable G.
*inputs are normalized to the sum, so you can specify inputs that.
*sum to greater than 1, the percentages will just be i/sum(i's).
*Andy Wheeler, apwheele@gmail.com, https://andrewpwheeler.wordpress.com/

DEFINE !RandMult (!POSITIONAL = !CMDEND)
!LET !S = !HEAD(!1)
!DO !I !IN (!TAIL(!1))
  !LET !S = !CONCAT(!S," + ",!I)
!DOEND
!LET !C = "_"
!LET !P = !HEAD(!1)
COMPUTE #R = RV.UNIFORM(0,(!S)).
DO IF #R < !P.
COMPUTE G = !LENGTH(!C).
!DO !I !IN (!TAIL(!1))
!LET !P = !CONCAT(!P," + ",!I)
!LET !C = !CONCAT(!C,"_")
ELSE IF #R < (!P).
COMPUTE G = !LENGTH(!C).
!DOEND
END IF.
!LET !F = !CONCAT("F",!LENGTH(!LENGTH(!C)),".0")
FORMATS G (!F).
!ENDDEFINE.


*Example use.
 * DATASET CLOSE ALL.
 * OUTPUT CLOSE ALL.
 * SET SEED 10.
 * INPUT PROGRAM.
 * LOOP Id = 1 TO 1000000.
 * END CASE.
 * END LOOP.
 * END FILE.
 * END INPUT PROGRAM.
 * DATASET NAME Check.
 * PRESERVE.
 * SET MPRINT ON.
*Replace * with !.
*RandMult 0.1 0.2 0.7.
 * FREQ G.
*RandMult 1 2 6 1.
 * FREQ G.
 * RESTORE.
