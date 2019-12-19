*Inequality measures, Gini, Theil.
*Diversity indices Shannon & Simpson.

*Questions, email apwheele@gmail.com, Andy Wheeler

*Updated to include decomposition between subgroups.
DEFINE !Theil (Val = !TOKENS(1)
              /Group = !DEFAULT ("") !TOKENS(1) 
              /Dataset = !DEFAULT (Theil) !TOKENS(1) )
AGGREGATE OUTFILE=* MODE=ADDVARIABLES
  /BREAK !Group
  /XX_MeanVal_XX = MEAN(!Val).
COMPUTE #1 = (!Val/XX_MeanVal_XX).
DO IF !Val > 0.
  COMPUTE XX_T_XX = #1*LN(#1).
ELSE.
  COMPUTE XX_T_XX = 0.
END IF.
DATASET DECLARE !Dataset.
AGGREGATE OUTFILE=!QUOTE(!Dataset)
  /BREAK !Group
  /Theil = MEAN(XX_T_XX)
  /GroupMean = MEAN(!Val)
  /GroupSum = SUM(!Val)
  /GroupN = N.
MATCH FILES FILE = * /DROP XX_MeanVal_XX XX_T_XX.
!IF (!LENGTH(!Group) !NE 0) !THEN 
DATASET ACTIVATE !Dataset.
AGGREGATE OUTFILE=* MODE=ADDVARIABLES
  /BREAK
  /TotalSum = SUM(GroupSum)
  /TotalN = SUM(GroupN).
COMPUTE Si = GroupSum/TotalSum.
COMPUTE TotalMean = TotalSum/TotalN.
COMPUTE One = Si*Theil.
COMPUTE Two = Si*(LN(GroupMean/TotalMean)).
AGGREGATE OUTFILE=* MODE=ADDVARIABLES OVERWRITE=YES
  /BREAK
  /Within = SUM(One)
  /Between = SUM(Two).
COMPUTE GlobalTheil = Within + Between.
*If you still wants these individual parts.
*Just comment out the line below.
ADD FILES FILE = * /DROP GroupMean GroupSum GroupN TotalSum TotalN Si TotalMean One Two.
!ELSE
DATASET ACTIVATE !Dataset.
ADD FILES FILE = * /DROP GroupMean GroupSum GroupN.
!IFEND
!ENDDEFINE.

*Calculations with http://www.had2know.com/academics/gini-coefficient-calculator.html.
DEFINE !Gini (Val = !TOKENS(1)
             /Group = !DEFAULT ("") !TOKENS(1) 
             /Dataset = !DEFAULT (Gini) !TOKENS(1) )
*Compute rank.
!IF (!Group = "") !THEN
RANK VARIABLES=!Val /TIES = MEAN /RANK INTO XX_Rank_XX.
!ELSE
RANK VARIABLES=!Val BY !Group /TIES = MEAN /RANK INTO XX_Rank_XX.
!IFEND
*Calculate total n.
AGGREGATE OUTFILE=* MODE=ADDVARIABLES
  /BREAK !Group
  /XX_TotN_XX = N.
COMPUTE XX_Num_XX = (XX_TotN_XX + 1 - XX_Rank_XX)*!Val.
*Aggregate to group.
DATASET DECLARE !Dataset.
AGGREGATE OUTFILE=!QUOTE(!Dataset)
  /BREAK !Group
  /XX_Num_XX = SUM(XX_Num_XX)
  /XX_TotN_XX = FIRST(XX_TotN_XX)
  /XX_Sum_XX = SUM(!Val).
MATCH FILES FILE = * /DROP XX_TotN_XX XX_Rank_XX.
DATASET ACTIVATE !Dataset.
COMPUTE #1 = (XX_TotN_XX + 1)/XX_TotN_XX.
COMPUTE #Num = 2*XX_Num_XX.
COMPUTE #Den = XX_TotN_XX*XX_Sum_XX.
COMPUTE Gini = #1 - (#Num/#Den).
EXECUTE.
MATCH FILES FILE = * /DROP XX_TotN_XX XX_Num_XX XX_Sum_XX. 
!ENDDEFINE.

DEFINE !Shannon (Val = !TOKENS(1)
                /Group = !DEFAULT ("") !TOKENS(1) 
                /Dataset = !TOKENS(1))
AGGREGATE OUTFILE=* MODE=ADDVARIABLES
  /BREAK = !Group
  /XX_ValAgg_XX = SUM(Val).
COMPUTE #IndProp = Val/XX_ValAgg_XX.
DO IF #IndProp > 0.
  COMPUTE XX_Shannon_XX = -(#IndProp*LN(#IndProp)).
ELSE.
  COMPUTE XX_Shannon_XX = 0.
END IF.
DATASET DECLARE !Dataset.
AGGREGATE OUTFILE=!QUOTE(!Dataset)
  /BREAK = !Group
  /ShannonEnt = SUM(XX_Shannon_XX).
MATCH FILES FILE = * /DROP XX_ValAgg_XX XX_Shannon_XX.
!ENDDEFINE.
*Standard errors? http://stats.stackexchange.com/q/188869/1036.


DEFINE !Simpson (Val = !TOKENS(1)
                /Group = !DEFAULT ("") !TOKENS(1) 
                /Dataset = !TOKENS(1))
AGGREGATE OUTFILE=* MODE=ADDVARIABLES
  /BREAK = !Group
  /XX_ValAgg_XX = SUM(Val).
COMPUTE #IndProp = Val/XX_ValAgg_XX.
COMPUTE XX_Simpson_XX = #IndProp**2.
DATASET DECLARE !Dataset.
AGGREGATE OUTFILE=!QUOTE(!Dataset)
  /BREAK = !Group
  /Simpson = SUM(XX_Simpson_XX).
MATCH FILES FILE = * /DROP XX_ValAgg_XX XX_Simpson_XX.
!ENDDEFINE.


*Quick data example.
*DATA LIST FREE / Group Income.
*BEGIN DATA
*1 100
*1 100
*1 100
*2 0
*2 0
*2 1000
*3 0 
*3 0 
*3 100
*4 50
*4 150
*4 200
*END DATA.
*DATASET NAME InEq.


