import geopandas as gpd
from geopandas.tools import sjoin
import matplotlib.pyplot as plt
import webbrowser
import os
import folium


"""
Load the data and do some exploraty visualizations
"""
## load datasets
bert = gpd.read_file('./Charlie_OpenDataPortal/data/Integrated_rapid_transit_(IRT)_system_MyCiTi_Bus_Stops.geojson')
suburbs = gpd.read_file('./Charlie_OpenDataPortal/data/Official_Planning_Suburbs.geojson')
regions = gpd.read_file("./Charlie_OpenDataPortal/data/City_Health_Regions.geojson")
parks = gpd.read_file('./Charlie_OpenDataPortal/data/Parks.geojson')
waters = gpd.read_file('./Charlie_OpenDataPortal/data/Storm_water_Waterbodies.geojson')

# check orginal CRS and if not 3395 then transform to projected coordinate system
geojsons = {
    'bert': bert,
    'suburbs': suburbs,
    'parks': parks,
    'waters': waters,
    'regions': regions
}

# check CRS
for name, geojson in geojsons.items():
    print(f"Original {name} CRS: ", geojson.crs)
    if geojson.crs != 'EPSG:3395':
        geojsons[name] = geojson.to_crs('EPSG:3395')

# convert to EPSG:3395
bert_3395 = bert.to_crs('EPSG:3395')
suburbs_3395 = suburbs.to_crs('EPSG:3395')
regions_3395 = regions.to_crs('EPSG:3395')
parks_3395 = parks.to_crs('EPSG:3395')
waters_3395 = waters.to_crs('EPSG:3395')

#export
bert_3395.to_file('bert_3395.geojson', driver='GeoJSON')
suburbs_3395.to_file('suburbs_3395.geojson', driver='GeoJSON')
regions_3395.to_file('regions_3395.geojson', driver='GeoJSON')
parks_3395.to_file('parks_3395.geojson', driver='GeoJSON')
waters_3395.to_file('waters_3395.geojson', driver='GeoJSON')

# interative maps usiong explore
waters_obj = waters.explore()
waters_obj.save('./Charlie - OpenDataPortal/maps/waters_map.html')
abs_path = os.path.abspath('./Charlie - OpenDataPortal/maps/waters_map.html')
webbrowser.open('file://' + abs_path, new=2)

parks_obj = parks.explore()
parks_obj.save('./Charlie - OpenDataPortal/maps/parks_map.html')
abs_path = os.path.abspath('./Charlie - OpenDataPortal/maps/parks_map.html')
webbrowser.open('file://' + abs_path, new=2)

bert_obj = bert.explore()
bert_obj.save('./Charlie - OpenDataPortal/maps/bert_map.html')
abs_path = os.path.abspath('./Charlie - OpenDataPortal/maps/bert_map.html')
webbrowser.open('file://' + abs_path, new=2)

suburbs_obj = suburbs.explore()
suburbs_obj.save('./Charlie - OpenDataPortal/maps/suburbs_map.html')
abs_path = os.path.abspath('./Charlie - OpenDataPortal/maps/suburbs_map.html')
webbrowser.open('file://' + abs_path, new=2)



"""
Task 1 The percentage of the stormwater water area that is located in parks
"""

# total stormwater area
water_area = waters_3395['geometry'].area.sum()
# Get the overlapping areas (Intersection) between parks and waters
water_in_parks = gpd.overlay(parks_3395, waters_3395, how='intersection')
# area of water in park
water_in_parks_area = water_in_parks['geometry'].area.sum()
# water in park area % total
water_in_parks_area_perc = water_in_parks_area/water_area
# water not in park
water_not_in_parks = gpd.overlay(waters_3395,parks_3395, how='difference')
# parks without water
parks_minus_water = gpd.overlay(parks_3395,waters_3395,how='difference')


#export
water_in_parks.to_file('water_in_parks_3395.geojson', driver='GeoJSON')
water_not_in_parks.to_file('water_not_in_parks_3395.geojson', driver='GeoJSON')
parks_minus_water.to_file('parks_minus_water.geojson', driver='GeoJSON')


# reload data
water_not_in_parks = gpd.read_file('./Charlie - OpenDataPortal/data/water_not_in_parks_3395.geojson')
regions_3395 = gpd.read_file("./Charlie - OpenDataPortal/data/regions_3395.geojson")
parks_minus_water = gpd.read_file('./Charlie - OpenDataPortal/data/parks_minus_water.geojson')
water_in_parks = gpd.read_file('./Charlie - OpenDataPortal/data/water_in_parks_3395.geojson')



# Setup the plot
fig, ax = plt.subplots(figsize=(12, 10))
# Plot parks without water
regions_3395.plot(ax=ax, facecolor='none',color='none', edgecolor="black",linewidth=0.5,alpha=1,linestyle='dashed',label='boundaries')
# Plot parks without water
parks_minus_water.plot(ax=ax, color='darkgreen', label='Parks')
# Plot water_in_park with a distinct color, e.g., cyan
water_in_parks.plot(ax=ax, color='cyan', label='water in parks')
# Plot water_not_in_parks with another distinct color, e.g., royalblue
water_not_in_parks.plot(ax=ax, color='blue', label='water not in park')
# Show the plot
plt.show()

#capte town coordinates
capetown_coord = [-33.9249, 18.4241]

#Create base the map
my_map = folium.Map(location = capetown_coord, zoom_start=11)
tile_layer = folium.TileLayer(
    tiles="Stamen Toner",
    max_zoom=19,
    control=False,
    opacity=0
)
tile_layer.add_to(my_map)

# add parks and water
parks_minus_water.explore(
    m=my_map,
    color='green',
)

water_in_parks.explore(
    m=my_map,
    color='cyan'
)

water_not_in_parks.explore(
    m=my_map,
    color='blue'
)

#Display the map
my_map.save('./Charlie - OpenDataPortal/maps/map1.html')
abs_path = os.path.abspath('./Charlie - OpenDataPortal/maps/map1.html')
webbrowser.open('file://' + abs_path, new=2)



"""
Task 2 the number of BRT stops with a park within ten meters
"""

# Reload Data
regions_3395 = gpd.read_file("./Charlie_OpenDataPortal/data/regions_3395.geojson")
parks_3395 = gpd.read_file('./Charlie_OpenDataPortal/data/parks_3395.geojson')
bert_3395 = gpd.read_file('./Charlie_OpenDataPortal/data/bert_3395.geojson')

# create 10 metter buffer around bus stops
buffer_distance = 10  # 10 meters
bert_3395_circles = bert_3395.copy()
bert_3395_circles['geometry'] = bert_3395_circles.buffer(buffer_distance)

# export
# bert_3395_circles.to_file("./Charlie_OpenDataPortal/data/bert_3395_circles.geojson", driver='GeoJSON')

# Cnt nunber of berts stops intersect with Park
# Perform spatial join to find circles that intersect with parks
intersecting_circles = sjoin(bert_3395_circles, parks_3395, predicate='intersects')

# get stops that don't intersect
# Perform a left spatial join.
joined_gdf = sjoin(bert_3395_circles, parks_3395, how='left', predicate='intersects')
# Filter the joined GeoDataFrame to get circles that don’t intersect with any park.
non_intersecting_circles = joined_gdf[joined_gdf.index_right.isna()].reset_index(drop=True)
# Clean up the resultant GeoDataFrame
non_intersecting_circles = non_intersecting_circles.drop(columns=['index_right'])

#export
# intersecting_circles.to_file("./Charlie_OpenDataPortal/data/bert_3395_circles_inpark.geojson", driver='GeoJSON')
# non_intersecting_circles.to_file("./Charlie_OpenDataPortal/data/bert_3395_circles_notinpark.geojson", driver='GeoJSON')


# Count the number of unique circles that intersect with parks
cnt_bert_intersect_parks = len(intersecting_circles.index.unique())
#count total number of bert stops
cnt_bert = len(bert_3395)
# % total
bert_intersect_perc_tot = cnt_bert_intersect_parks/cnt_bert

#map it out
# Define the map centered around Capetown
capetown_coord = [-33.9249, 18.4241]
my_map = folium.Map(location=capetown_coord, zoom_start=11)

# Define the TileLayer and add to map
tile_layer = folium.TileLayer(
    tiles="Stamen Toner",
    max_zoom=19,
    control=False,
    opacity=0.7  # fully transparent
)
tile_layer.add_to(my_map)

# Define a style function for regions_3395
def style_function_regions(feature):
    return {
        'fillOpacity': 0,  # fully transparent
        'color': 'black',  # border color
        'weight': 1,  # border width
    }

# Add regions_3395 layer
folium.GeoJson(
    regions_3395,
    style_function=style_function_regions,
    name='Regions'
).add_to(my_map)

# Define a style function for parks_3395
def style_function_parks(feature):
    return {
        'fillColor': 'green',
        'color': 'green',
        'weight': 1,
    }

# Add parks_3395 layer
folium.GeoJson(
    parks_3395,
    style_function=style_function_parks,
    name='Parks'
).add_to(my_map)

# Add bert_3395 as CircleMarker
for index, row in bert_3395.iterrows():
    folium.CircleMarker(
        location=[row['geometry'].y, row['geometry'].x],  # Extract latitude and longitude
        radius=10,  # Define the size of the CircleMarker
        color='red',  # Define the border color of the CircleMarker
        fill=True,
        fill_color='red',  # Define the fill color of the CircleMarker
        fill_opacity=1,  # Define the opacity of the CircleMarker
        name='Bert'
    ).add_to(my_map)

# Define a style function for bert_3395_circles with lower opacity
def style_function_bert_circles(feature):
    return {
        'fillColor': 'red',
        'color': 'red',
        'fillOpacity': 0.3,  # 50% opacity
        'weight': 1,
    }

# Add bert_3395_circles layer
folium.GeoJson(
    bert_3395_circles,
    style_function=style_function_bert_circles,
    name='Bert Circles'
).add_to(my_map)

# If you want LayerControl, you can add it like this:
folium.LayerControl().add_to(my_map)

#Display the map
my_map.save('./Charlie_OpenDataPortal/maps/map2.html')
abs_path = os.path.abspath('./Charlie_OpenDataPortal/maps/map2.html')
webbrowser.open('file://' + abs_path, new=2)


"""
Task 3 The percent of the area of each suburb covered by parks
"""
# Perform spatial intersection (overlay) between parks and suburbs
intersected = gpd.overlay(suburbs_3395, parks_3395, how='intersection')

# Calculate the area of the intersected geometries
intersected['area'] = intersected['geometry'].area

# Aggregate the intersected areas for each suburb
aggregated_areas = intersected.groupby('OBJECTID_1')['area'].sum().reset_index(name='intersected_area')

# Merge the aggregated areas back to the suburbs GeoDataFrame
suburbs_with_areas = suburbs_3395.merge(aggregated_areas, left_on='OBJECTID', right_on='OBJECTID_1', how='left')
suburbs_with_areas.drop(columns={'OBJECTID_1'},inplace=True)

# Fill NaN values with 0 for suburbs with no parks
suburbs_with_areas['intersected_area'].fillna(0, inplace=True)

# Calculate the area of the suburb geometries
suburbs_with_areas['suburb_area'] = suburbs_with_areas['geometry'].area

suburbs_with_areas.crs

# Calculate the percentage of each suburb covered in parks
suburbs_with_areas['parks_percentage'] = (suburbs_with_areas['intersected_area'] / suburbs_with_areas['suburb_area']) * 100

#export
suburbs_with_areas.to_file("./Charlie_OpenDataPortal/data/suburbs_3395_parks.geojson", driver='GeoJSON')


"""
Task 4 - The distance from each BRT stop to the closest park]
"""

#calculate the shortest distance to parks for each bert stop
distances = []
for index, bert in bert_3395.iterrows():
    # Calculate the distance from each point to all parks and find the minimum distance
    min_distance = parks_3395.distance(bert.geometry).min()
    distances.append(min_distance)

bert_3395['distance'] = distances

# export
bert_3395.to_file("./Charlie_OpenDataPortal/data/bert_3395_distance.geojson", driver='GeoJSON')

#plot hist
bert_3395_dist = gpd.read_file("./Charlie_OpenDataPortal/data/bert_3395_distance.geojson")

bert_3395_dist['distance'] =  bert_3395_dist['distance'].astype(int)

# Extract the column
distances = bert_3395_dist['distance']

# Define bin edges with a step of 50 meters
bin_edges = range(0, int(distances.max()) + 50, 50)

# Plot histogram
plt.figure(figsize=(10,6))
plt.hist(distances, bins=bin_edges, edgecolor='k', alpha=0.7)
plt.title('Distance Histogram')
plt.xlabel('Distance (m)')
plt.ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)
plt.xticks(bin_edges, rotation=45)
plt.tight_layout()

# Show plot
plt.show()


