from bs4 import BeautifulSoup
import urllib, os

myfolder = r'C:\Users\axw161530\Dropbox\Documents\BLOG\Scrape_Methlabs\PDFs' #local folder to download stuff
base_url = r'https://www.dea.gov/clan-lab' #online site with PDFs for meth lab seizures
                                           #see https://www.dea.gov/clan-lab/clan-lab.shtml
state_ab = ['al','ak','az','ar','ca','co','ct','de','fl','ga','guam','hi','id','il','in','ia','ks',
            'ky','la','me','md','ma','mi','mn','ms','mo','mt','ne','nv','nh','nj','nm','ny','nc','nd',
			'oh','ok','or','pa','ri','sc','sd','tn','tx','ut','vt','va','wa','wv','wi','wy','wdc']
			
state_name = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Guam','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas',
              'Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey',
			  'New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas',
			  'Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming','Washington DC']

all_data = [] #this is the list that the tuple data will be stashed in

#Function to parse the xml and return the line by line data I want
def ParseXML(soup_xml,state):
    data_parse = []
    page_count = 1
    pgs = soup_xml.find_all('page')
    for i in pgs:
        txt = i.find_all('text')
        order = 1
        for j in txt:
            value = j.get_text() #text
            top = j['top']
            left = j['left']
            dat_tup = (state,page_count,order,top,left,value)
            data_parse.append(dat_tup)
            order += 1
        page_count += 1
    return data_parse

#This loops over the pdfs, downloads them, turns them to xml via pdftohtml command line tool
#Then extracts the data

for a,b in zip(state_ab,state_name):
    #Download pdf
    url = base_url + r'/' + a + '.pdf'
    file_loc = os.path.join(myfolder,a)
    #print url, file_loc + '.pdf'
    urllib.urlretrieve(url,file_loc + '.pdf')
    #Turn to xml with pdftohtml, does not need xml on end
    cmd = 'pdftohtml -xml ' + file_loc + ".pdf " + file_loc
    os.system(cmd)
    #parse with BeautifulSoup
    MyFeed = open(file_loc + '.xml')
    textFeed = MyFeed.read()
    FeedParse = BeautifulSoup(textFeed,'xml')
    MyFeed.close()
    #Extract the data elements
    state_data = ParseXML(soup_xml=FeedParse,state=b)
    all_data = all_data + state_data

#only takes about 3 minutes to download and parse all of the files

print len(all_data)
for i in all_data[7000:7100]:
    print i

#Tuple goes
#State, page, order within page, vertical top, horizontal left, cell value

#Now need to parse the data, will do in SPSS

#import pdfquery
#To use pdfquery for the same ends
#pdf = pdfquery.PDFQuery(r'C:\Users\axw161530\Dropbox\Documents\BLOG\Scrape_Methlabs\ky.pdf')
#pdf.load()
#pdf.tree.write(r'C:\Users\axw161530\Dropbox\Documents\BLOG\Scrape_Methlabs\ky.txt', pretty_print=True)

