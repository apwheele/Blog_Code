'''
Set of helper functions to work with folium
'''

import folium
from folium.plugins import FloatImage
import geopandas as gpd
from matplotlib.colors import rgb2hex
import os
import pandas as pd
from pylab import cm

# SVG helpers for legends

# This is for a polygon area (such as a city boundary, or a choropleth map)
def poly_svg(text="Polygon",fill="grey",fill_opacity=0.5,stroke="black",stroke_width=1,stroke_opacity=1,height=20,width=20):
    x_pts = [3,17,17,10,3]
    y_pts = [3,3 ,10,17,17]
    x_pts = [(i/20)*width for i in x_pts]
    y_pts = [(i/20)*height for i in y_pts]
    svg = '<span>\n'
    svg += f'<svg height="{height}" width="{width}">\n'
    poly_pts = " ".join([f'{x},{y}' for x,y in zip(x_pts,y_pts)])
    poly_pts = poly_pts.replace(".0 "," ").replace(".0,",",")
    svg += f'  <polygon points="{poly_pts}" fill="{fill}" fill-opacity="{fill_opacity}" '
    svg += f'stroke="{stroke}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}" />'
    svg += f'\n</svg>  {text}</span>'
    return svg

mask3 = '''    <clipPath id="shape">
      <use href="#circle1" />
      <use href="#circle2" />
      <use href="#circle3" />
    </clipPath>
    <mask id="maskC1">
      <use href="#canvas" />
      <use href="#circle2" />
      <use href="#circle3" />
    </mask>
    <mask id="maskC2">
      <use href="#canvas" />
      <use href="#circle1" />
      <use href="#circle3" />
    </mask>    
    <mask id="maskC3">
      <use href="#canvas" />
      <use href="#circle1" />
      <use href="#circle2" />
    </mask>
    <mask id="maskC2fill">
      <use href="#canvas" />
      <use href="#circle3" />
    </mask>
  </defs>\n'''


# This is for blobby hotspots, forcing to be square since based on circles
def hot_svg(text="HotSpot",fill="grey",fill_opacity=0.9,stroke="black",stroke_width=1,stroke_opacity=1,side=20):
    c1x, c1y, r1 = (6.5/20)*side, (7/20)*side, (5/20)*side
    c2x, c2y, r2 = (14/20)*side, (7/20)*side, (5/20)*side
    c3x, c3y, r3 = (12/20)*side, (12/20)*side, (5/20)*side
    svg = "<span>\n"
    svg += f'<svg width="{side}" height="{side}" xmlns="http://www.w3.org/2000/svg">\n  <defs>\n'
    svg += '    <rect id="canvas" width="100%" height="100%" fill="white" />\n'
    svg += f'    <circle id="circle1" cx="{c1x}" cy="{c1y}" r="{r1}" />\n'
    svg += f'    <circle id="circle2" cx="{c2x}" cy="{c2y}" r="{r2}" />\n'
    svg += f'    <circle id="circle3" cx="{c3x}" cy="{c3y}" r="{r3}" />\n'
    svg += mask3
    svg += f'  <use href="#circle1" stroke="none" fill="{fill}" fill-opacity="{fill_opacity}" mask="url(#maskC1)" />\n'
    svg += f'  <use href="#circle2" stroke="none" fill="{fill}" fill-opacity="{fill_opacity}" mask="url(#maskC2fill)" />\n'
    svg += f'  <use href="#circle3" stroke="none" fill="{fill}" fill-opacity="{fill_opacity}" />\n'
    svg += f'  <use href="#circle1" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" mask="url(#maskC1)"/>\n'
    svg += f'  <use href="#circle2" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" mask="url(#maskC2)"/>\n'
    svg += f'  <use href="#circle3" stroke="{stroke}" stroke-width="{stroke_width}" fill="none" mask="url(#maskC3)"/>\n'
    svg += f"</svg>  {text}</span>"
    svg = svg.replace('.0',"")
    return svg

# Creating a base folium map
def base_folium(boundary,zoom=12,weight=4,color="black",opacity=0.3, logo=False, legend_name="City Boundary"):
    b2 = boundary.copy()
    b2['area'] = boundary.geometry.area
    b2.sort_values(by='area',inplace=True,ascending=False)
    b2.reset_index(drop=True,inplace=True)
    center = b2.geometry.centroid[[0]].to_crs('EPSG:4326')[0]
    b2 = b2.to_crs('EPSG:4326')
    mapf = folium.Map(location=[center.y,center.x],
                      zoom_start=zoom,
                      control_scale= True,
                      tiles=None)
    #show=True,overlay=False
    cartodb = folium.TileLayer(tiles='cartodbpositron',name='CartoDB Positron Basemap',control=True,show=True)
    cartodb.add_to(mapf)
    osm_base = folium.TileLayer(tiles='OpenStreetMap',name='OSM Basemap',control=True)
    osm_base.add_to(mapf)
    # Add in boundary
    bound2 = b2.boundary.to_json()
    def bound_func(x):
        di = {"color":color,
              "weight": weight,
              "opacity": opacity}
        return di
    
    # This is currently not working for hex color codes
    #bound_name = f'''<span><svg width="12" height="12">
    #             <rect width="12" height="12" fill-opacity="100%" fill="white"
    #             style="stroke-width:4;stroke:{color};opacity:{opacity}" />
    #             </svg> {legend_name}</span>'''
    # May also do fill="none"
    bound_name = poly_svg(legend_name,fill="white",fill_opacity=1,stroke=color,
                          stroke_width=4,stroke_opacity=opacity)
    boundfol = folium.GeoJson(bound2, style_function=bound_func, name=bound_name, overlay=True, control=True)
    boundfol.add_to(mapf)
    # CrimeDeCoder logo
    if logo:
        fi = FloatImage("https://crimede-coder.com/images/CrimeDeCoder_Logo_Small.PNG", bottom=10, left=0.4)
        fi.add_to(mapf)
    # Layer control needs to be last
    #folium.LayerControl(collapsed=False).add_to(mapf)
    return mapf

# Adding hotspots
def add_hotspots(mapf,
                 poly_df,
                 tab_fields,
                 title = None,
                 footer = None,
                 name="Hot Spots",
                 fill="#880808",
                 edge="#8B0000",
                 opacity=0.5,
                 tab_names = ['Crime','Count']):
    poly2 = poly_df.to_crs('EPSG:4326')
    poly2['area'] = poly_df.geometry.area
    # I do this so smaller geometries are placed on the top
    poly2 = poly2.sort_values(by='area',ascending=False).reset_index(drop=True)
    #svg_name = f'''<span><svg width="12" height="12">
    #            <rect width="12" height="12" fill-opacity="{opacity}" fill="{fill}"
    #             style="stroke-width:4;stroke:{edge}" />
    #             </svg> {name}</span>
    #'''
    svg_name = hot_svg(text=name,fill=fill,fill_opacity=opacity,
                       stroke=edge,stroke_width=1.5,stroke_opacity=1)
    fg = folium.FeatureGroup(name=svg_name,overlay=True,control=True)
    def style_func(x):
        di = {"fillColor": fill,
              "fillOpacity": opacity,
              "color": edge}
        return di
    def high_func(x):
        di = {"fillColor": fill,
              "fillOpacity": 0.05,
              "color": edge,
              "weight": 4}
        return di
    for i in range(poly_df.shape[0]):
        sub_data = poly2.loc[[i]].copy()
        geo_js = sub_data.geometry.to_json()
        geo_fol = folium.GeoJson(data=geo_js,
                                 style_function=style_func,
                                 highlight_function=high_func,
                                 name=svg_name,
                                 overlay=True,
                                 control=True)
        lab_data = pd.DataFrame(sub_data[tab_fields].T.reset_index())
        lab_data.columns = tab_names
        lab_data.sort_values(by=tab_names[1],ascending=False,inplace=True)
        lab_data[tab_names[1]] = lab_data[tab_names[1]].map('{:,.0f}'.format)
        html_lab = lab_data.to_html(index=False,header=True)
        if title is not None:
            html_lab = sub_data[title][i] + html_lab
        if footer is not None:
            html_lab += sub_data[footer][i]
        popup = folium.Popup(html_lab)
        popup.add_to(geo_fol)
        geo_fol.add_to(fg)
    fg.add_to(mapf)

# This gets hex codes for a pallett
# eg get_map('Blues',5)
# or get_map('viridis',4)
def get_map(name, n):
    cmap = cm.get_cmap(name, n)
    res_hex = []
    # not sure if it matters to use 
    for i in range(cmap.N):
        hex = rgb2hex(cmap(i))
        res_hex.append(hex)
    return res_hex

# Makes a hex palette given labels
def make_palette(labs, name):
    hex_map = get_map(name, len(labs))
    res_map = {l:h for l,h in zip(labs,hex_map)}
    return res_map


# di should have {'label':'color'}
# and be in the order you want
def build_svg(di,group_name,edge='#D3D3D3',fill_opacity=0.5,edge_weight=1):
    # If edge_weight is 0, do it as 0
    if edge_weight == 0:
        loc_edge = 0
    else:
        loc_edge = 2
    fin_leg = f"<span>{group_name}"
    for lab,col in di.items():
        fin_leg += '<br><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<svg width="10" height="10">'
        fin_leg += f'<rect width="12" height="12" fill-opacity="{fill_opacity}"'
        fin_leg += f' fill="{col}" style="stroke-width:{loc_edge};stroke:{edge}" />'
        fin_leg += f'</svg> {lab}</span>'
    fin_leg += "</span>"
    return fin_leg

# Currying the style function
# https://leafletjs.com/reference.html#path-option
def style_wrap(fillColor, fillOpacity, color, weight):
    def style_func(x):
        di = {"fillColor": fillColor,
              "fillOpacity": fillOpacity,
              "color": color,
              "weight": weight}
        return di
    return style_func

# Adding Choropleth
def add_choro(mapf,
              poly_df,
              col_field,
              lab_di,
              tab_fields,
              title = None,
              footer = None,
              name="Choropleth",
              edge='#D3D3D3',
              edge_weight=1,
              opacity=0.65,
              tab_names = ['Field','Value']):
    poly2 = poly_df.to_crs('EPSG:4326')
    poly2['area'] = poly_df.geometry.area
    poly2 = poly2.sort_values(by='area',ascending=False).reset_index(drop=True)
    # creating the legend
    svg_name = build_svg(lab_di,name,edge,opacity,edge_weight)
    fg = folium.FeatureGroup(name=svg_name,overlay=True,control=True)
    # Making the necessary style functions
    sf = {}
    hf = {}
    for lab,col in lab_di.items():
        sf[lab] = style_wrap(col,opacity,edge,edge_weight)
        # highlight function
        hf[lab] = style_wrap(col,opacity*0.5,edge,4)
    # Looping over polygons, adding into map
    for i in range(poly_df.shape[0]):
        sub_data = poly2.loc[[i]].copy()
        geo_js = sub_data.geometry.to_json()
        choro_lab = sub_data[col_field][i]
        geo_fol = folium.GeoJson(data=geo_js,
                                 style_function=sf[choro_lab],
                                 highlight_function=hf[choro_lab],
                                 name=svg_name,
                                 overlay=True,
                                 control=True)
        lab_data = pd.DataFrame(sub_data[tab_fields].T.reset_index())
        lab_data.columns = tab_names
        html_lab = lab_data.to_html(index=False,header=True)
        if title is not None:
            html_lab = sub_data[title][i] + html_lab
        if footer is not None:
            html_lab += sub_data[footer][i]
        popup = folium.Popup(html_lab)
        popup.add_to(geo_fol)
        geo_fol.add_to(fg)
    fg.add_to(mapf)


# This adds crime de-coder logo
# and methods note to leaflet map

logo_js = '''
</script>
<script>var logo = '<a href="https://crimede-coder.com/" target="_blank">' +
'<svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 325.16 171.35">' +
'<defs><style>.cls-1{fill:#010101;}.cls-2{fill:none;stroke:#fff;stroke-miterlimit:10;stroke-width:3px;}' +
'.cls-3{font-size:84.54px;font-family:Helvetica-Bold,Helvetica;font-weight:700;}.cls-3,.cls-4{fill:#fff;}' +
'.cls-4{font-size:65.23px;font-family:Helvetica;}</style></defs><rect class="cls-1" width="325.16" height="171.35">' +
'</rect><rect class="cls-2" x="6.61" y="5.42" width="313.29" height="160.52"></rect>' +
'<text class="cls-3" transform="translate(15.42 77.15) scale(1.06 1)">CRIME</text>' +
'<text class="cls-4" transform="translate(15.42 141.98) scale(1.01 1)">De-Coder</text></svg>'+
'</a>'

var methods = '<p>For details on how I made this map, see ' +
'<a href="https://github.com/apwheele/Blog_Code/tree/master/Python/folium_helpers" target="_blank">' +
'Folium Helpers Github</a>.<br>Based on open data for Austin.</p>'

document.querySelector("section.leaflet-control-layers-list").insertAdjacentHTML("afterbegin",logo);
document.querySelector("div.leaflet-control-attribution").insertAdjacentHTML("afterbegin",methods);

let rad = document.querySelectorAll("input.leaflet-control-layers-selector")

// for only 2 does it for the radio buttons
// if I do it for everything, when clicking
// on or off layers appends it

for (let i = 0; i < 2; i++) {
     rad[i].addEventListener("change", add_note);
 }

function add_note() {
  document.querySelector("div.leaflet-control-attribution").insertAdjacentHTML("afterbegin",methods);
}

// making sure the first radio button is selected
// document.querySelectorAll('input[type=text]')
//rad[0].checked = true;

rad[0].click();

'''

table_css = '''<style>
/* Alternate row coloring */
tr:nth-child(even) {
  background-color: #f2f2f2;
}

/* Right align columns 2/3 */
td:nth-child(2), td:nth-child(3),
th:nth-child(2), th:nth-child(3) {
  text-align: right;
}

/* Background color of header */
th {
  background-color: #DDDDDD
}

/* No borders in Table */
table {
  border: none;
  border-collapse:collapse;
  width: 200px;
  border-bottom: none;
  border-top: none;
}

/* No vertical borders in header and cells */
table, th, td {
  border-left: none;
  border-right: none;
  border-spacing: 2%;
}

/* Cell padding */
th, td {
  padding: 0% 2% 0% 2%;
}
</style>'''

def save_map(mapf,file="temp.html",add_css=table_css,add_js=logo_js,layer=True):
    # Need to add in layercontrol at the very end
    if layer:
        folium.LayerControl(collapsed=False).add_to(mapf)
    # Adding in CSS and javascript
    css_element = folium.Element(add_css)
    js_element = folium.Element(add_js)
    mapf.get_root().header.add_child(css_element)
    # now adding in javascript at the end
    # https://github.com/python-visualization/folium/issues/86
    html = mapf.get_root()
    html.script.get_root().render()
    html.script._children['XXX_LogoJavascript'] = js_element
    mapf.save(file)