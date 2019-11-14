import pandas as pd
import json
import urllib
import datetime

gbfs_master_csv = 'https://raw.githubusercontent.com/NABSA/gbfs/master/systems.csv'

class BikeShareSystem(object):
    def __init__(self,system):
        self.system = system
        self.stations = pd.DataFrame()
        self.free_bikes = pd.DataFrame()
        
    def query_stations(self):
        df = query_station_status(self.system)
        self.stations = pd.concat([self.stations,df])
        return df
    
    def query_bikes(self):
        df = query_free_bikes(self.system)
        self.free_bikes = pd.concat([self.free_bikes,df])
        return df
    
    def query_station_info(self):
        self.station_info = query_station_info(self.system)
        return self.station_info
    
    def get_hourly_usage(self):
        tdf = make_taken_df(self.stations)
        thdf = tdf.groupby(pd.Grouper(freq='H')).sum()
        
        return thdf
    
    def get_hourly_returned(self):
        rdf = make_returned_df(self.stations)
        rhdf = rdf.groupby(pd.Grouper(freq='H')).sum()
        return rhdf

    def clear(self):
        self.stations = pd.DataFrame()
        self.free_bikes = pd.DataFrame()
    
    
def get_sys_url(system):
    """
    Get GBFS url for a given System ID
    """
    
    df = pd.read_csv(gbfs_master_csv)

    url = df.loc[df['System ID']==system,'Auto-Discovery URL'].values[0]

    return url


def get_station_status_url(system):
    sys_url = get_sys_url(system)
    with urllib.request.urlopen(sys_url) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='station_status'][0]['url']      

def get_station_info_url(system):
    sys_url = get_sys_url(system)
    with urllib.request.urlopen(sys_url) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='station_information'][0]['url']   

def query_station_status(system):
    
    url = get_station_status_url(system)
    
    
    with urllib.request.urlopen(url) as data_url:
        data = json.loads(data_url.read().decode())
    
    df = pd.DataFrame(data['data']['stations'])
    # drop inactive stations
    df = df[df.is_renting==1]
    df = df[df.is_returning==1]
    df = df.drop_duplicates(['station_id','last_reported'])
    df.last_reported = df.last_reported.map(lambda x: datetime.datetime.fromtimestamp(x))
    df['time'] = datetime.datetime.now()
    return df



def query_station_info(system):
    url = get_station_info_url(system)
    
    with urllib.request.urlopen(url) as data_url:
        data = json.loads(data_url.read().decode())  
    
    return pd.DataFrame(data['data']['stations'])
    
def make_taken_df(df):
    pdf = pd.pivot_table(df,columns='station_id',index='time',values='num_bikes_available')
    ddf = pdf.copy()
    for col in pdf.columns:
        ddf[col] = pdf[col] - pdf[col].shift(-1)
    takendf = ddf.fillna(0.0).astype(int)
    takendf[takendf>0] = 0
    takendf = takendf*-1

    return takendf

def make_returned_df(df):
    pdf = pd.pivot_table(df,columns='station_id',index='time',values='num_bikes_available')
    ddf = pdf.copy()
    for col in pdf.columns:
        ddf[col] = pdf[col] - pdf[col].shift(-1)
    returneddf = ddf.fillna(0.0).astype(int)
    returneddf[returneddf<0] = 0

    return returneddf

def query_free_bikes(system):
    url = get_free_bike_url(system)
    
    with urllib.request.urlopen(url) as data_url:
        data = json.loads(data_url.read().decode())
    
    df = pd.DataFrame(data['data']['bikes'])
    df['time'] = datetime.datetime.now()
    return df
    
def get_free_bike_url(system):
    sys_url = get_sys_url(system)
    with urllib.request.urlopen(sys_url) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='free_bike_status'][0]['url']   


def get_free_bike_trips(df):
    df['coords'] = [(x,y) for x,y in zip(df.lat,df.lon)]
    trips = pd.DataFrame(df.groupby('bike_id')['coords'].unique())
    trips['trips'] = trips.coords.map(len)
    return trips

