
#Load google api key
GoogleAPIKey = os.environ['GoogleAPIKey']

import pickle
import os
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from bokeh.io import output_file, show, curdoc
from bokeh.models import ColumnDataSource, GMapOptions, TextInput, Button, HoverTool, glyphs
from bokeh.layouts import row, column, widgetbox, layout
from bokeh.plotting import gmap

#Options
 
#Load google api key
f = open('/home/henry/Insight/APIKey/GooglePlacesAPIKey.pckl', 'rb')
GoogleAPIKey = pickle.load(f)
f.close()

#Load zip code distance data frame data
f = open('ZipcodeDistanceDf.pckl', 'rb')
NYZipcodeDistanceDf = pickle.load(f)
f.close()

#Load zip code boundary data frame data
f = open('ZipcodeBoundaryDf.pckl', 'rb')
ZipcodeBoundaryDf = pickle.load(f)
f.close()

#Load Yoga model dataset
f = open('ModelDf.pckl', 'rb')
ModelDf = pickle.load(f)
f.close()

#Load Yoga Score prediction
f = open('PredictDf.pckl', 'rb')
PredictDf = pickle.load(f)
f.close()

#Functions

#find closest zip codes given a zip code
def closestzipcode(Lon1,Lat1,ZipcodeDistanceDf):
    LonArray = np.float64(ZipcodeDistanceDf.loc[:,'Longitude'])
    LatArray = np.float64(ZipcodeDistanceDf.loc[:,'Latitude'])
    Lon1Radian = np.ones(np.size(LonArray))*(Lon1*(np.pi/180))
    Lat1Radian = np.ones(np.size(LatArray))*(Lat1*(np.pi/180))
    LonRadian = LonArray*(np.pi/180)
    LatRadian = LatArray*(np.pi/180)
    # haversine formula 
    DiffLon = LonRadian - Lon1Radian
    DiffLat = LatRadian - Lat1Radian
    a = np.square(np.sin(DiffLat/2)) + np.multiply(np.multiply(np.cos(Lat1Radian),np.cos(LatRadian)), np.square(np.sin(DiffLon/2)))
    c = 2 * np.arcsin(np.sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371* c
    mile = 0.621371 * km
    DistanceDF = pd.DataFrame(mile,columns=['Distance'])
    ZipcodeDistanceDf = pd.concat([ZipcodeDistanceDf, DistanceDF], axis=1, sort=False)
    ZipcodeDistanceDf = ZipcodeDistanceDf.sort_values('Distance', ascending=True)
    return ZipcodeDistanceDf

def update():

    #Find zipcodes nearby search 
    InputZipcode = text_input.value
    InputZipcode = np.int64(InputZipcode)
    InputZipRow = NYZipcodeDistanceDf[NYZipcodeDistanceDf['GEO.id2']==InputZipcode]
    InputLon = InputZipRow['Longitude'].iloc[0]
    InputLat = InputZipRow['Latitude'].iloc[0]
    CloseZipcodeDf = closestzipcode(InputLon,InputLat,NYZipcodeDistanceDf)
    CloseZipcodeDf = CloseZipcodeDf[CloseZipcodeDf['Distance']<10]

    #Recommend 5 zipcodes near search
    NumZipRecommend = 0
    i = 0
    ZipRecommend = []
    ScoreRecommend = []
    LonRecommend = []
    LatRecommend = []
    LonBoundaryRecommend = []
    LatBoundaryRecommend = []
    PopulationRecommend = []
    FemaleRatioRecommend = []
    IncomeRecommend = []
    PopDensityRecommend = []
    FillColor = []    
    Alpha = []

    while (NumZipRecommend < 5) and (i < CloseZipcodeDf.shape[0]): 
        ZipRow = CloseZipcodeDf.iloc[i,0]
        LonRow = CloseZipcodeDf.iloc[i,2]
        LatRow = CloseZipcodeDf.iloc[i,1]
        BoundaryRow = ZipcodeBoundaryDf[ZipcodeBoundaryDf['zip']==ZipRow]
        LonBoundary = BoundaryRow['LongitudeBoundary'].iloc[0]
        LatBoundary = BoundaryRow['LatitudeBoundary'].iloc[0]
        PredictRow = PredictDf[PredictDf['zip']==ZipRow]
        ModelRow = ModelDf[(ModelDf['zip']==ZipRow) & (ModelDf['year']==2016)]
        
        if not PredictRow.empty:
            Score = np.int(np.round(PredictRow['Score'].iloc[0]*10))
            Population = ModelRow['population'].iloc[0]
            FemaleRatio = ModelRow['FemaleRatio'].iloc[0]
            Income = ModelRow['Income'].iloc[0]
            PopDensity = np.round(ModelRow['PopDensity'].iloc[0]/.0000003880) 
            AlphaValue = ((Score-50)/62.5)+.1
            if Score > 50:
                ZipRecommend.append(ZipRow)
                ScoreRecommend.append(Score)
                LatRecommend.append(LatRow)
                LonRecommend.append(LonRow)
                LatBoundaryRecommend.append(LatBoundary)
                LonBoundaryRecommend.append(LonBoundary)
                PopulationRecommend.append(Population)
                FemaleRatioRecommend.append(FemaleRatio)
                IncomeRecommend.append(Income)
                PopDensityRecommend.append(PopDensity)
                FillColor.append('Purple')
                Alpha.append(AlphaValue)
                NumZipRecommend = NumZipRecommend + 1            
        i = i + 1      

    #Remove old map
    rootLayout = curdoc().get_model_by_name('column1')
    listOfSubLayouts = rootLayout.children
    plotToRemove = curdoc().get_model_by_name('plot1')
    listOfSubLayouts.remove(plotToRemove)
    if NumZipRecommend > 0:
        #Create hovertool
        my_hover = HoverTool()
        my_hover.tooltips = [            
                    ("Score", "@ScoreRecommend"),
                    ("Zip code", "@ZipRecommend"),                
                    ("Population", "@PopulationRecommend"),
                    ("Median Income", "@IncomeRecommend"),
                    ("Population Density", "@PopDensityRecommend")
        ]
              

        #Make map with recommended zipcodes
        map_options = GMapOptions(lat=np.mean(LatRecommend), lng=np.mean(LonRecommend), map_type="roadmap", zoom=12)
        p = gmap(GoogleAPIKey, map_options, title="Yogee", name='plot1')
        source = ColumnDataSource(
            data=dict(
                    ZipRecommend=ZipRecommend,
                    ScoreRecommend=ScoreRecommend,
                    LatRecommend=LatRecommend,
                    LonRecommend=LonRecommend,
                    LatBoundaryRecommend=LatBoundaryRecommend,
                    LonBoundaryRecommend=LonBoundaryRecommend,
                    PopulationRecommend=PopulationRecommend,
                    IncomeRecommend=IncomeRecommend,
                    PopDensityRecommend=PopDensityRecommend,
                    FillColor=FillColor,
                    Alpha=Alpha
                    
            )
        )

        #p.circle(x="LonRecommend", y="LatRecommend", size=15, fill_color="purple", fill_alpha=0.8, source=source)
        p.patches(xs="LonBoundaryRecommend", ys="LatBoundaryRecommend", fill_color="FillColor", alpha="Alpha", source=source)
        p.add_tools(my_hover)
        plotToAdd = p
        listOfSubLayouts.append(plotToAdd)
    else:
        map_options = GMapOptions(lat=InputLat, lng=InputLon, map_type="roadmap", zoom=12)
        p = gmap(GoogleAPIKey, map_options, title="Yogee", name='plot1')
        plotToAdd = p
        listOfSubLayouts.append(plotToAdd)

#Text Input
text_input = TextInput(placeholder="Type in Zipcode")

#Search button
button = Button(label="Find Locations", button_type="success")
button.on_click(update)

#Map
map_options = GMapOptions(lat=40.750672, lng=-73.9972808, map_type="roadmap", zoom=12)
p = gmap(GoogleAPIKey, map_options, name='plot1')

#layout 1
column1 = column([text_input,button,p], name='column1')

#add layout to curdoc
curdoc().add_root(column1)
curdoc().title = "Yogee"
