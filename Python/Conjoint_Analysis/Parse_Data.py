'''
Trying to parse the 
Wolfang survey file

https://www.icpsr.umich.edu/icpsrweb/NACJD/studies/8295/datadocumentation

Andy Wheeler
apwheele@gmail.com
'''


import pandas as pd
import os

os.chdir(r'C:\Users\andre\OneDrive\Desktop\Conjoint_WolfgangSurvey\ICPSR_08295-V1\ICPSR_08295\DS0001')

###############################################
#Prepping initial text file

#Read as one long string
#There are two files, one for 0001 is quarter 3, and 0002 is quarter 4
surv_data1 = pd.read_table('08295-0001-Data.txt',header=None,names=['blob'])
surv_data2 = pd.read_table('08295-0002-Data.txt',header=None,names=['blob'])
surv_data = pd.concat([surv_data1, surv_data2], axis=0)
print( surv_data['blob'].str.len().value_counts() ) #checking length

#Get ID and line number
surv_data['ID'] = surv_data['blob'].str[0:16]
surv_data['Line'] = "L" + surv_data['blob'].str[16]

#Reshape long to wide
wide_data = surv_data.pivot(index='ID',columns='Line').reset_index()
rename_cols = [col[1] for col in wide_data.columns.values]
rename_cols[0] = 'ID'
wide_data.columns = rename_cols

#Concat into one big string
wide_data['full_blob'] = wide_data[rename_cols[1:]].agg(''.join, axis=1)
print( wide_data['full_blob'].str.len().value_counts() ) #checking length
###############################################

###############################################
#Parsing the text file into new fields

parse_data = wide_data[['ID','full_blob']].copy()

#These go char begin/end
#Name
#Description
#Should create dictionary of value labels

var_map = [(1,2,'Sample','Control Section: Sample 3 or 5'),
(3,5,'PSU','Primary Sampling Unit: 001-999'),
(6,9,'Segment','Segment Number: 1100-6699'),
(10,10,'CD','Check Digit: 0-9'),
(11,12,'Serial','Serial Number: 01-99'),
(13,13,'Type_of_Segment','1 Address, 2 special place...'),
(14,14,'HH#','Household Number: 1-9'),
(15,16,'Line_Number','Line Number of respondent:01-20'),
(17,17,'Sequence Number of Subrecord'),
(18,20,'Blank1','B1'),
(21,21,'Land_Use','1 Urban, 2-5 Rural'),
(22,23,'Place_Size_Code','00 = under 200, 01 = 200 to 499...'),
(24,24,'Place_Description','1 Central city of an SMSA only...'),
(25,27,'Interview_Identification','A01-Z99'),
(28,28,'Blank2','B2'),
(29,30,'Record_of_Interview','01-20 actual line number'),
(31,31,'Household_noninterview_type','I -- interviewed household'),
(32,32,'Race_of_Head','1 white...'),
(33,34,'Reason_for_noninterview','Type A reason'),
(35,42,'Interview_not_obtained','01-20 line number'),
(43,43,'Blank3','B3'),
(44,44,'Household_Status','1 Same Household...'),
(45,46,'Special_Place_Recode','97 Special Place...'),
(47,47,'Tenure','1 Owned or being bought...'),
(48,48,'Blank4','B4'),
(49,50,'Type_of_Living_Quarter','01-06 housing, 07-10 other unit'),
(51,51,'Number_of_Housing','Units in structure: 5=Five-Nine...'),
(52,52,'Operate_Business','Does anyone operate a business at this address? 1=No, 2=Yes'),
(53,54,'Family_Income','01=Under $1000...'),
(55,56,'Garbage1','G1'),
(57,58,'Household_Members_Over12','01-09 actual number of members'),
(59,60,'Garbage2','G2'),
(61,62,'Garbage3','G3'),
(63,64,'Household_Members_Under12','00-09 number of members'),
(65,65,'Motor_Vehicles','4=four or more'),
(66,66,'Telephone','Use of Telephone'),
(67,68,'Family_Income','01 under $1,000'),
(69,69,'Victimization_Experience','1 not victimized'),
(70,72,'Garbage4','G4'),
(73,84,'Blank5','B5'),
(85,85,'National_Sample','?'),
(86,86,'Blank6','B6'),
(87,88,'Month_Interview','07 July...'),
(89,90,'Year_Interview','Calendar year of interview'),
(91,92,'Crime_Incidents','Crime incident reports filled 01-25'),
(93,94,'People_over18','Number of people in house 01-09'),
(95,95,'Garbage5','G5'),
(96,105,'Blank7','B7'),
(106,106,'Garbage6','G6'),
(107,108,'Blank8','B8'),
(109,110,'Sample2','Control Section: Sample 3 or 5'),
(111,113,'PSU2','Primary Sampling Unit: 001-999'),
(114,117,'Segment2','Segment Number: 1100-6699'),
(118,118,'CD2','Check Digit: 0-9'),
(119,120,'Serial2','Serial Number: 01-99'),
(121,121,'Type_of_Segment2','1 Address, 2 special place...'),
(122,122,'HH#2','Household Number: 1-9'),
(123,124,'Line_Number2','Line Number of respondent:01-20'),
(125,125,'Sequence_Number2','Seq number of subrecord'),
(126,137,'Blank9','B9'),
(138,144,'Household_Weight','three implied decimals'),
(145,145,'Type_of_Interview','1 personal...'),
(146,147,'Line_Number3','01-20'),
(148,148,'Relationship_to_Head','1 head...'),
(149,150,'Age','Age at last birthday, 12-99'),
(151,151,'Marital_Status','1 married...'),
(152,152,'Race','1 white...'),
(153,153,'Sex','1 male 2 female'),
(154,154,'Armed_Forces','1 yes 2 no'),
(155,156,'Highest_Grade','00 never attended kindergarten...'),
(157,157,'Grade_Complete','Did you complete that year, 1 yes'),
(158,158,'Live_House','Did you live in this house April 1 1970'),
(159,159,'Live_City','live in limits of city/town 1 no, 2 yes'),
(160,160,'Armed_Forces_Recent','Were you in AF on April 1, 1970'),
(161,161,'Work_Last_Week','What were you doing last week'),
(162,162,'Interview_Type','1 personal...'),
(163,167,'Blank10','B10'),
(168,168,'Job_Layoff','1 no...'),
(169,169,'Looking_Work','1 yes...'),
(170,170,'Take_Job','Any reason to not take job'),
(171,171,'Work_For','for whom did you work'),
(172,174,'Business','Industry code 017-998'),
(175,175,'Employ_Type','1 private, 2 gov...'),
(176,178,'Occupation_Code','001-992'),
(179,180,'Police_Call_3','11 rape, 12 att rape...'),
(181,182,'Police_Call_2','11 rape, 12 att rape...'),
(183,184,'Police_Call_1','11 rape, 12 att rape...'),
(185,186,'Not_Report_3','11 rape, 12 att rape...'),
(187,188,'Not_Report_2','11 rape, 12 att rape...'),
(189,190,'Not_Report_1','11 rape, 12 att rape...'),
(191,192,'Any_Work','00 no'),
(193,194,'Ethnicity','41 German...'),
(195,195,'Employ_Status_Recode','1 at work...'),
(196,197,'Blank11','B11'),
(198,204,'NSCS_Person_Weight','Three implied decimals'),
(205,205,'Garbage7','G7'),
(206,207,'Version_NSCS','01-12'),
(208,209,'Line_Number4','01-20'),
(210,212,'Interviewer_ID','A01-Z99'),
(213,213,'Type_of_Interview2','1 personal...'),
(214,214,'Else_Present_Interview','1 yes all...'),
(215,215,'Reason_NonInterview','1 Type z...'),
(216,216,'Blank12','B12'),
(217,218,'Sample3','Control Section: Sample 3 or 5'),
(219,221,'PSU3','Primary Sampling Unit: 001-999'),
(222,225,'Segment3','Segment Number: 1100-6699'),
(226,226,'CD3','Check Digit: 0-9'),
(227,228,'Serial3','Serial Number: 01-99'),
(229,229,'Type_of_Segment3','1 Address, 2 special place...'),
(230,230,'HH#3','Household Number: 1-9'),
(231,232,'Line_Number3','Line Number of respondent:01-20'),
(233,233,'Sequence_Number3','Seq number of subrecord'),
(234,234,'Blank13','B13'),
(235,240,'R1_BikeTheft','A person steals a bicycle...'),
(241,246,'R2_Robbery','A person robs a victim'),
(247,252,'R3_Truancy','A person plays hooky from school'),
(253,258,'R4_Stabs','A person stabs a victim to death'),
(259,264,'R5','Change depending on version'),
(265,270,'R6','????'),
(271,276,'R7','????'),
(277,282,'R8','????'),
(283,288,'R9','????'),
(289,294,'R10','????'),
(295,300,'R11','????'),
(301,306,'R12','????'),
(307,312,'R13','????'),
(313,318,'R14','????'),
(319,324,'R15','????'),
(325,326,'Sample4','Control Section: Sample 3 or 5'),
(327,329,'PSU4','Primary Sampling Unit: 001-999'),
(330,333,'Segment4','Segment Number: 1100-6699'),
(334,334,'CD4','Check Digit: 0-9'),
(335,336,'Serial4','Serial Number: 01-99'),
(337,337,'Type_of_Segment4','1 Address, 2 special place...'),
(338,338,'HH#4','Household Number: 1-9'),
(339,340,'Line_Number4','Line Number of respondent:01-20'),
(341,341,'Sequence_Number4','Seq number of subrecord'),
(342,342,'Blank14','B14'),
(343,348,'R16','????'),
(349,354,'R17','????'),
(355,360,'R18','????'),
(361,366,'R19','????'),
(367,372,'R20','????'),
(373,378,'R21','????'),
(379,384,'R22','????'),
(385,390,'R23','????'),
(391,396,'R24','????'),
(397,402,'R25','????'),
(403,404,'Blank14','B14'),
(405,408,'Work_Unit','Work unit'),
(409,411,'Document_Number','A seq # assiging within each...'),
(412,414,'Blank15','B15'),
(415,420,'Sequence_Number5','as it apperas on orig NSCS file'),
(421,424,'Blank16','B16'),
(425,425,'Recode_Limit','0 all of Q blank'),
(426,426,'Upper_Limit','1 no upper limit in mind'),
(427,432,'Limit_in_Q','77777 limit was blank...'),
(433,434,'Sample5','Control Section: Sample 3 or 5'),
(435,437,'PSU5','Primary Sampling Unit: 001-999'),
(438,441,'Segment5','Segment Number: 1100-6699'),
(442,442,'CD5','Check Digit: 0-9'),
(443,444,'Serial5','Serial Number: 01-99'),
(445,445,'Type_of_Segment5','1 Address, 2 special place...'),
(446,446,'HH#5','Household Number: 1-9'),
(447,448,'Line_Number5','Line Number of respondent:01-20'),
(449,449,'Sequence_Number5','Seq number of subrecord'),
(450,450,'Blank17','B17'),
(451,456,'Int_Notes1','Interview Notes'),
(457,462,'Int_Notes2','Interview Notes'),
(463,468,'Int_Notes3','Interview Notes'),
(469,469,'Flag_Change_1','Flags to indicate change, blank score not changed'),
(470,470,'Flag_Change_2','Flags to indicate change, blank score not changed'),
(471,471,'Flag_Change_3','Flags to indicate change, blank score not changed'),
(472,472,'Flag_Change_4','Flags to indicate change, blank score not changed'),
(473,473,'Flag_Change_5','Flags to indicate change, blank score not changed'),
(474,474,'Flag_Change_6','Flags to indicate change, blank score not changed'),
(475,475,'Flag_Change_7','Flags to indicate change, blank score not changed'),
(476,476,'Flag_Change_8','Flags to indicate change, blank score not changed'),
(477,477,'Flag_Change_9','Flags to indicate change, blank score not changed'),
(478,478,'Flag_Change_10','Flags to indicate change, blank score not changed'),
(479,479,'Flag_Change_11','Flags to indicate change, blank score not changed'),
(480,480,'Flag_Change_12','Flags to indicate change, blank score not changed'),
(481,481,'Flag_Change_13','Flags to indicate change, blank score not changed'),
(482,482,'Flag_Change_14','Flags to indicate change, blank score not changed'),
(483,483,'Flag_Change_15','Flags to indicate change, blank score not changed'),
(484,484,'Flag_Change_16','Flags to indicate change, blank score not changed'),
(485,485,'Flag_Change_17','Flags to indicate change, blank score not changed'),
(486,486,'Flag_Change_18','Flags to indicate change, blank score not changed'),
(487,487,'Flag_Change_19','Flags to indicate change, blank score not changed'),
(488,488,'Flag_Change_20','Flags to indicate change, blank score not changed'),
(489,489,'Flag_Change_21','Flags to indicate change, blank score not changed'),
(490,490,'Flag_Change_22','Flags to indicate change, blank score not changed'),
(491,491,'Flag_Change_23','Flags to indicate change, blank score not changed'),
(492,492,'Flag_Change_24','Flags to indicate change, blank score not changed'),
(493,504,'Weight_Theft','Weight for pre-score'),
(505,516,'Weight_Rob','Weight for pre-score'),
(517,528,'Weight_Truancy','Weight for pre-score'),
(529,540,'Weight_Stab','Weight for pre-score'),
(541,542,'Sample6','Control Section: Sample 3 or 5'),
(543,545,'PSU6','Primary Sampling Unit: 001-999'),
(546,549,'Segment6','Segment Number: 1100-6699'),
(550,550,'CD6','Check Digit: 0-9'),
(551,552,'Serial6','Serial Number: 01-99'),
(553,553,'Type_of_Segment6','1 Address, 2 special place...'),
(554,554,'HH#6','Household Number: 1-9'),
(555,556,'Line_Number6','Line Number of respondent:01-20'),
(557,557,'Sequence_Number6','Seq number of subrecord'),
(558,558,'Blank18','B18'),
(559,570,'Weight_R5','Three decimals'),
(571,582,'Weight_R6','Three decimals'),
(583,594,'Weight_R7','Three decimals'),
(595,606,'Weight_R8','Three decimals'),
(607,618,'Weight_R9','Three decimals'),
(619,630,'Weight_R10','Three decimals'),
(631,642,'Weight_R11','Three decimals'),
(643,648,'Blank19','B19'),
(649,650,'Sample7','Control Section: Sample 3 or 5'),
(651,653,'PSU7','Primary Sampling Unit: 001-999'),
(654,657,'Segment7','Segment Number: 1100-6699'),
(658,658,'CD7','Check Digit: 0-9'),
(659,660,'Serial7','Serial Number: 01-99'),
(661,661,'Type_of_Segment7','1 Address, 2 special place...'),
(662,662,'HH#7','Household Number: 1-9'),
(663,664,'Line_Number7','Line Number of respondent:01-20'),
(665,665,'Sequence_Number7','Seq number of subrecord'),
(666,666,'Blank20','The devils blank'),
(667,678,'Weight_R12','Three decimals'),
(679,690,'Weight_R13','Three decimals'),
(691,702,'Weight_R14','Three decimals'),
(703,714,'Weight_R15','Three decimals'),
(715,726,'Weight_R16','Three decimals'),
(727,738,'Weight_R17','Three decimals'),
(739,750,'Weight_R18','Three decimals'),
(751,756,'Blank21','B21'),
(757,758,'Sample8','Control Section: Sample 3 or 5'),
(759,761,'PSU8','Primary Sampling Unit: 001-999'),
(762,765,'Segment8','Segment Number: 1100-6699'),
(766,766,'CD8','Check Digit: 0-9'),
(767,768,'Serial8','Serial Number: 01-99'),
(769,769,'Type_of_Segment8','1 Address, 2 special place...'),
(770,770,'HH#8','Household Number: 1-9'),
(771,772,'Line_Number8','Line Number of respondent:01-20'),
(773,773,'Sequence_Number8','Seq number of subrecord'),
(774,774,'Blank22','B22'),
(775,786,'Weight_R19','Three decimals'),
(787,798,'Weight_R20','Three decimals'),
(799,810,'Weight_R21','Three decimals'),
(811,822,'Weight_R22','Three decimals'),
(823,834,'Weight_R23','Three decimals'),
(835,846,'Weight_R24','Three decimals'),
(847,858,'Weight_R25','Three decimals'),
(859,864,'Blank23','B23')]

var_map_df = pd.DataFrame(var_map, columns=['Beg','End','Var','Desc'])

for i in var_map:
    b_m1 = i[0] - 1
    e = i[1]
    v = i[2]
    parse_data[v] = parse_data['full_blob'].str[b_m1:e]

drop_cols = ['full_blob']
#Take out garbage and blank columns
drop_cols += ["Blank" + str(i) for i in range(1,24)]
drop_cols += ["Garbage" + str(i) for i in range(1,8)]
#Take out redundant set of id information
head_li = ['Sample','PSU','Segment','CD','Serial','Type_of_Segment','HH#','Line_Number','Sequence_Number']
drop_cols += [var + str(i) for i in range(2,9) for var in head_li]
    
parse_data.drop(columns=drop_cols, inplace=True)
    
parse_data.to_csv('NSCS_Supplement.csv',index=False)

###############################################

