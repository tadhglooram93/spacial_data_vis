import geopandas as gpd
import matplotlib.pyplot as plt
import webbrowser
import os
import folium

## load datasets
bert = gpd.read_file('./Charlie - OpenDataPortal/data/Integrated_rapid_transit_(IRT)_system_MyCiTi_Bus_Stops.geojson')
suburbs = gpd.read_file('./Charlie - OpenDataPortal/data/Official_Planning_Suburbs.geojson')
regions = gpd.read_file("./Charlie - OpenDataPortal/data/City_Health_Regions.geojson")
parks = gpd.read_file('./Charlie - OpenDataPortal/data/Parks.geojson')
waters = gpd.read_file('./Charlie - OpenDataPortal/data/Storm_water_Waterbodies.geojson')

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

### Calculations

## The percentage of the stormwater water area that is located in parks
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


# relaod data

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



folium.TileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.{ext}',
                 attr='Mapbox'
                 ).add_to(m)
m.save('./Charlie - OpenDataPortal/maps/map1.html')
abs_path = os.path.abspath('./Charlie - OpenDataPortal/maps/map1.html')
webbrowser.open('file://' + abs_path, new=2)



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

overlapping_areas_3395_obj = overlapping_areas_3395.explore()
overlapping_areas_3395_obj.save('./Charlie - OpenDataPortal/maps/overlapping_areas_3395_map.html')
abs_path = os.path.abspath('./Charlie - OpenDataPortal/maps/overlapping_areas_3395_map.html')
webbrowser.open('file://' + abs_path, new=2)

# The number of BRT stops with a park within ten meters
# The percent of the area of each suburb covered by parks
# The distance from each BRT stop to the closest park]

