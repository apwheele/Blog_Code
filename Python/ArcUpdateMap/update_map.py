'''
I use the conda environment that came with arcpro
for this, eg

conda activate "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3"
'''

import arcpy
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import os

# Set environment to a particular project
gdb = "DallasDB.gdb"
ct = "TempCrimes"
ol = "ExampleCrimes"
nc = "New Crimes"
arcpy.env.workspace = gdb
aprx = arcpy.mp.ArcGISProject("DallasExample.aprx")
dallas_map = aprx.listMaps('DallasMap')[0]
temp_layer = f"{gdb}/{ct}"

# Load in data, set as a spatial dataframe
df = pd.read_csv('DallasSample.csv') # for a real project, will prob query your RMS
df = df[['incidentnum','lon','lat']]
sdf = pd.DataFrame.spatial.from_xy(df,'lon','lat', sr=4326)

# Add the feature class to the map, note this does not like missing data
sdf.spatial.to_featureclass(location=temp_layer)
dallas_map.addDataFromPath(os.path.abspath(temp_layer)) # it wants the abs path for this

# Get the layers, copy symbology from old to new
new_layer = dallas_map.listLayers(ct)[0]
old_layer = dallas_map.listLayers(ol)[0]
old_layer.visible = False
new_layer.symbology = old_layer.symbology
new_layer.name = nc

# Add into the legend, moving to top
layout = aprx.listLayouts("DallasLayout")[0]
leg = layout.listElements("LEGEND_ELEMENT")[0]
item_di = {f.name:f for f in leg.items}
leg.moveItem(item_di['Dallas PD Divisions'], item_di[nc], move_position='BEFORE')

# Update title in layout "TitleText"
txt = layout.listElements("TEXT_ELEMENT")
txt_di = {f.name:f for f in txt}
txt_di['TitleText'].text = "New Title"
# If you need to make larger, can do
#txt_di['TitleText'].elementWidth = 2.0

# Export to high res PNG file
layout.exportToPNG("DallasUpdate.png",resolution=500)

# Cleaning up, to delete the file in geodatabase, need to remove from map
dallas_map.removeLayer(new_layer)
arcpy.management.Delete(ct)