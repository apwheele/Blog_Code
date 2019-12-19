#This script downloads your PDF files from CiteULike
#Using selenium and the Chrome driver
#Andrew Wheeler, apwheele@gmail.com, 
#https://andrewpwheeler.wordpress.com/2019/02/28/downloading-your-pdfs-from-citeulike-using-python-and-selenium/

import selenium.webdriver
import os
import time
import csv

#Here is what you need to edit to work on your personal machine

#1 - edit in your username and password
my_user = r'????!!!!!!YourUsernameHere!!!??????'
my_pass = r'????!!!!!!YourPasswordHere!!!??????'

#2 - edit in where you want the PDF files to be downloaded to
pdf_fold = r'C:\Users\axw161530\Dropbox\Documents\CIteULikeData\PDF'

#3 - edit in where you have stored your bibtext file exported from CiteUlike
base_fold = r'C:\Users\axw161530\Dropbox\Documents\CIteULikeData'
BibFile = os.path.join(base_fold,'apwheele.bib') #your name will be different!

#4 - edit in where you have the ChromeDriver exe on your local machine
ChromeDriver = os.path.join(base_fold,'chromedriver.exe')

####################################################################
#This part reads in the bib file
#Finds the article ID and the attachments
#And exports to a CSV file

#creating index of the files I want to search
bib = open(BibFile,'r',encoding="utf8")
art_res = []
curr_id = ''
line_num = 0
test_id = 'citeulike-article-id = {'
len_test_id = len(test_id)
test_pdf = 'citeulike-attachment-'
len_test_pdf = len(test_pdf)

for line in bib:
    line_num += 1
    bl = line.strip()
    #This part identifies the numeric CiteULike ID
    art_check = bl.find(test_id)
    if art_check == 0:
        back_brack = bl.find('}')
        beg = art_check+len_test_id
        end = back_brack-1
        curr_id = bl[beg:end]
    #This part finds the PDF
    pdf_check = bl.find(test_pdf)
    if pdf_check == 0:
        first_lbrack = bl.find('{')
        first_semi = bl.find(';')
        sec_semi = bl.find(';',first_semi+1)
        pdf_name = bl[(first_lbrack+1):first_semi]
        pdf_url = bl[(first_semi+2):sec_semi]
        art_res.append( (curr_id,pdf_name,pdf_url) )

print(len(art_res)) #over 2000 pdfs I have uploaded!
#for i in art_res:
#    print(i)

#I need to save this as a csv file so you can line up PDF with Bibtext article

#General function to export nested tuples to csv
def ExpCSV(loc,head,data):
    with open(loc, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(head)
        for line in data:
            writer.writerow(line)

head_names = ('ArticleID','PDF_Name','PDF_URL')
ExpCSV(loc=pdf_fold + r'\BibPDFs.csv',head=head_names,data=art_res)
####################################################################

####################################################################
#This part opens up CiteUlike in selenium
#Signs into your account
#And then downloads your PDFs

#good intro Selenium tutorial for reference
#https://github.com/CU-ITSS/Web-Data-Scraping-S2019/blob/master/Class%2004%20-%20Selenium%2C%20Twitter%2C%20and%20Internet%20Archive/Class%2004%20-%20Selenium%2C%20Twitter%2C%20and%20Internet%20Archive.ipynb

#Setting options for selenium to download PDFs instead of opening in Chrome
#https://stackoverflow.com/a/43321346/604456
options = selenium.webdriver.ChromeOptions()
profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": pdf_fold , "download.extensions_to_open": "applications/pdf"}
options.add_experimental_option("prefs", profile)
driver = selenium.webdriver.Chrome(executable_path=ChromeDriver, options=options)

#Sign into CiteULike, https://stackoverflow.com/a/21186465/604456
driver.get('http://www.citeulike.org/login')
username = driver.find_element_by_id("username")
password = driver.find_element_by_id("password")
username.send_keys(my_user)
password.send_keys(my_pass)
driver.find_element_by_name("Submit").click()

#Now I can download a file, set to sleep 5 seconds in loop
base_cite = r'http://www.citeulike.org'
for i in art_res:
    pdf_url = base_cite + i[2]
    driver.get(pdf_url)
    time.sleep(5)
    
#note if you have PDFs with same name it will not overwrite, but do "Name(1).pdf" etc.
#Shouldn't be a problem unless saved PDFs on CiteULike with generic names
	
#This finds all elements on the page
#useful to see that it is "username" and not "Username"
#for example
#https://stackoverflow.com/a/27951084/604456
#ids = driver.find_elements_by_xpath('//*[@id]')
#for ii in ids:
#    #print ii.tag_name
#    print( ii.get_attribute('id') )   # id name as string
####################################################################