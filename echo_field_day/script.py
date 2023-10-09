from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import folium
import gpxpy.gpx
import os

#helper functions
def get_geotagging(exif):
    if not exif:
        raise ValueError("No EXIF metadata found")

    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                raise ValueError("No EXIF geotagging found")

            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]

    return geotagging

def get_coordinates(geotags):
    lat = geotags['GPSLatitude']
    lon = geotags['GPSLongitude']

    lat = (lat[0] + lat[1] / 60 + lat[2] / 3600) * (1 if geotags['GPSLatitudeRef'] == 'N' else -1)
    lon = (lon[0] + lon[1] / 60 + lon[2] / 3600) * (1 if geotags['GPSLongitudeRef'] == 'E' else -1)

    return lat, lon

#load tracks
with open("echo_field_day/tracks.gpx", "r") as gpx_file:
    gpx = gpxpy.parse(gpx_file)
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(tuple([point.latitude, point.longitude]))


# Load images and extract coordinates
folder_path = "/Users/tadhglooramcoinmetrics/Harvard/g2_sem1/VIS-2128/echo_field_day/images/"
image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
coordinates = []

for image_file in image_files:
    with Image.open(os.path.join(folder_path, image_file)) as img:
        exif = img._getexif()
        geotags = get_geotagging(exif)
        coordinates.append((get_coordinates(geotags),image_file))
# titles for images
descriptions = {
        "IMG-2711.jpg" : ["Charles Street Meeting House","Built in 1807, the Charles Street Meeting House in Beacon Hill once hosted anti-slavery figures like Frederick Douglass and Harriet Tubman and is now used for commercial purposes."],
        "IMG-2712.jpg" : ["Louisburg Square","Designed in the 1840s, Louisburg Square is a prestigious Boston address, privately owned and featuring statues donated in 1850; notable residents have included Louisa May Alcott and Senator John Kerry."],
        "IMG-2713.jpg" : ["Nichol House Museum","Constructed in 1805, the Nichols House Museum showcases the lifestyle of the American upper class from 1885 to 1960, named after resident Rose Standish Nichols,"],
        "IMG-2714.jpg": ["Acorn Street","Acorn, one of the city's most photographed streets, transports visitors to colonial Boston, once home to 19th-century artisans."],
        "IMG-2715.jpg": ["Ashburton Park","Ashburton Park, located beside the Massachusetts State House, was formed from land created by Beacon Hill's 19th-century excavation and had its borders set during the capitol's 1890s extension, stretching between Bowdoin, Mount Vernon, and Derne Streets."],
        "IMG-2716.jpg": ["Boston Athenaeum","Founded in 1807, the Boston Athenaeum is one of the U.S.'s oldest libraries, requiring membership for full access but welcoming the public to its first floor, which features an art gallery, historical artifacts and more!"]
}

# Base folium plot Visualize with Folium
m = folium.Map(location=[42.3562, -71.0694], zoom_start=17,tiles='cartodbpositron')  # Initial map centered on Boston

# # Add new base layer
# folium.TileLayer(f'cartodbpositron').add_to(m)

# Add GPX track as a polyline
folium.PolyLine(points, color="#9e6b90", weight=3, opacity=1).add_to(m)

# plot symboles for location visited and images as pop ups
for coord, image_file in coordinates:
    title = descriptions[image_file][0]
    description = descriptions[image_file][1]
    popup_content = f'''
    <div style="text-align:center; font-weight:bold; font-size:15px; font-family: 'Optima', sans-serif;">
        {title}
    </div>
    <div style="width:400px;">
        <img src="{os.path.join(folder_path, image_file)}" width="400">
        <div style="text-align:left; font-size:12px; font-family: 'Optima', sans-serif;">
            {description}
        </div>
    </div>
    '''

    popup = folium.Popup(popup_content, max_width=2650)
    folium.Marker(
        location=coord,
        popup=popup,
        icon=folium.CustomIcon(icon_image="./echo_field_day/location.png", icon_size=(30,30))
    ).add_to(m)


loc = 'Sunday Walk in Beacon Hill'
subtitle = "Click on the icons to see photos and descriptions of the sights!"

title_html = '''
             <h3 align="center" style="background-color: #9e6b90; color: white; font-weight:bold; font-family: 'Optima', sans-serif; padding: 10px; text-align: center; font-size: 24px;"><b>{}</b></h3>
             <h4 align="center" style="background-color: white; color: black; font-family: 'Optima', sans-serif; padding: 5px; text-align: center; font-size: 15px;">{}</h4>
             '''.format(loc, subtitle)

m.get_root().html.add_child(folium.Element(title_html))

# Save the map as a string
m.save(f'./echo_field_day/beacon_hill_map.html')