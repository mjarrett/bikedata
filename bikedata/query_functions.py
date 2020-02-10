import pandas as pd
import json
import urllib
import datetime as dt
import timeout_decorator
import ssl

        


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
    with urllib.request.urlopen(sys_url,context=ssl._create_unverified_context()) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='station_status'][0]['url']      

def get_station_info_url(sys_url):
    with urllib.request.urlopen(sys_url,context=ssl._create_unverified_context()) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='station_information'][0]['url']   


def get_system_info_url(sys_url):
    with urllib.request.urlopen(sys_url,context=ssl._create_unverified_context()) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='system_information'][0]['url']

@timeout_decorator.timeout(30) 
def query_system_info(bs):
    url = get_system_info_url(bs.url)

    with urllib.request.urlopen(url, context=ssl._create_unverified_context()) as data_url:
        data = json.loads(data_url.read().decode())  

    return data

    
@timeout_decorator.timeout(30) 
def query_station_status(bs):
    """
    Query station_status.json
    """
    
    url = get_station_status_url(bs.url)


    with urllib.request.urlopen(url, context=ssl._create_unverified_context()) as data_url:
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
    
    """
    Query station_information.json
    """
    url = get_station_info_url(bs.url)

    with urllib.request.urlopen(url, context=ssl._create_unverified_context()) as data_url:
        data = json.loads(data_url.read().decode())  

    return pd.DataFrame(data['data']['stations'])


@timeout_decorator.timeout(30) 
def query_free_bikes(bs):
    
    """
    Query free_bikes.json
    """
    
    url = get_free_bike_url(bs.url)

    with urllib.request.urlopen(url, context=ssl._create_unverified_context()) as data_url:
        data = json.loads(data_url.read().decode())

    df = pd.DataFrame(data['data']['bikes'])
    df['bike_id'] = df['bike_id'].astype(str)

    df['time'] = data['last_updated']
    df.time = df.time.map(lambda x: dt.datetime.utcfromtimestamp(x))
    df = df.set_index('time')
    df.index = df.index.tz_localize('UTC')

    return df
    
def get_free_bike_url(sys_url):
    with urllib.request.urlopen(sys_url, context=ssl._create_unverified_context()) as url:
        data = json.loads(url.read().decode())
    return [x for x in data['data']['en']['feeds'] if x['name']=='free_bike_status'][0]['url']


