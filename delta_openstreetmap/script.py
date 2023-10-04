
import osmnx as ox
import pandas as pd
import warnings
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point
import shapely
import folium
import matplotlib.pyplot as plt

#Helper functions
def get_amenity(amenity_str: str,tag:str):
    """
    Given a gdf of a city and a specified ameneity, get all existing coordinates

    :param amenity: string of the amenity you want to get
    :param cities: gdf of city you are getting the amenity from
    :return: geodataframe of the amenity
    """
    tags = {tag: amenity_str}
    gdf = pd.concat(
        [
            ox.geometries.geometries_from_polygon(r["geometry"], tags)
            for i, r in cities.iterrows()
        ]
    )
    gdf = (
        gdf.loc["node"].dropna(axis=1, thresh=len(gdf) / 4)
    )
    # change polygon to point
    gdf["geometry"] = gdf.to_crs(gdf.estimate_utm_crs())[
        "geometry"
    ].centroid.to_crs(gdf.crs)
    return gdf

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
    gdf_nodes = ox.graph_to_gdfs(G, edges=False)
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

def plot_isochrone(amenity_str: str, tag:str ,chart_name: str, circle_col: str, isochrome_col: str, tilelayer: str, wt=5):
   #turn off warnings
    warnings.filterwarnings("ignore")

    # get gdf of amebity
    gdf = get_amenity(amenity_str,tag)

    # build geopandas data frame of isochrone polygons for each school
    isochrones = pd.concat(
        [
            gpd.GeoDataFrame(
                get_isochrone(
                    r["geometry"].x,
                    r["geometry"].y,
                    name=r["name"],
                    point_index=i,
                ),
                crs=gdf.crs,
            )
            for i, r in gdf.iterrows()
        ]
    )

    # merge overlapping polygons
    mergedpolys = gpd.GeoDataFrame(
        geometry=isochrones.groupby("time")["geometry"]
        .agg(lambda g: g.unary_union)
        .apply(lambda g: [g] if isinstance(g, shapely.geometry.Polygon) else g.geoms)
        .explode(),
        crs=isochrones.crs,
    )

    #set map object
    m = None

    # visualize merged polygons
    m = mergedpolys.explore(
        m=m,
        color=f"{isochrome_col}",
        name=f"{wt} minute walk",
        height=800,
        width=1000,
    )

    # visualize the amenity
    m = gdf.explore(
        m=m, marker_kwds={"radius": 3, "color": f"{circle_col}"}, name=amenity_str
    )

    # Add new base layer
    folium.TileLayer(f'{tilelayer}').add_to(m)

    folium.LayerControl().add_to(m)

    # Save viz
    m.save(f'./delta_openstreetmap/output/{chart_name}.html')

    return m , mergedpolys , isochrones, gdf

def bar_plot(percentage, color: str):
    # plot bar chart
    complementary_percentage = 100 - percentage

    # Data for the stacked bar chart
    categories = ['Isochrone Area', 'Other']
    values = [percentage, complementary_percentage]

    bar_width = 0.1

    # Plotting the stacked bar chart
    fig, ax = plt.subplots()

    ax.bar(categories[0], values[1], bottom=values[0], label=categories[1], color='#F1F2F3', width=bar_width)
    ax.bar(categories[0], values[0], label=categories[0], color=color, width=bar_width)

    # Displaying the percentage in the middle of each segment of the stacked bar
    ax.text(0, values[0] / 2, f"{values[0]}%", ha='center', va='center', color='black')
    ax.text(0, values[0] + values[1] / 2, f"{values[1]}%", ha='center', va='center', color='black')

    # Setting title, labels, and legend
    ax.set_ylim(0, 110)
    ax.legend(loc='upper left')

    # Removing axis, labels, and borders
    ax.axis('off')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    plt.show()

"""
Get the GeoFrame of Manial
"""
cities = ["City of Manila"]  # ["Hereford", "Worcester", "Gloucester"]
cities = ox.geocode_to_gdf([{"city": c, "country": "philippines"} for c in cities])

"""
Clinics
"""
#parameters
tag ="amenity"
amenity_str = "clinic"
chart_name = "clinics_isochrome_map"
circle_col = "darkgreen"
isochrome_col = "lightgreen"
tile_layer = "cartodbpositron"

# create folium map of clinics and isochrones
clinics_folium, clinics_isoch , clinic_isoch2 , clinics = plot_isochrone(amenity_str=amenity_str,
                                                         tag=tag,
                                                         chart_name=chart_name,
                                                         circle_col=circle_col,
                                                         isochrome_col=isochrome_col,
                                                         tilelayer=tile_layer)

# calculate percentage
total_city_area = cities['geometry'].to_crs(epsg=32651).area.sum()
total_iso_area_cli = clinics_isoch['geometry'].to_crs(epsg=32651).area.sum()
percentage_cli = int(total_iso_area_cli / total_city_area * 100)
bar_plot(percentage_cli,"lightgreen")

"""
Bus Stops
"""
#parameters
tag ="highway"
amenity_str = "bus_stop"
chart_name = "bus_stop_isochrome_map"
circle_col = "navy"
isochrome_col = "lightblue"
tile_layer = "cartodbpositron"

# create folium map of bus stops and isochrones
bus_stop_folium , bus_stop_isoch , bus_stop_isoch2, bustops = plot_isochrone(amenity_str=amenity_str,
                                tag=tag,
                                chart_name=chart_name,
                                circle_col=circle_col,
                                isochrome_col=isochrome_col,
                                tilelayer=tile_layer)

# calculate percentage
total_iso_area_bus = bus_stop_isoch['geometry'].to_crs(epsg=32651).area.sum()
percentage_bus = int((total_iso_area_bus / total_city_area) * 100)
bar_plot(percentage_bus,"lightblue")

"""
Number of clinics within 5 minute walk to a bus stop
"""

# Spatial join of clincs within bustop_isochromes
clinics_within_bustop = gpd.sjoin(clinics.to_crs(epsg=32651), bus_stop_isoch.to_crs(epsg=32651), op='within')
clinics_notwithin_bustop =  clinics[~clinics.index.isin(clinics_within_bustop.index)]

clin_with_bus_cnt = len(clinics_within_bustop)
clin_cnt = len(clinics)
print(f'{clin_with_bus_cnt} out of {clin_cnt} are within 5 minutes of a bus stop')
percentage_clin_bus = int((len(clinics_within_bustop) / len(clinics)) * 100)


# plot
# set map object
m = None

# visualize clinics within
m = clinics_within_bustop.explore(
    m=m, marker_kwds={"radius": 5, "color": f"darkgreen"}, name="clinics",
    height = 800,
    width = 1000,
)

# visualize the clinics not within
m = clinics_notwithin_bustop.explore(
    m=m, marker_kwds={"radius": 5, "color": f"#D2042D"}, name="clinics",
    height=800,
    width=1000,
)

# Add new base layer
folium.TileLayer(f'cartodbpositron').add_to(m)

folium.LayerControl().add_to(m)

# Save viz
m.save(f'./delta_openstreetmap/output/clinics_within_bus.html')

# plot bar chart
complementary_percentage = 100 - percentage_clin_bus

# Data for the stacked bar chart
categories = ['Clinics Near Bus', 'Other']
values = [percentage_clin_bus, complementary_percentage]

bar_width = 0.1

# Plotting the stacked bar chart
fig, ax = plt.subplots()

ax.bar(categories[0], values[1], bottom=values[0], label=categories[1], color='#D2042D', width=bar_width)
ax.bar(categories[0], values[0], label=categories[0], color="darkgreen", width=bar_width)

# Displaying the percentage in the middle of each segment of the stacked bar
ax.text(0, values[0] / 2, f"{values[0]}%", ha='center', va='center', color='black')
ax.text(0, values[0] + values[1] / 2, f"{values[1]}%", ha='center', va='center', color='black')

# Setting title, labels, and legend
ax.set_ylim(0, 110)
ax.legend(loc='upper left')

# Removing axis, labels, and borders
ax.axis('off')
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()
plt.show()


# sources
"""
https://c-voulgaris.github.io/VIS-2128/week4/dataset-osm.html
https://c-voulgaris.github.io/VIS-2128/week4/skills.html#calculate-a-travel-time-matrix
https://data.humdata.org/dataset/cod-ab-phl
https://wiki.openstreetmap.org/wiki/OSMPythonTools
https://github.com/mocnik-science/osm-python-tools/tree/master
https://github.com/gboeing/osmnx
https://www.medicalnewstoday.com/articles/average-walking-speed#average-speed-by-age
https://stackoverflow.com/questions/71268239/how-do-i-plot-multiple-isochrones-polygons-using-python-osmnx-library
https://deparkes.co.uk/2016/06/10/folium-map-tiles/
Chat GPT
"""

