'''
Getting the variables for the American
Community Survey

Andy Wheeler
'''

import pandas as pd
import re
import os

# Reading ACS data from local directories
def read_acs(template,data):
    book = pd.read_excel(template,engine='openpyxl') #needs openpyxl installed for xlsx
    var_names = list(book) #names on the header rows
    labs = book.loc[0,:].to_list() #labels on the second row
    #this rewrites duplicate 'BLANK' names, mangle dups not working for me
    n = 0
    vars2 = []
    blank = []
    for i,v in enumerate(var_names):
        if v == 'BLANK':
            bl = 'BLANK.' + str(i+1)
            vars2.append(bl)
            blank.append(bl)
        else:
            vars2.append(v)
    #check for if geo file or data file
    if vars2[1] == 'FILETYPE':
        df = pd.read_csv(data,names=vars2,index_col='LOGRECNO',
                         dtype={'FILETYPE':'object'}, encoding='latin_1')
    else:
        # FYI I have troubles with reading the txt geo file, the 
        # csv geo file no issues though
        df = pd.read_csv(data,names=vars2,index_col='LOGRECNO', encoding='latin_1')
    df.drop(columns=blank,inplace=True) #no need to keep blank columns
    lab_dict = {v:l for v,l in zip(vars2,labs)}
    return df, lab_dict

# Getting a dictionary of ACS vars and associated tables
# Given a directory of XLS files
def acs_vars(directory=None):
    #get the excel files in the directory
    excel_files = []
    for file in os.listdir(directory):
        if file.endswith(".xls") | file.endswith(".xlsx"):
            if directory:
                excel_files.append( os.path.join(directory, file) )
            else:
                excel_files.append(file)
    #getting the variables in a nice dictionaries
    lab_dict = {}
    loc_dict = {}
    for file in excel_files:
        book = pd.read_excel(file,engine='openpyxl')
        var_names = list(book) #names on the header rows
        labs = book.loc[0,:].to_list()#labels on the second row
        #now add to the overall dictionary
        for v,l in zip(var_names,labs):
            lab_dict[v] = l
            loc_dict[v] = file
    #returning the two dictionaries
    return lab_dict, loc_dict

# A reduced set of tables given variables of interest
def tables_set(var_names,tabs):
    fin_list = []
    for v in var_names:
        try:
            fin_list.append(tabs[v])
        except:
            print(f'{v} not in any table')
    fin_list = list(set(fin_list))
    return fin_list

# Matching up text table and sequence xlsx file
def match_temp(temp_dir,table_dir):
    temp_list = os.listdir(temp_dir)
    tabl_list = os.listdir(table_dir)
    fin_tabs = {}
    fin_temp = {}
    for ft in tabl_list:
        ch_nm = re.findall(r'[0-9]+', ft)
        # For the geotable
        if (len(ch_nm) == 1) & (ft[0] == 'g') & (ft.endswith('.csv')):
            fin_tabs['geo'] = ft
        elif (len(ch_nm) == 2) & (ft[0] == 'e'):
            nm_int = int(int(ch_nm[1])/1000)
            fin_tabs[str(nm_int)] = ft
    for te in temp_list:
        # Check if it is the geo file
        if not re.findall(r'GeoFileTemplate',te):
            numb = str(int(re.findall(r'[0-9]+', te)[0]))
            fin_temp[os.path.join(temp_dir,te)] = os.path.join(table_dir,fin_tabs[numb])
        else:
            fin_temp[os.path.join(temp_dir,te)] = os.path.join(table_dir,fin_tabs['geo'])
    return fin_temp            

# This grabs all the tables of interest and 
# Puts them into a final table and dict 
# Of var labels
def merge_tabs(var_names,temp_loc,tab_loc):
    tab_match = match_temp(temp_loc,tab_loc)
    labels, tables = acs_vars(temp_loc)
    if var_names is None:
        var_names = list(labels.keys())
    fin_tabs = tables_set(var_names, tables)
    print(f'There are a total of {len(fin_tabs)} tables you need to import/merge')
    keep_vars = set(var_names)
    fin_labs = {}
    all_tabs = []
    for loc_fi in fin_tabs:
        loc_tab = tab_match[loc_fi]
        rd, di = read_acs(loc_fi,loc_tab)
        overlap = list(set(list(rd)) & keep_vars)
        all_tabs.append( rd[overlap].copy() )
    res_tab = pd.concat(all_tabs, axis=1)
    allv = ['LOGRECNO'] + list(res_tab)
    fin_labs = {v:labels[v] for v in allv}
    return fin_labs, res_tab

# This function preps the data variables of interest
# num/den should be a list of equal length
# for items can either have an individual string variable
# or a list of strings to sum together for numerator/denominator
# turns into final list of names
# denominator is clipped to a value of 1, so missing data is imputed
# as 0's (if denominator=0 numerator should equal 0 as well)
def prop_prep(data, num, den, names):
    li_type = [1,2,3]
    fin_vars = []
    for n,d in zip(num,den):
        if type(n) == type(li_type):
            num_sum = data[n].sum(axis=1)
        else:
            num_sum = data[n]
        if type(d) == type(li_type):
            den_sum = data[d].sum(axis=1).clip(1)
        else:
            den_sum = data[d].clip(1)
        fin_vars.append( (num_sum/den_sum) ) #can multiply to make %
    res_df = pd.concat(fin_vars,axis=1)
    res_df.columns = names
    return res_df

base = r'C:\Users\e009156\Desktop\TexasCensus'
temp = os.path.join(base,'2019_5yr_Summary_FileTemplates')
data = os.path.join(base,'tables')

interest = ['B03001_001','B02001_005','B07001_017','B99072_001','B99072_007',
            'B11003_016','B11003_013','B14006_002','B01001_003','B23025_005',
            'B22010_002','B16002_004','GEOID','NAME']

# Variable summation
lim_english = ['B16004_007',
               'B16004_008',
               'B16004_012',
               'B16004_013',
               'B16004_017',
               'B16004_018',
               'B16004_022',
               'B16004_023',
               'B16004_029',
               'B16004_030',
               'B16004_034',
               'B16004_035',
               'B16004_039',
               'B16004_040',
               'B16004_044',
               'B16004_045',
               'B16004_051',
               'B16004_052',
               'B16004_056',
               'B16004_057',
               'B16004_061',
               'B16004_062',
               'B16004_066',
               'B16004_067']

top = ['B17010_002',['B11003_016','B11003_013'],lim_english,'B08141_002']
bot = ['B17010_001',        'B11002_001'       ,'B16004_001','B08141_001']
nam = ['PovertyFamily','SingleHeadwithKids'    ,'LimitedEnglishPop','NoCarWorkers']

interest += lim_english + bot + ['B17010_002','B11003_016','B11003_013','B08141_002']
interest = list(set(interest))

labs, comp_tabs = merge_tabs(interest,temp,data)
tr = comp_tabs['NAME'].str.find('Census Tract') == 0
#bg = comp_tabs['NAME'].str.find('Block Group') == 0
tracts = comp_tabs[ tr ].copy()

prep_sdh = prop_prep(tracts, top, bot, nam)
prep_sdh.to_csv(os.path.join(base,'SocialDet_TexCT.csv'))