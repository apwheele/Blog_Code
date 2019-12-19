* Encoding: UTF-8.
*Macro to create funnel chart lines in SPSS.
*And to create empirical Bayes shrunk rates.

*See these two blog posts for detail, 
* 1 https://andrewpwheeler.wordpress.com/2014/10/12/using-funnel-charts-for-monitoring-rates/
* 2 https://andrewpwheeler.wordpress.com/2018/07/23/sorting-rates-using-empirical-bayes/

* Any questions, email apwheele@gmail.com
* Andy Wheeler

****************************************************************************.
*This macro makes funnel lines within the current dataset to add to funnel
*chart graphs.

*Takes as arguments:
* Num = Numerator values
* Den = Denominator values
* Perc = percent you want the funnel lines for, eg 95, 99, 99.9, etc.
* MinPop = lines will be interpolated from min pop to max pop, if no argument
* MaxPop = provided will be taken from min and max of data
* Rate = rate ratio you want to use, defaults to 100,000
* Split = variable to split the lines by.

* Returns: OverallRate, Low99, High99 (or replace number with Percentage provided).
****************************************************************************.

DEFINE !FunnelLines (Num = !TOKENS(1)
                    /Den = !TOKENS(1)
                    /Perc = !TOKENS(1) 
                    /MinPop = !DEFAULT("XX_MinPop_XX") !TOKENS(1)
                    /MaxPop = !DEFAULT("XX_MaxPop_XX") !TOKENS(1)
                    /Rate = !DEFAULT("100000") !TOKENS(1)
                    /Split = !DEFAULT("") !TOKENS(1) )
*Calculating rate.
AGGREGATE OUTFILE=* MODE=ADDVARIABLES
  /BREAK !Split
  /XX_TotNum_XX = SUM(!Num)
  /XX_TotDen_XX = SUM(!Den)
  /XX_MinPop_XX = MIN(!Den)
  /XX_MaxPop_XX = MAX(!Den)
  /XX_TotObs_XX = N.
COMPUTE OverallRate = (XX_TotNum_XX/XX_TotDen_XX)*!Rate.
COMPUTE Const = 1.
SORT CASES BY !Split !Den.
SPLIT FILE BY !Split Const.
CREATE XX_Ord_XX = CSUM(Const).
SPLIT FILE OFF.
COMPUTE #Step = ( LN(!MaxPop) - LN(!MinPop) ) / (XX_TotObs_XX-1).
COMPUTE XX_N_XX = EXP( LN(!MinPop) + XX_Ord_XX*#Step ). 
COMPUTE #Alpha = 1 - (!Perc/100).
COMPUTE #Suc = (OverallRate*XX_N_XX)/!Rate.
!LET !L = !CONCAT("Low",!Perc)
!LET !H = !CONCAT("High",!Perc)
COMPUTE !L = IDF.BETA(#Alpha/2,#Suc,XX_N_XX-#Suc+1)*!Rate.
COMPUTE !H = IDF.BETA(1-#Alpha/2,#Suc+1,XX_N_XX-#Suc)*!Rate.
COMPUTE FunnelN = XX_N_XX.
ADD FILES FILE = * /DROP XX_TotNum_XX XX_TotDen_XX XX_MinPop_XX XX_MaxPop_XX 
XX_TotObs_XX XX_Ord_XX XX_N_XX Const.
!ENDDEFINE.

****************************************************************************.
*SPSS function to do empirical bayes smoothing.
*See formulas in http://www.dpi.inpe.br/gilberto/tutorials/software/geoda/tutorials/w6_rates_slides.pdf.

*Takes as arguments:
* Num = Numerator values
* Den = Denominator values
* Out = Shrunken Rate

* Returns: Out 
****************************************************************************.

DEFINE !ShrunkRate (Num = !TOKENS(1)
                   /Den = !TOKENS(1)
                   /Out = !TOKENS(1) )
  COMPUTE Const = 1.
  AGGREGATE OUTFILE=* MODE=ADDVARIABLES
    /BREAK = Const
    /k = N
    /SumNum = SUM(!Num)
    /SumDen = SUM(!Den).
  COMPUTE mu = SumNum/SumDen.
  COMPUTE ObsRate = !Num/!Den.
  COMPUTE v = !Den*( (ObsRate-mu)**2 ).
  COMPUTE Pav = SumDen/k.
  AGGREGATE OUTFILE=* MODE=ADDVARIABLES OVERWRITE=YES
    /BREAK = Const
	/v = SUM(v).
  COMPUTE v = (v / SumDen) - (mu/Pav).
  COMPUTE W = v / (v + (mu/!Den) ).
  COMPUTE !Out = W*ObsRate + (1 - W)*mu.
  ADD FILES FILE = * /DROP Const k SumNum SumDen mu ObsRate v Pav W.
!ENDDEFINE.	



****************************************************************************.
*Example use.
 * DATASET CLOSE ALL.
 * OUTPUT CLOSE ALL.

 * DATA LIST LIST (",") /OrigRank (F3.0) OrigRate (F5.2) City (A40) State (A2) Pop2010 (F8.0) OIS (F5.0) Lat (F9.4) Lon (F9.4).
 * BEGIN DATA
1,36.3,St. Louis,MO,319294,116,38.6357,-90.2446
2,28.1,Orlando,FL,238300,67,28.4166,-81.2736
3,25.5,Las Vegas,NV,583756,149,36.2292,-115.2601
4,25.2,San Bernardino,CA,209924,53,34.1416,-117.2936
5,24.8,Miami,FL,399457,99,25.7752,-80.2086
6,20.2,Kansas City,MO,459787,93,39.1251,-94.5510
7,20.1,Bakersfield,CA,347483,70,35.3212,-119.0183
8,19.9,Tulsa,OK,391906,78,36.1279,-95.9023
9,19.2,Tucson,AZ,520116,100,32.1531,-110.8706
10,19,Atlanta,GA,420003,80,33.7629,-84.4227
11,18.1,Albuquerque,NM,545852,99,35.1056,-106.6474
12,18,Fresno,CA,494665,89,36.7836,-119.7934
13,16.9,Oklahoma City,OK,579999,98,35.4671,-97.5137
14,16.6,Baltimore,MD,620961,103,39.3000,-76.6105
15,16.5,Birmingham,AL,212237,35,33.5274,-86.7990
16,15.8,Stockton,CA,291707,46,37.9763,-121.3133
17,15.2,Newark,NJ,277140,42,40.7242,-74.1726
18,15.1,Cleveland,OH,396815,60,41.4785,-81.6794
19,15.1,Oakland,CA,390724,59,37.7698,-122.2257
20,14.5,New Orleans,LA,343829,50,30.0534,-89.9345
21,14.4,Norfolk,VA,242803,35,36.9230,-76.2446
22,14.2,Reno,NV,225221,32,39.5491,-119.8499
24,13.7,Denver,CO,600158,82,39.7619,-104.8811
23,13.7,Houston,TX,2100263,288,29.7866,-95.3909
25,13.5,Baton Rouge,LA,229493,31,30.4422,-91.1309
26,13.4,Long Beach,CA,462257,62,33.8092,-118.1553
27,12.9,Phoenix,AZ,1445632,187,33.5722,-112.0901
28,12.8,Pittsburgh,PA,305704,39,40.4398,-79.9766
30,12.5,Columbus,OH,787033,98,39.9852,-82.9848
29,12.5,Mesa,AZ,439041,55,33.4019,-111.7174
31,11.8,Cincinnati,OH,296943,35,39.1402,-84.5058
32,11.7,Philadelphia,PA,1526006,179,40.0094,-75.1333
33,11.6,Jacksonville,FL,821784,95,30.3369,-81.6616
34,11.5,Omaha,NE,408958,47,41.2644,-96.0451
35,11.3,Memphis,TN,646889,73,35.1028,-89.9774
36,11.2,Detroit,MI,713777,80,42.3830,-83.1022
37,11.2,Riverside,CA,303871,34,33.9381,-117.3932
38,10.8,Aurora,CO,325078,35,39.6880,-104.6897
39,10.7,Tampa,FL,335709,36,27.9701,-82.4797
40,10.6,St. Petersburg,FL,244769,26,27.7620,-82.6441
41,10.2,Santa Ana,CA,324528,33,33.7363,-117.8830
42,10.1,Chicago,IL,2695598,272,41.8376,-87.6818
43,10,Washington,DC,601723,60,38.9041,-77.0172
44,9.9,Fort Wayne,IN,253691,25,41.0882,-85.1439
45,9.6,Milwaukee,WI,594833,57,43.0633,-87.9667
46,9.5,Anaheim,CA,336265,32,33.8555,-117.7601
47,9.4,Sacramento,CA,466488,44,38.5666,-121.4686
48,9.2,Scottsdale,AZ,217385,20,33.6843,-111.8611
49,9.1,St. Paul,MN,285068,26,44.9489,-93.1041
51,9,Dallas,TX,1197816,108,32.7933,-96.7665
50,9,Seattle,WA,608660,55,47.6205,-122.3509
52,8.9,Anchorage,AK,291826,26,61.1743,-149.2843
53,8.9,Colorado Springs,CO,416427,37,38.8673,-104.7607
54,8.7,San Antonio,TX,1327407,116,29.4724,-98.5251
55,8.2,Portland,OR,583776,48,45.5370,-122.6500
56,8.1,Wichita,KS,382368,31,37.6907,-97.3459
57,8,Indianapolis,IN,820445,66,39.7767,-86.1459
58,8,Louisville,KY,597337,48,38.1654,-85.6474
60,7.8,Boise,ID,205671,16,43.6002,-116.2317
61,7.8,Henderson,NV,257729,20,36.0097,-115.0357
59,7.8,Los Angeles,CA,3792621,296,34.0194,-118.4108
62,7.7,Madison,WI,233209,18,43.0878,-89.4299
63,7.6,San Diego,CA,1307402,99,32.8153,-117.1350
64,7.4,Durham,NC,228330,17,35.9811,-78.9029
65,7.4,Lubbock,TX,229573,17,33.5656,-101.8867
66,7.4,North Las Vegas,NV,216961,16,36.2857,-115.0939
67,7.2,Chesapeake,VA,222209,16,36.6794,-76.3018
69,7.1,Glendale,AZ,226721,16,33.5331,-112.1899
68,7.1,San Francisco,CA,805235,57,37.7272,-123.0322
70,7,Fremont,CA,214089,15,37.4945,-121.9412
72,6.6,Garland,TX,226876,15,32.9098,-96.6303
71,6.6,Toledo,OH,287208,19,41.6641,-83.5819
73,6.3,Minneapolis,MN,382578,24,44.9633,-93.2683
75,6.2,Austin,TX,790390,49,30.3039,-97.7544
74,6.2,Corpus Christi,TX,305215,19,27.7543,-97.1734
76,6.1,Fort Worth,TX,741206,45,32.7815,-97.3467
77,5.4,El Paso,TX,649121,35,31.8484,-106.4270
78,5.1,Laredo,TX,236091,12,27.5604,-99.4892
79,5.1,San Jose,CA,945942,48,37.2967,-121.8189
80,5,Nashville,TN,601222,30,36.1718,-86.7850
81,4.9,Charlotte,NC,731424,36,35.2078,-80.8310
82,4.8,Jersey City,NJ,247597,12,40.7114,-74.0648
83,4.7,Chandler,AZ,236123,11,33.2829,-111.8549
84,4.5,Hialeah,FL,224669,10,25.8699,-80.3029
85,4.2,Irving,TX,216290,9,32.8577,-96.9700
86,4.1,Greensboro,NC,269666,11,36.0951,-79.8270
87,3.9,Lincoln,NE,258379,10,40.8105,-96.6803
88,3.8,Arlington,TX,365438,14,32.7007,-97.1247
89,3.8,Buffalo,NY,261310,10,42.8925,-78.8597
90,3.7,Virginia Beach,VA,437994,16,36.7800,-76.0252
91,3.6,Honolulu,HI,337256,12,21.3243,-157.8476
92,3.3,Chula Vista,CA,243916,8,32.6277,-117.0152
94,3,Lexington,KY,295803,9,38.0407,-84.4583
93,3,Winston-Salem,NC,229617,7,36.1027,-80.2610
95,2.4,Irvine,CA,212375,5,33.6784,-117.7713
96,2.3,Boston,MA,617594,14,42.3320,-71.0202
97,2.2,Raleigh,NC,403892,9,35.8306,-78.6418
98,1.4,Gilbert,AZ,208453,3,33.3103,-111.7431
99,1.2,Plano,TX,259841,3,33.0508,-96.7479
100,0.2,New York,NY,8175133,16,40.6635,-73.9387
END DATA.
 * DATASET NAME OISRates.


*Calculating the shrunk rates - replace * with ! to run.
 * *ShrunkRate Num = OIS Den = Pop2010 Out = ShrunkRate.
*Putting back on the 100,000 scale.
 * COMPUTE ShrunkRate = ShrunkRate*100000.

*Creating funnel chart - replace * with ! to run.
 * *FunnelLines Num = OIS Den = Pop2010 Perc = 99.
 * FORMATS OrigRate OverallRate Low99 High99 (F2.0) Pop2010 FunnelN (F8.0).
 * EXECUTE.
 * GGRAPH
  /GRAPHDATASET NAME="graphdataset" VARIABLES=Pop2010 OrigRate OverallRate Low99 High99 FunnelN
  /GRAPHSPEC SOURCE=INLINE.
 * BEGIN GPL
  SOURCE: s=userSource(id("graphdataset"))
  DATA: Pop2010=col(source(s), name("Pop2010"))
  DATA: OrigRate=col(source(s), name("OrigRate"))
  DATA: FunnelN=col(source(s), name("FunnelN"))
  DATA: OverallRate=col(source(s), name("OverallRate"))
  DATA: Low99=col(source(s), name("Low99"))
  DATA: High99=col(source(s), name("High99"))
  GUIDE: axis(dim(1), label("Population 2010"))
  GUIDE: axis(dim(2), label("OIS Rate Per 100,000"))
  SCALE: log(dim(1))
  ELEMENT: line(position(FunnelN*OverallRate), size(size."1"))
  ELEMENT: line(position(FunnelN*Low99), size(size."1"))
  ELEMENT: line(position(FunnelN*High99), size(size."1"))
  ELEMENT: point(position(Pop2010*OrigRate))
END GPL.
****************************************************************************.
