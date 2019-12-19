* Encoding: windows-1252.
*Macro to help match results after FUZZY and calculate bias reduction stats.
*Original FUZZY should be treated/control drawn from the same dataset.

*Any questions feel free to email.
*Andy Wheeler, apwheele@gmail.com.
*See this blog post for walk-through - https://andrewpwheeler.wordpress.com/2016/07/11/comparing-samples-post-matching-some-helper-functions-after-fuzzy-spss/.
*Any my blog for other info.


*Returns two new datasets.
*One contains aggregate bias reduction statistics.
*The other contains only the matched sample plus the other variables.
*specified in the command.

*Also adds in a new variable into the original dataset named "MatchedSample".
*Equals 1 if they were matched cases.

*The arguments are.
* - Dataset - the name of the dataset with the original data.
* - Case - the variable that had the original treated status (1 equals treated).
* - MatchGroup - variable naming the grouping identifier, unique to each case-control pair or set.
*                what FUZZY spits out after MATCHGROUPVAR
* - Controls - the variable(s) that identify the control cases after FUZZY 
*              what FUZZY spits out after NEWDEMANDERIDVARS (can use TO for this command).
* - MatchVars - Variable(s) that were used to match, and will calculate bias reduction for.
*                should be continuous variables with variance, will get errors if matched exactly.
* - OthVars - Other variables added to the MatchedSamples dataset - like the outcome of interest.



DEFINE !MatchedSample (Dataset = !TOKENS(1)
                      /Id = !TOKENS(1)
                      /Case = !TOKENS(1)
                      /MatchGroup = !TOKENS(1)
                      /Controls = !ENCLOSE("[","]")
                      /MatchVars = !ENCLOSE("[","]")
                      /OthVars = !DEFAULT("") !CMDEND )
OMS /SELECT ALL EXCEPT = [WARNINGS] /DESTINATION VIEWER = NO /TAG = 'NoJunk'.
DATASET ACTIVATE !Dataset.
SORT CASES BY !Id.
!LET !M_Mean = ""
!LET !M_Std = ""
!LET !M_N = ""
!DO !V !IN (!MatchVars)
  !LET !M_Mean = !CONCAT(!M_Mean," ",!V,"_mean")
  !LET !M_Std = !CONCAT(!M_Std," ",!V,"_std")
  !LET !M_N = !CONCAT(!M_N," ",!V,"_N")
!DOEND
DATASET DECLARE AggStats.
AGGREGATE OUTFILE='AggStats' /BREAK !Case /!M_Mean = MEAN(!MatchVars) /!M_Std = SD(!MatchVars) /!M_N = N(!MatchVars).
DATASET ACTIVATE !Dataset.
DATASET COPY MatchedSamples.
DATASET ACTIVATE MatchedSamples.
SELECT IF !Case = 1.
ADD FILES FILE = * /KEEP !Id !Controls !MatchGroup.
VARSTOCASES /MAKE !Id FROM !Id !Controls.
AGGREGATE OUTFILE=* MODE=ADDVARIABLES /BREAK !MatchGroup /XX_MatchN_XX = N.
SELECT IF XX_MatchN_XX > 1.
ADD FILES FILE = * /DROP XX_MatchN_XX.
SORT CASES BY !Id.
MATCH FILES FILE = * /TABLE = !Dataset /KEEP !Id !Case !MatchGroup !MatchVars !OthVars /BY !Id.
DATASET DECLARE AggStats2.
AGGREGATE OUTFILE='AggStats2' /BREAK !Case /!M_Mean = MEAN(!MatchVars) /!M_Std = SD(!MatchVars) /!M_N = N(!MatchVars).
DATASET ACTIVATE AggStats.
ADD FILES FILE = * /FILE = 'AggStats2' /IN MatchedSample.
DATASET CLOSE AggStats2.
VARSTOCASES /MAKE Mean FROM !M_Mean /MAKE Std FROM !M_Std /MAKE Ns FROM !M_N /INDEX Variable.
!LET !Counter = ""
!DO !V !IN (!MatchVars)
  !LET !Counter = !CONCAT(!Counter,"_")
  ADD VALUE LABELS Variable !LENGTH(!Counter) !QUOTE(!V).
!DOEND
VALUE LABELS MatchedSample 0 'Original Sample' 1 'Matched Sample'.
VARIABLE LABELS Mean 'Means' Std 'Standard Deviations' Ns 'Total Valid N'.
DATASET ACTIVATE MatchedSamples.
DATASET COPY MSamp2.
DATASET ACTIVATE MSamp2.
ADD FILES FILE = * /KEEP !Id !MatchGroup.
DATASET ACTIVATE !Dataset.
ADD FILES FILE = * /DROP !MatchGroup.
MATCH FILES FILE = * /TABLE = 'MSamp2' /IN MatchedSample /BY !Id.
DATASET CLOSE MSamp2.
VALUE LABELS MatchedSample 0 'Not Matched' 1 'Matched'.
FORMATS MatchedSample (F1.0).
*Now standardized bias calculations.
DATASET ACTIVATE AggStats.
SORT CASES BY Variable MatchedSample !Case.
DO IF !Case = 1.
*Test test of mean differences.
COMPUTE #MeanDiff = Mean - LAG(Mean,1).
COMPUTE #DF = (Ns - 1) + (LAG(Ns,1) - 1).
COMPUTE #SE = SQRT( (Std**2/Ns) + (LAG(Std)**2/LAG(Ns)) ).
COMPUTE T = #MeanDiff/#SE.
COMPUTE P = 1 - CDF.T(ABS(T),#DF).
COMPUTE StandBias = (100*#MeanDiff)/SQRT( (Std**2 + (LAG(Std)**2))/2 ).
IF MatchedSample = 1 BiasReduction = 100*(1 - StandBias/LAG(StandBias,2)).
END IF.
VALUE LABELS MatchedSample 0 'Original Sample' 1 'Matched Sample'
            /!Case 0 'Case' 1 'Control'.
VARIABLE LABELS T 't-test of Mean Differences'
                P 'Two tailed P-Value of t-test'
                StandBias 'Standardized Bias'
                BiasReduction 'Percent Bias Reduction'.
OMSEND TAG = 'NoJunk'.
*SUMMARIZE
  /TABLES=Variable MatchedSample !Case Ns T StandBias BiasReduction
  /FORMAT=LIST NOCASENUM TOTAL
  /TITLE='Matching Overview'
  /MISSING=VARIABLE
  /CELLS=NONE.
!ENDDEFINE.

********************************************************.
*A Working example with fuzzy.
 * DATASET CLOSE ALL.
 * OUTPUT CLOSE ALL.
 * SET SEED 10.
 * INPUT PROGRAM.
 * LOOP Id = 1 TO 2000.
 * END CASE.
 * END LOOP.
 * END FILE.
 * END INPUT PROGRAM.
 * DATASET NAME OrigData.
 * COMPUTE Male = RV.BERNOULLI(0.7).
 * COMPUTE YearsOld = RV.UNIFORM(18,40).
 * FORMATS Male (F1.0) YearsOld (F2.0).
 * DO IF Male = 1 AND YearsOld <= 28.
 *   COMPUTE Treated = RV.BERNOULLI(0.3).
 * ELSE.
 *   COMPUTE Treated = 0.
 * END IF.
 * COMPUTE #OutLogit = 0.7 + 0.5*Male - 0.05*YearsOld - 0.7*Treated.
 * COMPUTE #OutProb = 1/(1 + EXP(-#OutLogit)).
 * COMPUTE Outcome = RV.BERNOULLI(#OutProb).
 * FREQ Treated Outcome.
 * FUZZY BY=Male YearsOld SUPPLIERID=Id NEWDEMANDERIDVARS=Match1 GROUP=Treated
    EXACTPRIORITY=FALSE FUZZ=0 3 MATCHGROUPVAR=MGroup DRAWPOOLSIZE=CheckSize
/OPTIONS SAMPLEWITHREPLACEMENT=FALSE MINIMIZEMEMORY=TRUE SHUFFLE=TRUE SEED=10.
*Replace "*" with "!" at the beginning of next line to run.
*MatchedSample Dataset=OrigData Id=Id Case=Treated MatchGroup=MGroup Controls=[Match1] 
  MatchVars=[YearsOld] OthVars=Outcome Male.
*Original Comparison.
 * DATASET ACTIVATE OrigData.
 * T-TEST GROUPS=Treated(0 1) /VARIABLES=Outcome.
*Only the matched subset.
 * TEMPORARY.
 * SELECT IF MatchedSample = 1.
 * T-TEST GROUPS=Treated(0 1) /VARIABLES=Outcome.
 * EXECUTE.
********************************************************.


