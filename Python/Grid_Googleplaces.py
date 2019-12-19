#Code to scrape Google places data
#All you need is a 
#1 - lat/lon bounding box
#2 - a place type you are interested in
#3 - an API key

#Questions, email apwheele@gmail.com
#Andy Wheeler

import math, pyproj, urllib, json, time

#function to figure out UTM zone based on lat/lon
#see https://gis.stackexchange.com/a/13292/751
def coord_to_UTM(Lat,LongTemp):
    ZoneNumber = math.floor((LongTemp + 180)/6.0) + 1
    if ( Lat >= 56.0 and Lat < 64.0 and LongTemp >= 3.0 and LongTemp < 12.0 ):
        ZoneNumber = 32
    #Special zones for Svalbard
    if ( Lat >= 72.0 and Lat < 84.0 ):
        if  ( LongTemp >= 0.0 and LongTemp <  9.0 ): 
            ZoneNumber = 31
        elif ( LongTemp >= 9.0 and LongTemp < 21.0):
            ZoneNumber = 33
        elif (LongTemp >= 21.0 and LongTemp < 33.0 ):
            ZoneNumber = 35
        elif (LongTemp >= 33.0 and LongTemp < 42.0 ):
            ZoneNumber = 37
    return int(ZoneNumber)

#lat,lon = 32.749914, -96.833551
#print coord_to_UTM(32.749914, -96.833551 - 7)

#Function to create grid given ll [lower left]
#and ur [upper right], each should be lat/lon format
#steps are in meters, and start from lower left,
#so will spill over upper right
def build_grid(ll,ur,meters):
  #convert to a local projection based on lat/lon of middle
  mid_lat = (ll[0] + ur[0])/2.0
  mid_lon = (ll[1] + ur[1])/2.0
  utmz = coord_to_UTM(mid_lat,mid_lon)
  #do not think north/south equator matters
  p1 = pyproj.Proj(proj='latlong',datum='WGS84')
  p2 = pyproj.Proj(proj="utm",zone=utmz,datum='WGS84')
  lx,ly = pyproj.transform(p1, p2, ll[1], ll[0])
  ux,uy = pyproj.transform(p1, p2, ur[1], ur[0])
  #now with projected coordinates in meters can generate grid
  difx = ux - lx
  dify = uy - ly
  nx = int( math.ceil( difx/meters ) )
  ny = int( math.ceil( dify/meters ) )
  grid_latlon = []
  for i in range(nx+1):
      for j in range(ny+1):
          tx = lx + i*meters
          ty = ly + j*meters
          tlon, tlat = pyproj.transform(p2, p1, tx, ty)
          grid_latlon.append( (tlat,tlon) )
  return grid_latlon

#ll = [32.749914, -96.833551]
#ur = [32.819148, -96.746914]
#res = build_grid(ll,ur,1000)
#print res

#Function to scrape google data
#https://andrewpwheeler.wordpress.com/2014/05/15/using-the-google-places-api-in-python/
#if you want more than one type, it should be a comman separated string
#see supported types, https://developers.google.com/places/web-service/supported_types

def GoogPlac(lat,lng,radius,type,key):
  #making the url
  AUTH_KEY = key
  LOCATION = str(lat) + "," + str(lng)
  RADIUS = radius
  TYPE = type
  MyUrl = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
           '?location=%s'
           '&radius=%s'
           '&types=%s'
           '&sensor=false&key=%s') % (LOCATION, RADIUS, TYPE, AUTH_KEY)
  #grabbing the JSON result
  response = urllib.urlopen(MyUrl)
  jsonRaw = response.read()
  jsonData = json.loads(jsonRaw)
  return jsonData
  
#This blog post is better than mine, https://medium.com/pew-research-center-decoded/learning-about-locations-with-google-apis-377c4272c95f
#says results are limited to 20 per page and 60 total (need to check, make sure mine are not missing places)
#can make grid finer to make sure you are not missing any

#This is a helper to grab the Json data that I want in a list
def IterJson(place):
  x = ( place['name'], place['reference'], place['geometry']['location']['lat'], 
         place['geometry']['location']['lng'], place['vicinity'] )
  return x
#Might want to add in open/close times
#Pretty sure can use PlaceID to look back up other info

  
#So now we have all we need to loop over google results

MyKey = ???????????? #you need to replace this with a string of your own Maps API key
MyType = 'atm'
ll = [32.615782, -97.013317] #covering Dallas
ur = [33.025225, -96.539880] #if you want to be more efficient, do point in poly
meters = 3000
#this is to figure out the necessary radius for the circles
#to slightly overlap in my grid search
overlap = ( math.sqrt( 2.0 * math.pow(meters,2)  ) / 2 ) * 1.05
print overlap

#1 generate grid

res_grid = build_grid(ll,ur,meters)
print len(res_grid)

#2 loop over grid and stuff results in a vector

atms = []
place_ids = []
for i in res_grid:
    search = GoogPlac(lat=i[0],lng=i[1],radius=overlap,type=MyType,key=MyKey)
    if search['status'] == 'OK':
        for place in search['results']:
            x = IterJson(place)
            #only append places that are not duplicates
            if x[1] not in place_ids:
                atms.append(x)
                place_ids.append(x[1])
    time.sleep(3) #delay in seconds so dont spam servers

#atms

#3 save results to csv file

import csv, os

save_loc = r'C:\Users\axw161530\Dropbox\Documents\BLOG\CrimeGenerator_DataSources'
field_names = ('Name','PlaceID','Lat','Lon','Address')

csv_loc = os.path.join(save_loc,'Atms_Dallas.csv')
with open(csv_loc, 'wb') as af:
    writer = csv.writer(af)
    writer.writerow(field_names)
    for line in atms:
        writer.writerow(line)
