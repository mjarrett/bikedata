import pandas as pd
import json
import urllib
import datetime as dt
import timeout_decorator

def is_known(bs):
    df = pd.read_csv(bs.gbfs_master_csv)
    if bs.system in df['System ID'].values:
        return True
    else:
        return False
        

def get_sys_url(bs):
    """
    Get GBFS url for a given System 
    """
    
    df = pd.read_csv(bs.gbfs_master_csv)

    url = df.loc[df['System ID']==bs.system,'Auto-Discovery URL'].values[0]

    return url


def get_sys_info(bs):
    """
    Get GBFS system info for a given System ID
    """
    
    df = pd.read_csv(bs.gbfs_master_csv)

    data = df.loc[df['System ID']==bs.system].iloc[0].to_dict()

    return data

def get_station_status_url(sys_url):
    with urllib.request.urlopen(sys_url) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='station_status'][0]['url']      

def get_station_info_url(sys_url):
    with urllib.request.urlopen(sys_url) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='station_information'][0]['url']   


def get_system_info_url(sys_url):
    with urllib.request.urlopen(sys_url) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='system_information'][0]['url']

@timeout_decorator.timeout(30) 
def query_system_info(bs):
    url = get_system_info_url(bs.url)

    with urllib.request.urlopen(url) as data_url:
        data = json.loads(data_url.read().decode())  

    return data

    
@timeout_decorator.timeout(30) 
def query_station_status(bs):
    
    url = get_station_status_url(bs.url)


    with urllib.request.urlopen(url) as data_url:
        data = json.loads(data_url.read().decode())


    df = pd.DataFrame(data['data']['stations'])
    # drop inactive stations
    df = df[df.is_renting==1]
    df = df[df.is_returning==1]
    df = df.drop_duplicates(['station_id','last_reported'])
    df.last_reported = df.last_reported.map(lambda x: dt.datetime.utcfromtimestamp(x))
    df['time'] = data['last_updated']
    df.time = df.time.map(lambda x: dt.datetime.utcfromtimestamp(x))
    df = df.set_index('time')
    df.index = df.index.tz_localize('UTC')

    return df

@timeout_decorator.timeout(30) 
def query_station_info(bs):
    url = get_station_info_url(bs.url)

    with urllib.request.urlopen(url) as data_url:
        data = json.loads(data_url.read().decode())  

    return pd.DataFrame(data['data']['stations'])


@timeout_decorator.timeout(30) 
def query_free_bikes(bs):
    url = get_free_bike_url(bs.url)

    with urllib.request.urlopen(url) as data_url:
        data = json.loads(data_url.read().decode())

    df = pd.DataFrame(data['data']['bikes'])
    df['bike_id'] = df['bike_id'].astype(str)

    df['time'] = data['last_updated']
    df.time = df.time.map(lambda x: dt.datetime.utcfromtimestamp(x))
    df = df.set_index('time')
    df.index = df.index.tz_localize('UTC')

    return df
    
def get_free_bike_url(sys_url):
    with urllib.request.urlopen(sys_url) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='free_bike_status'][0]['url']

@timeout_decorator.timeout(30)
def query_weather(bs):
    
    """https://www.weatherbit.io/api/weather-current"""
    weather_url = f'https://api.weatherbit.io/v2.0/current/?lat={bs.lat_min}&lon={bs.lon_min}&units=M&key={bs.WEATHERBIT_KEY}'


    with urllib.request.urlopen(weather_url) as url:
        data = json.loads(url.read().decode())

    wdf = pd.DataFrame(data['data'][0])
    wdf.index = pd.to_datetime(wdf['ob_time'])
    wdf.index = wdf.index.tz_localize('UTC')#.tz_convert(tz)

    cols = ['rh', 'pres',
           'clouds', 'wind_spd',
           'vis', 'uv',
           'snow', 'wind_dir', 'elev_angle',
           'precip', 'sunrise', 'sunset', 'temp',
           'station', 'app_temp','ob_time','timezone'
           ]
    wdf = wdf[cols]

    wdf.index.name = 'time'

        
    return wdf
