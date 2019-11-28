import pandas as pd
import os

class BikeShareSystemData(object):
    def __init__(self,workingdir='./'):
        self.workingdir = workingdir
        
        self.load()
        
        
    def load(self):
        self.stations = load_stations_csv(self)
        self.taken_hourly = load_taken_hourly_csv(self)
        self.returned_hourly = load_returned_hourly_csv(self)
        self.taken_bikes_hourly = load_taken_bikes_hourly_csv(self)
        self.returned_bikes_hourly = load_returned_bikes_hourly_csv(self)
        self.free_bike_trips = load_free_bikes_csv(self) 
        self.weather = load_weather_csv(self)
        
    def save(self):
        
        try:
            os.mkdir(f'{self.workingdir}/data/')
        except:
            pass
        
        
        if len(self.stations) > 0:
            self.stations.to_csv(f'{self.workingdir}/data/stations.csv', index=False)
        if len(self.taken_hourly) > 0:
            self.taken_hourly.reset_index().to_csv(f'{self.workingdir}/data/taken_hourly.csv', index=False)
        if len(self.returned_hourly) > 0:
            self.returned_hourly.reset_index().to_csv(f'{self.workingdir}/data/returned_hourly.csv', index=False)
        if len(self.taken_bikes_hourly) > 0:
            self.taken_bikes_hourly.reset_index().to_csv(f'{self.workingdir}/data/taken_bikes_hourly.csv', index=False)
        if len(self.returned_bikes_hourly) > 0:
            self.returned_bikes_hourly.reset_index().to_csv(f'{self.workingdir}/data/returned_bikes_hourly.csv', index=False)
        if len(self.free_bike_trips) > 0:
            self.free_bike_trips.to_csv(f'{self.workingdir}/data/free_bike_trips.csv', index=False)
        if len(self.weather) > 0:
            self.weather.reset_index().to_csv(f'{self.workingdir}/data/weather.csv',index=False)
        
 
    def clear(self):
        self.stations = pd.DataFrame()
        self.taken_hourly = pd.DataFrame()
        self.returned_hourly = pd.DataFrame()
        self.free_bike_trips = pd.DataFrame()  
        self.weather = pd.DataFrame()

def load_stations_csv(bsd):
    try:
        sdf = pd.read_csv(f'{bsd.workingdir}/data/stations.csv',dtype={'station_id':str})
    except:
        sdf = pd.DataFrame()
    return sdf

def load_taken_hourly_csv(bsd):
    try:
        thdf = pd.read_csv(f'{bsd.workingdir}/data/taken_hourly.csv',index_col=0,parse_dates=['time'])
    except:
        thdf = pd.DataFrame()
    return thdf

def load_returned_hourly_csv(bsd):
    try:
        rhdf = pd.read_csv(f'{bsd.workingdir}/data/returned_hourly.csv',index_col=0,parse_dates=['time'])
    except:
        rhdf = pd.DataFrame()
    return rhdf


def load_taken_bikes_hourly_csv(bsd):
    try:
        thdf = pd.read_csv(f'{bsd.workingdir}/data/taken_bikes_hourly.csv',index_col=0,parse_dates=['time'])
    except:
        thdf = pd.DataFrame()
    return thdf

def load_returned_bikes_hourly_csv(bsd):
    try:
        rhdf = pd.read_csv(f'{bsd.workingdir}/data/returned_bikes_hourly.csv',index_col=0,parse_dates=['time'])
    except:
        rhdf = pd.DataFrame()
    return rhdf

def load_free_bikes_csv(bsd):
    try:
        bikesdf = pd.read_csv(f'{bsd.workingdir}/data/free_bike_trips.csv',parse_dates=['time_start','time_end'],dtype={'bike_id':str})
    except:
        bikesdf = pd.DataFrame()
    return bikesdf 



def load_weather_csv(bsd):
    try:
        weatherdf = pd.read_csv(f'{bsd.workingdir}/data/weather.csv',index_col=0,parse_dates=['time'])
    except:
        weatherdf = pd.DataFrame()
    return weatherdf