import pandas as pd
import pygris as pg
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from pygris.utils import shift_geometry
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from pypdf import PdfMerger

"""
Get TIGER layer for NY state
"""
#load NY state layer
states = pg.states(year=2022).to_crs(32619)
states = shift_geometry(states)
state_ny = states[states['NAME'] == "New York"]

"""
Get TIGER layer for NY roads
"""
#Get counties
counties = pg.counties()
# filter out the names of counties in new york
counties_name_ls = counties[counties['STATEFP'] == "36"]['NAME'].tolist()
#get roads for counties
roads_ny = pg.roads(year=2022, state="New York",county=counties_name_ls).to_crs(32619)
roads_ny = shift_geometry(roads_ny)


"""
Get TIGER layer for NY rails
"""
#load the data
rails = pg.rails(year=2022).to_crs(32619)
rails = shift_geometry(rails)
#load the rails name from the csv files
ny_rails_names = pd.read_csv("./assignments/Alpha - US_Census_TIGER/ny_rails.csv",dtype={
    'OID': 'string'})
#convert the names to a list
OID = ny_rails_names['OID'].unique().tolist()
# filter the dataframe
rails_ny = rails[rails['LINEARID'].isin(OID)]


"""
Plot a map of all three layers
"""
#helper function to plot a compass rose
def compass_rose(location=(0.1,0,1)):
    """
    Add a cpmpass rose to a Geopandas plot, note we assume here that the Geographic data in shapefiles follows a standard
    coordinate system where the positive Y-axis points towards the geographical north and the positive X-axis points towards
    the east. check that is the case before adding the compase rose: print(GeoDataFrame.crs) should print EPSG:4269.

    Parameters:
    location: The position of the compass rose in axis units.
    """
    # Setting the coordinates for the center of the compass rose
    compass_rose_x, compass_rose_y = location[0], location[1]

    # Creating the compass rose
    ax.annotate('', xy=(compass_rose_x, compass_rose_y + 0.04), xytext=(compass_rose_x, compass_rose_y),
                arrowprops=dict(arrowstyle='->', color='black'), xycoords='axes fraction')
    ax.annotate("N", xy=(compass_rose_x, compass_rose_y + 0.04), xytext=(compass_rose_x - 0.004, compass_rose_y + 0.04),
                fontsize=10, xycoords='axes fraction')
    ax.annotate('', xy=(compass_rose_x, compass_rose_y - 0.04), xytext=(compass_rose_x, compass_rose_y),
                arrowprops=dict(arrowstyle='->', color='black'), xycoords='axes fraction')
    ax.annotate("S", (compass_rose_x, compass_rose_y - 0.04), xytext=(compass_rose_x, compass_rose_y - 0.05),
                ha='center', fontsize=10, xycoords='axes fraction')
    ax.annotate('', xy=(compass_rose_x - 0.03, compass_rose_y), xytext=(compass_rose_x, compass_rose_y),
                arrowprops=dict(arrowstyle='->', color='black'), xycoords='axes fraction')
    ax.annotate("W", xy=(compass_rose_x - 0.03, compass_rose_y),
                xytext=(compass_rose_x - 0.034, compass_rose_y - 0.005), ha='center', fontsize=10,
                xycoords='axes fraction')
    ax.annotate('', xy=(compass_rose_x + 0.03, compass_rose_y), xytext=(compass_rose_x, compass_rose_y),
                arrowprops=dict(arrowstyle='->', color='black'), xycoords='axes fraction')
    ax.annotate('E', xy=(compass_rose_x + 0.03, compass_rose_y), xytext=(compass_rose_x + 0.03, compass_rose_y - 0.005),
                ha='center', fontsize=10, xycoords='axes fraction')

# Plotting the data
fig, ax = plt.subplots(1, 1, figsize=(15, 10))

# Plot the state boundary
state_ny.plot(ax=ax, color='#D6E0E1',alpha=0.2)
# Plot the roads
roads_ny.plot(ax=ax, color='grey', linewidth=0.1)
# Plot the rails
rails_ny.plot(ax=ax, color='#7494CB', linewidth=1)

# # check EPSG code to confirm north south position:
# print(f"sate_ny: {state_ny.crs}")
# print(f"roads_ny: {roads_ny.crs}")
# print(f"rails_ny: {rails_ny.crs}")

# Adding compass rose
compass_rose(location=(0.075, 0.85))
# Adding scale bar
ax.add_artist(ScaleBar(1,location='lower left', scale_loc='bottom', length_fraction=.1, height_fraction=0.005,
                    border_pad=0.5, pad=0.5))

# Adding legend
ax.legend(["NY Roads","NY RailRoads"], loc='upper left')
# Adding title
plt.title('New York State Map with Roads and Rails as of 2022', fontsize=15)
# Remove x and y axis
ax.set_axis_off()

# Save the plot as a PDF
plt.savefig('./assignments/Alpha - US_Census_TIGER/output/NY_map_roads_rails.pdf')

# Show the plot
plt.show()

"""
create pdf page of sources and join to viz
"""
doc = SimpleDocTemplate("./assignments/Alpha - US_Census_TIGER/output/NY_map_roads_rails_sources.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

source_text = """
TIGER Map Layers:<br/>
1) New York State <br/>
2) New York Rails <br/>
3) New York Roads <br/>
<br/>

Sources:<br/>
<a href="https://tigerweb.geo.census.gov/tigerwebmain/Files/acs23/tigerweb_acs23_rail_ny.html" color="blue">US Census Bureau (exported to get NY rails)</a><br/>
<a href="https://walker-data.com/pygris/" color="blue">Walker Data</a><br/>
<a href="https://github.com/walkerke/pygris/tree/67ffcfc69a4f899cc668b1b9cf6426ee211822a4" color="blue">GitHub - pygris</a><br/>
<a href="https://geopandas.org/en/stable/docs.html" color="blue">GeoPandas Documentation</a><br/>
<br/>
Software: <br/>
Python, ChatGPT
"""

story.append(Paragraph(source_text, styles['Normal']))
story.append(Spacer(1, 12))
story.append(PageBreak())

doc.build(story)

"""
combine pdfs
"""
pdfs = ["./assignments/Alpha - US_Census_TIGER/output/NY_map_roads_rails.pdf", "./assignments/Alpha - US_Census_TIGER/output/NY_map_roads_rails_sources.pdf"]

merger = PdfMerger()

for pdf in pdfs:
    merger.append(pdf)

merger.write("./assignments/Alpha - US_Census_TIGER/output/NY_map_roads_rails_combined.pdf")
merger.close()
