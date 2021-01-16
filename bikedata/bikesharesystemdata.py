import pandas as pd
import os
import sys
import geopandas

class BikeShareSystemData(object):
    def __init__(self,workingdir='./'):
        self.workingdir = workingdir
        
        self.load()
             
        try:
            self.stationxw = self.stations[['name','station_id']].set_index('station_id').to_dict()['name']
        except:
            self.stationxw = None
        self._clean = False
        
    def load(self):
        self.stations = load_stations_csv(self)
        self.taken_hourly = load_taken_hourly_csv(self)
        self.returned_hourly = load_returned_hourly_csv(self)
        self.taken_bikes = load_taken_bikes_csv(self)
        self.returned_bikes = load_returned_bikes_csv(self)
        self.grid  = load_grid(self)
    
    def clean(self,tz='UTC'):
        """
        Convert dataframe columns to human readable station names
        """

        self.taken_hourly = self.taken_hourly.rename(columns=self.stationxw)
        self.returned_hourly = self.returned_hourly.rename(columns=self.stationxw)
        self.taken_bikes = self.taken_bikes.rename(columns=self.stationxw)
        self.returned_bikes = self.returned_bikes.rename(columns=self.stationxw)
        
        self._clean = True
    
    def tz(self,tz='UTC'):
        """
        Convert data object to local timezone and human readable station names
        """

        self.taken_hourly.index = self.taken_hourly.index.tz_convert(tz)
        self.returned_hourly.index = self.returned_hourly.index.tz_convert(tz)
        self.taken_bikes.index = self.taken_bikes.index.tz_convert(tz)
        self.returned_bikes.index = self.returned_bikes.index.tz_convert(tz)
                     
        self._clean = True
        
    def save(self,force=False):
        
        if self._clean and not force:
            raise ValueError("Can't save dataframes: they've been converted to non-standard format")
        
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
        if len(self.taken_bikes) > 0:
            self.taken_bikes.reset_index().to_csv(f'{self.workingdir}/data/taken_bikes.csv', index=False)
        if len(self.returned_bikes) > 0:
            self.returned_bikes.reset_index().to_csv(f'{self.workingdir}/data/returned_bikes.csv', index=False)

        
 
    def clear(self):
        self.stations = pd.DataFrame()
        self.taken_hourly = pd.DataFrame()
        self.returned_hourly = pd.DataFrame()
        self.taken_bikes = pd.DataFrame()
        self.returned_bikes = pd.DataFrame()

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
        thdf.index = pd.to_datetime(thdf.index).tz_localize('UTC') # Need to make index tz aware
    return thdf

def load_returned_hourly_csv(bsd):
    try:
        rhdf = pd.read_csv(f'{bsd.workingdir}/data/returned_hourly.csv',index_col=0,parse_dates=['time'])
    except:
        rhdf = pd.DataFrame()
        rhdf.index = pd.to_datetime(rhdf.index).tz_localize('UTC') # Need to make index tz aware
    return rhdf


def load_taken_bikes_csv(bsd):
    try:
        thdf = pd.read_csv(f'{bsd.workingdir}/data/taken_bikes.csv',index_col=0,parse_dates=['time'])
    except:
        thdf = pd.DataFrame()
        thdf.index = pd.to_datetime(thdf.index).tz_localize('UTC') # Need to make index tz aware
    return thdf

def load_returned_bikes_csv(bsd):
    try:
        rhdf = pd.read_csv(f'{bsd.workingdir}/data/returned_bikes.csv',index_col=0,parse_dates=['time'])
    except:
        rhdf = pd.DataFrame()
        rhdf.index = pd.to_datetime(rhdf.index).tz_localize('UTC') # Need to make index tz aware
    return rhdf





def load_grid(bsd):
    try:
        gdf = geopandas.read_file(f'{bsd.workingdir}/data/city_grid.shp')
        gdf.crs = {'init' :'epsg:3857'}
        gdf.FID = gdf.FID.astype(int)
        return gdf
    except:
        return None




    
