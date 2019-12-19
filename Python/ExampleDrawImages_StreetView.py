#This code draws images running along a street in Google street view
#Need to submit lat-lon and orientation (can calculate those in a GIS from street centerline files)
#For grabbing sidewalk, found that 40 feet between photos was a good distance to prevent repeats

import urllib, os, json

#see https://andrewpwheeler.wordpress.com/2015/12/28/using-python-to-grab-google-street-view-imagery/
#key is a global for use in the functions
key = "&key=" + "!!!!!!!!!!!!!YourAPIHere!!!!!!!!!!!!!!!!"
DownLoc = r'!!!!!!!!!!!!!WhereYouWantTheImagesDownloaded!!!!!!!!!!!!!'

#set the path that you want to download the images into

def MetaParse(MetaUrl):
    response = urllib.urlopen(MetaUrl)
    jsonRaw = response.read()
    jsonData = json.loads(jsonRaw)
    #return jsonData
    if jsonData['status'] == "OK":
        if 'date' in jsonData:
            return (jsonData['date'],jsonData['pano_id']) #sometimes it does not have a date!
        else:
            return (None,jsonData['pano_id'])
    else:
        return (None,None)

PrevImage = [] #Global list that has previous images sampled, memoization kindof		
		
def GetStreetLL(Lat,Lon,Head,File,SaveLoc):
    base = r"https://maps.googleapis.com/maps/api/streetview"
    size = r"?size=1200x800&fov=60&location="
    end = str(Lat) + "," + str(Lon) + "&heading=" + str(Head) + key
    MyUrl = base + mid + end
    fi = File + ".jpg"
    MetaUrl = base + r"/metadata" + size + end
    #print MyUrl, MetaUrl #can check out image in browser to adjust size, fov to needs
    met_lis = list(MetaParse(MetaUrl))                           #does not grab image if no date
    if (met_lis[1],Head) not in PrevImage and met_lis[0] is not None:   #PrevImage is global list
        urllib.urlretrieve(MyUrl, os.path.join(SaveLoc,fi))
        met_lis.append(fi)
        PrevImage.append((met_lis[1],Head)) #append new Pano ID to list of images
    else:
        met_lis.append(None)
    return met_lis
	
#Make an example list of tuples of lat,lon's and orientation
#Pointed toward the sidewalk - plus or minus 90 degrees to face forward/backward on street

DataList = [(40.7036043470179800,-74.0143908501053400,97.00),
            (40.7037139540670900,-74.0143727485309500,97.00),
            (40.7038235569946140,-74.0143546472568100,97.00),
            (40.7039329592712600,-74.0143365794219800,97.00),
            (40.7040422704154500,-74.0143185262956300,97.00),
            (40.7041517813782500,-74.0143004403322000,97.00),
            (40.7042611636045350,-74.0142823755611700,97.00),
            (40.7043707615693800,-74.0142642750708300,97.00)]


image_list = [] #to stuff the resulting meta-data for images
ct = 0
for i in DataList:
	ct += 1
	fi = "Image_" + str(ct)
	temp = GetStreetLL(Lat=i[0],Lon=i[1],Head=i[2],File=fi,SaveLoc=DownLoc)
	if temp[2] is not None:
		image_list.append(temp)

print image_list
	
#If you want to see what example images might look like
#See https://photos.app.goo.gl/ip9qPZJ0DZMnERus2