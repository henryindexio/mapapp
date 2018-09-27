import pickle
import os
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from bokeh.io import output_file, show, curdoc
from bokeh.models import ColumnDataSource, GMapOptions, TextInput, Button, HoverTool
from bokeh.layouts import row, column, widgetbox
from bokeh.plotting import gmap

#Options
 

#Load google api key
GoogleAPIKey = os.environ['GoogleAPIKey']


#Load zip code data frame data
f = open('ZipcodeDistanceDf.pckl', 'rb')
NYZipcodeDistanceDf = pickle.load(f)
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
    CloseZipcodeDf = CloseZipcodeDf[CloseZipcodeDf['Distance']<5]
    
    #Recommend 5 zipcodes near search
    NumZipRecommend = 0
    i = 0
    ZipRecommend = []
    ScoreRecommend = []
    LonRecommend = []
    LatRecommend = []
    PopulationRecommend = []
    FemaleRatioRecommend = []
    IncomeRecommend = []
    PopDensityRecommend = []    

    while (NumZipRecommend < 5) and (i < CloseZipcodeDf.shape[0]): 
        ZipRow = CloseZipcodeDf.iloc[i,0]
        LonRow = CloseZipcodeDf.iloc[i,2]
        LatRow = CloseZipcodeDf.iloc[i,1]
        PredictRow = PredictDf[PredictDf['zip']==ZipRow]
        ModelRow = ModelDf[(ModelDf['zip']==ZipRow) & (ModelDf['year']==2016)]
        if not PredictRow.empty:
            Score = np.round(PredictRow['Score'].iloc[0]*100)/100
            Population = ModelRow['population'].iloc[0]
            FemaleRatio = ModelRow['FemaleRatio'].iloc[0]
            Income = ModelRow['Income'].iloc[0]
            PopDensity = np.round(ModelRow['PopDensity'].iloc[0]/.0000003880) 
            if Score > 5:
                ZipRecommend.append(ZipRow)
                ScoreRecommend.append(Score)
                LatRecommend.append(LatRow)
                LonRecommend.append(LonRow)
                PopulationRecommend.append(Population)
                FemaleRatioRecommend.append(FemaleRatio)
                IncomeRecommend.append(Income)
                PopDensityRecommend.append(PopDensity)
                NumZipRecommend = NumZipRecommend + 1            
        i = i + 1
   
    #Remove old map
    rootLayout = curdoc().get_model_by_name('column2')
    listOfSubLayouts = rootLayout.children
    plotToRemove = curdoc().get_model_by_name('plot2')
    listOfSubLayouts.remove(plotToRemove)
   
    #Create hovertool
    my_hover = HoverTool()
    my_hover.tooltips = [            
                ("Yogee Location Score", "@ScoreRecommend"),  
                ("Zip code", "@ZipRecommend"),                
                ("Population", "@PopulationRecommend"),
                ("Females per 100 males", "@FemaleRatioRecommend"),
                ("Median Income", "@IncomeRecommend"),
                ("Population Density", "@PopDensityRecommend")
    ]
          

    #Make map with recommended zipcodes
    map_options = GMapOptions(lat=np.mean(LatRecommend), lng=np.mean(LonRecommend), map_type="roadmap", zoom=11)
    p = gmap(GoogleAPIKey, map_options, title="Yogee", name='plot2')
    source = ColumnDataSource(
        data=dict(
                ZipRecommend=ZipRecommend,
                ScoreRecommend=ScoreRecommend,
                LatRecommend=LatRecommend,
                LonRecommend=LonRecommend,
                PopulationRecommend=PopulationRecommend,
                FemaleRatioRecommend=FemaleRatioRecommend,
                IncomeRecommend=IncomeRecommend,
                PopDensityRecommend=PopDensityRecommend
                
        )
    )
    p.circle(x="LonRecommend", y="LatRecommend", size=15, fill_color="purple", fill_alpha=0.8, source=source)
    p.add_tools(my_hover)
    plotToAdd = p
    listOfSubLayouts.append(plotToAdd)

#Text Input
text_input = TextInput(value="11220", title="Zipcode:")

#Search button
button = Button(label="Find Yoga Studio Location", button_type="success")
button.on_click(update)

#column 1
column1 = column([text_input] + [button])

#column 2
#add column 2
map_options = GMapOptions(lat=40.750672, lng=-73.9972808, map_type="roadmap", zoom=11)
p = gmap(GoogleAPIKey, map_options, title="Yogee", name='plot2')
source = ColumnDataSource(
    data=dict(lat=[],
              lon=[])
)
p.circle(x="lon", y="lat", size=15, fill_color="purple", fill_alpha=0.8, source=source)
column2 = column([p], name='column2')

#add columns to curdoc
curdoc().add_root(column1)
curdoc().add_root(column2)
curdoc().title = "Yogee"
