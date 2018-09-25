import pickle
import os
from bokeh.io import output_file, show, curdoc
from bokeh.models import ColumnDataSource, GMapOptions, TextInput, Button
from bokeh.layouts import row, column
from bokeh.plotting import gmap
from bokeh.layouts import widgetbox

#Options
mapnum = 0
map_options = GMapOptions(lat=40.7128, lng=-74.0060, map_type="roadmap", zoom=11)
GoogleAPIKey = os.environ['GoogleAPIKey']

#Load zip code data frame data

f = open('ZipcodeDistanceDf.pckl', 'rb')
ModelDf = pickle.load(f)
f.close()

#Functions

def my_button_handler():
    curdoc().add_root(column2)

#Text Input
text_input = TextInput(value="10001", title="Zipcode:")

#Search button
button = Button(label="Find Yoga Studio Location", button_type="success")
button.on_click(my_button_handler)

#column 1
column1 = column([text_input] + [button])

# For GMaps to function, Google requires you obtain and enable an API key:
#
#     https://developers.google.com/maps/documentation/javascript/get-api-key
#
# Replace the value below with your personal API key:
p = gmap(GoogleAPIKey, map_options, title="Yogee")

source = ColumnDataSource(
    data=dict(lat=[40.7537, 40.7859, 40.7093, 40.7388, 40.7465],
              lon=[-73.9992, -73.9742, -74.0131, -73.9816, -74.0094])
)

p.circle(x="lon", y="lat", size=15, fill_color="purple", fill_alpha=0.8, source=source)

#column 2
column2 = column([p])

curdoc().add_root(column1)
curdoc().title = "Yogee"
