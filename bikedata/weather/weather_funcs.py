import pandas as pd
import json
import urllib
import datetime as dt

def query_weather_day(bs,freq,day_timestamp):
    weather_url = f'https://api.darksky.net/forecast/{bs.DARKSKY_KEY}/{bs.lat},{bs.lon},{day_timestamp}?units=si'
    with urllib.request.urlopen(weather_url) as url:    
        data = json.loads(url.read().decode())
        
    hdf = pd.DataFrame(data['hourly']['data']).set_index('time')
    hdf.index = [dt.datetime.utcfromtimestamp(x) for x in hdf.index]
    hdf.index = hdf.index.tz_localize('UTC').tz_convert(bs.tz)

    ddf = pd.DataFrame(data['daily']['data']).set_index('time')
    ddf.index = [dt.datetime.utcfromtimestamp(x) for x in ddf.index]
    ddf.index = ddf.index.tz_localize('UTC').tz_convert(bs.tz)

    if freq == 'hourly':
        return hdf
    elif freq == 'daily':
        return ddf
    elif freq == 'both':
        return hdf,ddf
    else:
        raise ValueError("Unrecognized option for freq. Use hourly, daily or both")
                            
    return df


def get_weather_range(bs,freq,day1,day2=None):
    """
    bs: a BikeShareSystem object
    freq: 'daily' or 'hourly'
    day1,day2: pandas.Timestamp object representing the start and end days (inclusive)
    
    Returns a pandas.DataFrame
    
    """
    day1 = int(day1.value/10**9)
    if day2 is not None:
        day2 = int(day2.value/10**9)
    
    if day2 is None:
        df = query_weather_day(bs,freq,day1)
    else:
        days = [x for x in range(day1,day2+60*60*24,60*60*24)]
        df = pd.concat([query_weather_day(bs,freq,x) for x in days])
    

    
    return df