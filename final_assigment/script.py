import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from tqdm import tqdm
import time
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import json
import branca
import seaborn as sns
import osmnx as ox
import networkx as nx
from shapely.geometry import Point, LineString, Polygon, MultiLineString
import folium
from folium.map import Popup
from folium import Marker
import shapely


# read shape file
shape_file_path = "./final_assigment/decennial_census_tract/tl_2022_25_tract.shp"
tracks_gdf = gpd.read_file(shape_file_path)

#read census vietnamese population file
viet_pop = pd.read_csv("./final_assigment/decennial_viet_pop.csv")

#cleaning
viet_pop_piv = viet_pop.T.reset_index()
viet_pop_piv.rename(columns={'index':'tracks', 0:'vietnamese_pop'},inplace=True)
viet_pop_piv = viet_pop_piv.iloc[2:].reset_index(drop=True)
viet_pop_piv['vietnamese_pop'].iloc[337] = 2284
viet_pop_piv['vietnamese_pop'] = viet_pop_piv['vietnamese_pop'].astype(int)

# Extract the float number after "Census Tract" and county name
viet_pop_piv['track'] = viet_pop_piv['tracks'].str.extract(r'Census Tract (\d+(\.\d+)?)')[0]
viet_pop_piv['county'] = viet_pop_piv['tracks'].str.extract(r'; (\w+ County);')

#drop tracks col
viet_pop_piv.drop(columns={'tracks'},inplace=True)

#join to geo df
gdf = tracks_gdf.merge(viet_pop_piv,how='left', left_on='NAME', right_on='track')
# keep tracks for suffolk, norfolk and middlesex counties
gdf = gdf.loc[gdf['COUNTYFP'].isin(['017', '021', '025'])].reset_index(drop=True)
gdf['vietnamese_pop'] = gdf['vietnamese_pop'].fillna(0)

# choropleth map
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
gdf.plot(column='vietnamese_pop', cmap='OrRd', linewidth=0.8,ax=ax, edgecolor='0.8')
ax.set_title('Population Choropleth Map')
plt.show()

#log cloropleth
gdf['vietnamese_pop_log'] = np.log(gdf['vietnamese_pop']+1)
gdf['vietnamese_pop_log2'] = np.log(gdf['vietnamese_pop'])
gdf['vietnamese_pop_log2'] = gdf['vietnamese_pop_log2'].replace(-np.inf, 0)

# log choropleth map
# Create a custom colormap
colors = ["#FFCD00", "#C8102E"]
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

fig, ax = plt.subplots(1, 1, figsize=(10, 6))
gdf.plot(column='vietnamese_pop_log2', cmap=cmap, linewidth=0.8,ax=ax, edgecolor='0.8',legend=True)
ax.set_title('log of Vietnamese Population Choropleth Map')
plt.show()

## density plot
def generate_points_in_polygon(number, polygon):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < number:
        x = np.random.uniform(minx, maxx)
        y = np.random.uniform(miny, maxy)
        point = Point(x, y)
        if polygon.contains(point):
            points.append(point)
    return points

# Define the number of people each dot represents
PEOPLE_PER_DOT = 10

# Generate the points for the dot density map
all_points = []
for _, row in gdf.iterrows():
    num_points = int(row['vietnamese_pop'] / PEOPLE_PER_DOT)
    points = generate_points_in_polygon(num_points, row['geometry'])
    all_points.extend(points)

# Convert the points to a GeoDataFrame
point_gdf = gpd.GeoDataFrame(geometry=all_points)

# Plotting
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
gdf.plot(ax=ax, color='#FFCD00',edgecolor="white",linewidth=0.5)
point_gdf.plot(ax=ax, markersize=5, color='#C8102E',edgecolor="white", linewidth=0.2,legend=True)
ax.set_title('Dot Density Map of Vietnamese Population (1 dot = 10 residents')
plt.show()

#combine log cloropleth and dotdensity map
# Define a colormap for the choropleth
colors = ["#FFCD00", "#C8102E"]
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

# Create a 1x2 subplot (one row, two columns) for the two maps side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 6))

# First plot: Choropleth
gdf.plot(column='vietnamese_pop_log2', cmap=cmap, linewidth=0.8, ax=ax1, edgecolor='0.8', legend=True)
ax1.set_title('log of Vietnamese Population Choropleth Map')

# Second plot: Dot Density
gdf.plot(ax=ax2, color='#FFCD00', edgecolor="white", linewidth=0.5)
point_gdf.plot(ax=ax2, markersize=5, color='#C8102E', edgecolor="white", linewidth=0.2, legend=True)
ax2.set_title('Dot Density Map of Vietnamese Population (1 dot = 10 residents)')

plt.tight_layout()
plt.show()


########################################################################
# scrape yelp

#initial random useragent for web
ua = UserAgent()
def scrape_yelp(url):
    html_text = requests.get(url,headers={'User-Agent': ua.random}).text
    bs = BeautifulSoup(html_text,features="lxml")
    bs_pretty = bs.prettify()
    return bs_pretty

urls = ['https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Suffolk+County%2C+MA',
        'https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-70.94360181366349%2C42.386113130328916%2C-71.14238568817521%2C42.28078731343382',
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.02986165558244%2C42.35647810441349%2C-71.1292535928383%2C42.30381241389767",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.03904553924943%2C42.344927987936416%2C-71.13843747650529%2C42.29225262372801",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-70.98600217377091%2C42.370102215074255%2C-71.18478604828263%2C42.26474956680817",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.02428266083146%2C42.365894832253716%2C-71.22306653534318%2C42.26053513455049"
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-70.98236423559251%2C42.33190311514392%2C-71.18114811010423%2C42.22648648547551",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.03163105077806%2C42.333023194971645%2C-71.23041492528978%2C42.2276084407073",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.08536106176439%2C42.36142023956773%2C-71.2841449362761%2C42.25605304534429",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.08038288183275%2C42.394114980908704%2C-71.27916675634447%2C42.288802576744644",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.07866626806322%2C42.42413171601545%2C-71.27745014257493%2C42.31886964436058",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.10956531591478%2C42.48034613787989%2C-71.3083491904265%2C42.37517840530666",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.11025196142259%2C42.51816660713064%2C-71.30903583593431%2C42.4130624020112",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.05635028905931%2C42.50182067154346%2C-71.25513416357103%2C42.39668900434308",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.08587604589525%2C42.44897947413823%2C-71.28465992040697%2C42.343759089486674",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.02911596539978%2C42.295626887996484%2C-71.2278998399115%2C42.19014954111889",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-70.9228575730658%2C42.282227038876314%2C-71.12164144757752%2C42.17672727476713",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.03111031821295%2C42.31160984730014%2C-71.13050225546881%2C42.258906589803274",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.0697341280274%2C42.301379113803705%2C-71.16912606528327%2C42.248667294919514",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=&l=g%3A-71.07582810690924%2C42.301282588542456%2C-71.1752200441651%2C42.24857068889101",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Norfolk+County%2C+MA&l=g%3A-71.08468235086511%2C42.35792453024582%2C-71.18407428812097%2C42.305260051321454",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-71.28381807250977%2C42.65673575540294%2C-71.38321000976563%2C42.60432229367027",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-71.2800415222168%2C42.63728557455936%2C-71.37943345947266%2C42.58485573014335",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-71.25180322570802%2C42.62887610631419%2C-71.35119516296388%2C42.57643918056443",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-71.33883559059299%2C42.65054196945797%2C-71.43822752784885%2C42.59812329010799",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-71.40538170477664%2C42.646860672677285%2C-71.80294945380008%2C42.43690878637906",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-71.29757836005008%2C42.49472931285918%2C-71.69514610907352%2C42.28426573809329",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-71.16059258124149%2C42.431576189451604%2C-71.55816033026493%2C42.22090063919502",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-71.0730452789954%2C42.35186965134671%2C-71.47061302801883%2C42.14092693078141",
        "https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-70.85022881171024%2C42.25240951506509%2C-71.24779656073368%2C42.0411339870851",]

master_result = []

for url in tqdm(urls,total=len(urls)):

    #get html from search
    bs_pretty = scrape_yelp(url)

    # Use regex to extract desired text
    result = re.search(r'"key":1(.*?)"name":"ad_business"}', bs_pretty)

    # Check if the pattern was found and print the result
    if result:
        extracted_text = result.group(0)
        master_result.append(extracted_text)

    time.sleep(random.uniform(1, 5))

#Regex to pull the restaurant names coordinates
def regex_title_coord(obs):
    title_pattern = r'"title":"(.*?)"'
    latitude_pattern = r'"latitude":([\d.-]+)'
    longitude_pattern = r'"longitude":([\d.-]+)'

    titles = re.findall(title_pattern, obs)
    latitudes = re.findall(latitude_pattern, obs)
    longitudes = re.findall(longitude_pattern, obs)

    data_list = []

    for title, latitude, longitude in zip(titles, latitudes, longitudes):
        data_list.append({
            "title": title,
            "latitude": float(latitude),
            "longitude": float(longitude)
        })
    return data_list

clean_master = list()
for obs in master_result:
    clean = regex_title_coord(obs)
    clean_master.extend(clean)

#drop duplicates
clean_master_de_duped = list({frozenset(item.items()): item for item in clean_master}.values())
with open("./final_assigment/vietnamese_restaurants.json","w") as jsonfile:
        json.dump(clean_master_de_duped,jsonfile,indent=4)


#convert to geojson
viet_rest_df = pd.DataFrame(clean_master_de_duped)
viet_rest_df = viet_rest_df.drop_duplicates(subset="title")
geometry = [Point(xy) for xy in zip(viet_rest_df["longitude"], viet_rest_df["latitude"])]
viet_rest_gdf = gpd.GeoDataFrame(viet_rest_df, geometry=geometry)
viet_rest_gdf.crs = "EPSG:4269"

# filter for restaurants in census tracks
filtered_restaurants = gpd.sjoin(viet_rest_gdf, gdf, how="inner", op="within")


# plot with cloropleth map

fig, ax= plt.subplots(1, 1, figsize=(20, 6))

# First plot: Choropleth
gdf.plot(column='vietnamese_pop_log2', cmap=cmap, linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
filtered_restaurants.plot(ax=ax, markersize=20, color='black',edgecolor="white", linewidth=0.2,legend=True)
ax1.set_title('log of Vietnamese Population Choropleth Map and restaurant locations')
plt.tight_layout()
plt.show()

#save geojson files for final viz
gdf.to_file("./final_assigment/final_data/vietnamese_census_tracks.geojson", driver='GeoJSON')
point_gdf.to_file("./final_assigment/final_data/vietnamese_dotdensity.geojson", driver='GeoJSON')
filtered_restaurants.to_file("./final_assigment/final_data/vietnamese_restaurants.geojson", driver='GeoJSON')

########################################################################################################################


#load geo json files
census_track = gpd.read_file("./final_assigment/final_data/vietnamese_census_tracks.geojson")
viet_rest = gpd.read_file("./final_assigment/final_data/vietnamese_restaurants.geojson")
dot_density = gpd.read_file("./final_assigment/final_data/vietnamese_dotdensity.geojson")
def jitter_coordinates(geometry, magnitude=1e-4):
    """
    Add a small random offset to the point's coordinates.

    :param geometry: The geometry (point) to jitter.
    :param magnitude: The magnitude of the jitter (default is a very small value).
    :return: A new Point with jittered coordinates.
    """
    return Point(geometry.x + np.random.uniform(-magnitude, magnitude),
                 geometry.y + np.random.uniform(-magnitude, magnitude))

# Apply the jitter function to each point in the GeoDataFrame
viet_rest['geometry'] = viet_rest['geometry'].apply(jitter_coordinates)

#Map 1: dot density map of vietnamese population
m = folium.Map(location=[42.377150, -71.101980], zoom_start=10,tiles='cartodbpositron',height='80%')

#Add the census_track layer
def census_style(feature):
    return {
        'fillColor': '#FFCD00',
        'color': 'white',
        'weight': 2,
        'fillOpacity': 0.2
    }

folium.GeoJson(
    census_track,
    style_function=census_style,
).add_to(m)

#Add the dot_density points
def dot_density_style(feature):
    return {
        'radius': 3,  # You can change the radius of the points here
        'color': 'white',
        'fill': True,
        'fillColor': '#C8102E',
        'weight': 0.5,
        'fillOpacity': 1
    }

# Assuming dot_density is a GeoDataFrame of Point geometries
folium.GeoJson(
    dot_density,
    style_function=dot_density_style,
    marker=folium.CircleMarker()
).add_to(m)

loc = 'Dot Density Map of the Vietnamese Community, (1 dot = 10 people)'
subtitle = "Let's begin by examining the distribution of Vietnamese residents based on census tracks. Distinct pockets of residency emerge, especially in areas like Lowell, Malden, Dorchester, Quincy, and Randolph. Proceed to the next slide to explore potential restaurant locations within these areas."
source = 'Source: Decennial Census of Population and Housin (Suffolk, Norfolk and middlesex)'

title_html = '''
             <h3 align="center" style="background-color: #9e6b90; color: white; font-weight:bold; font-family: 'Optima', sans-serif; padding: 10px; text-align: center; font-size: 24px;"><b>{}</b></h3>
             <h4 align="center" style="background-color: white; color: black; font-family: 'Optima', sans-serif; padding: 5px; text-align: center; font-size: 15px;">{}</h4>
             '''.format(loc, subtitle)

bottom_subtitle_js = '''
<script type="text/javascript">
    document.addEventListener("DOMContentLoaded", function() {{
        var subtitleDiv = document.createElement("div");
        subtitleDiv.innerHTML = '<h4 align="left" style="background-color: white; color: black; font-family: "Optima", sans-serif; padding: 5px; text-align: center; font-size: 15px; margin-top: 10px;">{}</h4>';
        document.body.appendChild(subtitleDiv);
    }});
</script>
'''.format(source)

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(bottom_subtitle_js))

# Save the map
m.save(f'./final_assigment/map1.html')

#Map 2: Cloropleth map with restaurants
# Base folium plot Visualize with Folium
m = folium.Map(location=[42.377150, -71.101980], zoom_start=10,tiles='cartodbpositron',height='80%')

# Create a custom color gradient
colors = ["#FFCD00", "#C8102E"]
cmap = branca.colormap.LinearColormap(colors, vmin=census_track['vietnamese_pop_log2'].min(), vmax=census_track['vietnamese_pop_log2'].max()).to_step(n=10)
cmap.caption = 'log of Vietnamese Population'

def style_function(feature):
    return {
        'fillOpacity': 0.5,
        'weight': 0.8,
        'fillColor': cmap(feature['properties']['vietnamese_pop_log2']),
        'color' : "white"
    }

folium.GeoJson(
    census_track,
    style_function=style_function,
).add_to(m)

cmap.add_to(m)  # Adding the colormap to the map

# Adding the restaurants as points with a custom icon
for idx, row in viet_rest.iterrows():
    icon = folium.CustomIcon(icon_image=f"./final_assigment/food.png", icon_size=(60, 60))
    popup = Popup(str(row['title']), max_width=300)
    Marker(location=(row['geometry'].y, row['geometry'].x), icon=icon, popup=popup).add_to(m)

loc = 'Chloropleth Map of Vietnamese population and Vietnamese Restaurant Locations'
subtitle = "It seems there's a relationship between population density and the culinary landscape. Notably, areas such as Lowell, Dorchester, and Quincy are brimming with vietnamese restaurants. Note that I have a small sample of eateries scrapped from Yelp, so a more comprehensive statistical analysis with a broader dataset would be essential to draw any conclusions. Nonetheless, the initial findings are promising! Explore the map and click on the icons to see thename of the restaurant"
source = 'Source: Decennial Census of Population and Housin (Suffolk, Norfolk and middlesex), Yelp (web scrapped subset of vietnamese restaurants, not exhaustive)'

title_html = '''
             <h3 align="center" style="background-color: #9e6b90; color: white; font-weight:bold; font-family: 'Optima', sans-serif; padding: 10px; text-align: center; font-size: 24px;"><b>{}</b></h3>
             <h4 align="center" style="background-color: white; color: black; font-family: 'Optima', sans-serif; padding: 5px; text-align: center; font-size: 15px;">{}</h4>
             '''.format(loc, subtitle)

bottom_subtitle_js = '''
<script type="text/javascript">
    document.addEventListener("DOMContentLoaded", function() {{
        var subtitleDiv = document.createElement("div");
        subtitleDiv.innerHTML = '<h4 align="left" style="background-color: white; color: black; font-family: "Optima", sans-serif; padding: 5px; text-align: center; font-size: 15px; margin-top: 10px;">{}</h4>';
        document.body.appendChild(subtitleDiv);
    }});
</script>
'''.format(source)

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(bottom_subtitle_js))

# Save the map as a string
m.save(f'./final_assigment/map2.html')


# Identifying select restaurants based on pop density?
pop_where_rest = viet_rest.groupby(by="GEOID")['vietnamese_pop'].mean().reset_index().sort_values(by='GEOID')
rest_cnt = viet_rest.groupby(by="GEOID").size().reset_index(name='count')
pop_where_rest = pop_where_rest.merge(rest_cnt,how='left',left_on='GEOID',right_on='GEOID')


#plots!

# Setup figure and axes
fig, ax = plt.subplots(2, 2, figsize=(16, 12))

# Density plot
sns.kdeplot(pop_where_rest['vietnamese_pop'], fill=True, color="#FFCD00", lw=2, ax=ax[0,0])
ax[0,0].set_title('Vietnamese Population Distribution by Census Track - Density Plot')
ax[0,0].set_xlabel('Population')
ax[0,0].set_ylabel('Density')
ax[0,0].grid(True, which='both', linestyle='--', linewidth=0.5)

# CDF plot
cum_dist = np.linspace(0., 1., len(pop_where_rest['vietnamese_pop']))
cdf = pd.Series(cum_dist, index=pop_where_rest['vietnamese_pop'].sort_values())
cdf.plot(drawstyle='steps', color="#FFCD00", ax=ax[0,1])
ax[0,1].set_title('CDF of Vietnamese Population')
ax[0,1].set_xlabel('Population')
ax[0,1].set_ylabel('Probability')
ax[0,1].grid(True, which='both', linestyle='--', linewidth=0.5)

# Box plot
ax[1,0].boxplot(pop_where_rest['vietnamese_pop'], vert=False, patch_artist=True,
            boxprops=dict(facecolor="#FFCD00", color="#C8102E"),
            capprops=dict(color="#C8102E"),
            whiskerprops=dict(color="#C8102E"),
            flierprops=dict(markeredgecolor="#C8102E"),
            medianprops=dict(color="#C8102E"))
ax[1,0].set_title('Vietnamese Population Distribution - Box Plot')
ax[1,0].set_xlabel('Population')
ax[1,0].set_yticks([1])
ax[1,0].set_yticklabels(['Population'])
ax[1,0].grid(True, which='both', linestyle='--', linewidth=0.5, axis='x')

# scatter plot
colors = ["#C8102E" if pop >= 500 else "#FFCD00" for pop in pop_where_rest['vietnamese_pop']]
ax[1,1].scatter(pop_where_rest['vietnamese_pop'], pop_where_rest['count'], color=colors, edgecolor="#C8102E")
ax[1,1].set_title('Vietnamese Population vs. Number of Vietnamese Restaurants by census track - Scatter plot')
ax[1,1].set_xlabel('Vietnamese Population')
ax[1,1].set_ylabel('Number of Restaurants')
ax[1,1].get_legend()
ax[1,1].grid(True)

plt.tight_layout()
plt.show()

fig.savefig('./final_assigment/dist_plot.png')


#Map 3: driving distance and route from me to these restaurants

# filter out census tracks and restaurants if pop less than 500 and plot
viet_rest2 = viet_rest.loc[viet_rest['vietnamese_pop'] >= 500]

# Given coordinates
start_point = (42.375980, -71.113650)

# Get road network
G = ox.graph_from_point(start_point, dist=24000, network_type='drive')

# Convert start_point to the nearest node in the network
start_node = ox.distance.nearest_nodes(G, X=start_point[1], Y=start_point[0])

# Base folium plot
m = folium.Map(location=start_point, zoom_start=10, tiles='cartodbpositron',height='80%')

# Adding start point on the map
folium.Marker(location=start_point, popup="Gund Hall", icon=folium.Icon(color="green")).add_to(m)

# Iterate through the restaurant points
for idx, row in viet_rest2.iterrows():
    dest_point = (row['geometry'].y, row['geometry'].x)
    # Convert destination point to nearest node in the network
    dest_node = ox.distance.nearest_nodes(G, X=dest_point[1], Y=dest_point[0])

    # Get the shortest path
    route = nx.shortest_path(G, start_node, dest_node, weight='length')

    # Calculate distance of the route in meters
    distance_meters = sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length'))
    distance_kms = distance_meters / 1000

    # Assume average driving speed is 40 km/h (you can adjust this)
    avg_speed = 40
    time_minutes = (distance_kms / avg_speed) * 60

    # Convert the route to a LineString
    line_geom = LineString([Point((G.nodes[node]['x'], G.nodes[node]['y'])) for node in route])

    # Add the route to the map
    folium.PolyLine(locations=[(coord[1], coord[0]) for coord in line_geom.coords],
                    color="#FFCD00", weight=2.5, opacity=1).add_to(m)

    # Adding the restaurant point with popup details
    popup_text = f"{row['title']}<br>Distance: {distance_kms:.2f} km<br>Estimated Time: {time_minutes:.2f} mins"
    popup = Popup(popup_text, max_width=300)
    icon = folium.CustomIcon(icon_image=f"./final_assigment/food.png", icon_size=(60, 60))
    Marker(location=dest_point, icon=icon, popup=popup).add_to(m)

loc = 'Restaurants located in Areas with 500+ Vietnamese Residents and how far they are from School!'
subtitle = "It looks like Rochester and Randolph might be places worth venturing to for vietnamese food! Navigate through the map to explore some vietnamese eateries there and give those icons a tap to see how far they are from school!"
source = 'Source: Decennial Census of Population and Housin (Suffolk, Norfolk and middlesex), Yelp (web scrapped subset of vietnamese restaurants, not exhaustive)'

title_html = '''
             <h3 align="center" style="background-color: #9e6b90; color: white; font-weight:bold; font-family: 'Optima', sans-serif; padding: 10px; text-align: center; font-size: 24px;"><b>{}</b></h3>
             <h4 align="center" style="background-color: white; color: black; font-family: 'Optima', sans-serif; padding: 5px; text-align: center; font-size: 15px;">{}</h4>
             '''.format(loc, subtitle)

bottom_subtitle_js = '''
<script type="text/javascript">
    document.addEventListener("DOMContentLoaded", function() {{
        var subtitleDiv = document.createElement("div");
        subtitleDiv.innerHTML = '<h4 align="left" style="background-color: white; color: black; font-family: "Optima", sans-serif; padding: 5px; text-align: center; font-size: 15px; margin-top: 10px;">{}</h4>';
        document.body.appendChild(subtitleDiv);
    }});
</script>
'''.format(source)

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(bottom_subtitle_js))

# Save the map
m.save(f'./final_assigment/map4.html')


# method 4: plot restaurants and isochrones if they are 5 minutes walk from each other --> identifying pockets of good food!

def get_isochrone(lon, lat, walk_times=[5], speed=4.5, name=None, point_index=None,travel="walk"):
    """
    Create isochrone for given coordinates

    :param lon: longitude coordinate
    :param lat: latitude coordinate
    :param walk_times: time of walking distance in minutes
    :param speed: walking speed
    :return: isochrome
    """
    loc = (lat, lon)
    G = ox.graph_from_point(loc, simplify=True, network_type=travel)
    # gdf_nodes = ox.graph_to_gdfs(G, edges=False)
    center_node = ox.distance.nearest_nodes(G, lon, lat)

    meters_per_minute = speed * 1000 / 60
    for u, v, k, data in G.edges(data=True, keys=True):
        data["time"] = data["length"] / meters_per_minute
    polys = []
    for walk_time in walk_times:
        subgraph = nx.ego_graph(G, center_node, radius=walk_time, distance="time")
        node_points = [
            Point(data["x"], data["y"]) for node, data in subgraph.nodes(data=True)
        ]
        polys.append(gpd.GeoSeries(node_points).unary_union.convex_hull)
    info = {}
    if name:
        info["name"] = [name for t in walk_times]
    if point_index:
        info["point_index"] = [point_index for t in walk_times]
    return {**{"geometry": polys, "time": walk_times}, **info}

isochrones = pd.concat(
    [
        gpd.GeoDataFrame(
            get_isochrone(
                r["geometry"].x,
                r["geometry"].y,
                name=r["title"],
                point_index=i,
            ),
            crs=viet_rest.crs,
        )
        for i, r in viet_rest.iterrows()
    ]
)

# merge the isochrones
mergedpolys = gpd.GeoDataFrame(
      geometry=isochrones.groupby("time")["geometry"]
      .agg(lambda g: g.unary_union)
      .apply(lambda g: [g] if isinstance(g,Polygon) else g.geoms)
      .explode(),
      crs=isochrones.crs,
  )

#filter isochrones with only 1 point
def count_points_in_polygon(poly, points_gdf):
    return sum(points_gdf.within(poly))

#Applying this function to count points for each polygon in mergedpolys
mergedpolys['point_count'] = mergedpolys['geometry'].apply(lambda x: count_points_in_polygon(x, viet_rest))

# Filter merged polygons and points based on the count
filtered_polys = mergedpolys[mergedpolys['point_count'] >= 4].copy()
filtered_polys.drop(columns=['point_count'], inplace=True)

# Similarly, filter viet_rest points that fall within these filtered polygons
filtered_points = viet_rest[viet_rest.geometry.apply(lambda x: filtered_polys.contains(x).any())]

# Get the road network near the start point
location_point = (42.375980, -71.113650)
G = ox.graph_from_point(location_point, dist=40000, network_type='drive')  # Adjust distance as needed

# Get the nearest node to the start point
start_node = ox.distance.nearest_nodes(G, X=location_point[1], Y=location_point[0])

# Base folium plot
m = folium.Map(location=start_point, zoom_start=13, tiles='cartodbpositron',height='80%')

# Adding start point on the map
folium.Marker(location=start_point, popup="Gund Hall", icon=folium.Icon(color="green")).add_to(m)

# Plot the overlapping polygons
folium.GeoJson(filtered_polys, style_function=lambda feature: {
    'fillColor': '#FFCD00',
    'color': '#C8102E',
    'weight': 2,
    'fillOpacity': 0.4
}).add_to(m)

# Adding the restaurants as points with a custom icon and routes
for idx, row in filtered_points.iterrows():
    dest_point = (row['geometry'].y, row['geometry'].x)
    # Convert destination point to nearest node in the network
    dest_node = ox.distance.nearest_nodes(G, X=dest_point[1], Y=dest_point[0])

    # Get the shortest path
    route = nx.shortest_path(G, start_node, dest_node, weight='length')

    # Calculate distance of the route in meters
    distance_meters = sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length'))
    distance_kms = distance_meters / 1000

    # Assume average driving speed is 40 km/h (you can adjust this)
    avg_speed = 40
    time_minutes = (distance_kms / avg_speed) * 60

    # Convert the route to a LineString
    line_geom = LineString([Point((G.nodes[node]['x'], G.nodes[node]['y'])) for node in route])

    # Add the route to the map
    folium.PolyLine(locations=[(coord[1], coord[0]) for coord in line_geom.coords],
                    color="#FFCD00", weight=2.5, opacity=1).add_to(m)

    # Adding the restaurant point with popup details
    popup_text = f"{row['title']}<br>Distance: {distance_kms:.2f} km<br>Estimated Time: {time_minutes:.2f} mins"
    popup = Popup(popup_text, max_width=300)
    icon = folium.CustomIcon(icon_image=f"./final_assigment/food.png", icon_size=(60, 60))
    Marker(location=dest_point, icon=icon, popup=popup).add_to(m)

loc = 'Pockets of Restaurants: Identifying clusters of 4 or more restaurants that are 5 minute walk from each other'
subtitle = "Census tracks won't tell the whole story, so let's look at clusters of Vietnamese restaurants just a quick 5-minute walk apart. Who knows? These bustling culinary corners might just reveal where the real Vietnamese foodie magic happens!"
source = 'Source: Decennial Census of Population and Housin (Suffolk, Norfolk and middlesex), Yelp (web scrapped subset of vietnamese restaurants, not exhaustive)'

title_html = '''
             <h3 align="center" style="background-color: #9e6b90; color: white; font-weight:bold; font-family: 'Optima', sans-serif; padding: 10px; text-align: center; font-size: 24px;"><b>{}</b></h3>
             <h4 align="center" style="background-color: white; color: black; font-family: 'Optima', sans-serif; padding: 5px; text-align: center; font-size: 15px;">{}</h4>
             '''.format(loc, subtitle)

bottom_subtitle_js = '''
<script type="text/javascript">
    document.addEventListener("DOMContentLoaded", function() {{
        var subtitleDiv = document.createElement("div");
        subtitleDiv.innerHTML = '<h4 align="left" style="background-color: white; color: black; font-family: "Optima", sans-serif; padding: 5px; text-align: center; font-size: 15px; margin-top: 10px;">{}</h4>';
        document.body.appendChild(subtitleDiv);
    }});
</script>
'''.format(source)

m.get_root().html.add_child(folium.Element(title_html))
m.get_root().html.add_child(folium.Element(bottom_subtitle_js))

m.save(f'./final_assigment/map5.html')


"""
sources:
Vietnamese population decennial
https://data.census.gov/map?q=United+States&t=3861&g=050XX00US25017$1400000,25021$1400000,25025$1400000&tid=DECENNIALDDHCA2020.T01001&layer=VT_2020_140_00_PY_D1&mode=thematic&loc=42.3619,-71.3355,z8.8238

census tracks 
https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2022&layergroup=Census+Tracts

yelp
https://www.yelp.com/search?find_desc=Vietnamese+Food&find_loc=Middlesex+County%2C+MA&l=g%3A-70.964376254538%2C42.42284465058895%2C-71.16316012904971%2C42.31758042016914

skillsets:
1) hw1 - layers 
2) hw2 - demographic data /density plots
3) hwx - geospatial calculations - removing restaurants not in the sencus track 
4) hwx - open street map 
5) map on isochrones

icon:
https://pngtree.com/freepng/com-suon-vietnamese-food_6540258.html
"""