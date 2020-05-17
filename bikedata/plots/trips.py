import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import datetime as dt

def plot_hourly_trips(bs,kind,date1,date2,date1_hl=None,date2_hl=None,ax=None):
    sns.set(style='ticks', palette=bs.palette)  
    color = sns.color_palette()[0]

    if ax is None:
        f,ax = plt.subplots()

    
    if kind == 'stations':
        trips = bs.taken_hourly_stations.sum(1)
    elif kind == 'floating':
        trips = bs.taken_hourly_free_bikes
    elif kind == 'hybrid':
        trips = bs.taken_hourly_free_bikes.add(bs.taken_hourly_stations.sum(1),fill_value=0)
    trips.index = trips.index.tz_convert(bs.tz)
    trips = trips[date1:date2]


    trips_hl = trips[date1_hl:date2_hl]

    
    line = ax.plot(trips.index,trips.values,color=color)

    
    ax.xaxis.set_major_locator(mdates.DayLocator(tz=trips.index.tz))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%A",tz=trips.index.tz))
    #ax.xaxis.get_ticklabels()[-1].set_visible(False)
    ax.tick_params(axis='x',labelrotation=45)
    ax.fill_between(trips_hl.index,0,trips_hl.values,alpha=0.8,color=color)
    ax.fill_between(trips.index,0,trips.values,alpha=0.2,color=color)
    try:
        ax.xaxis.get_ticklabels()[-1].set_visible(False)
    except:
        pass
    ax.set_ylabel('Hourly trips')
    sns.despine(top=True,bottom=True,left=True,right=True)
    ax.tick_params(axis=u'both', which=u'both',length=0)
    ax.grid(which='both')
    return ax
    
def plot_daily_trips(bs,kind,date1,date2,ax=None):
    
    sns.set(style='ticks', palette=bs.palette)  
    color = sns.color_palette()[0]
    
    if ax is None:
        f,ax = plt.subplots()

    if kind == 'stations':
        trips = bs.taken_hourly_stations.sum(1)
    elif kind == 'floating':
        trips = bs.taken_hourly_free_bikes
    elif kind == 'hybrid':
        trips = bs.taken_hourly_free_bikes.add(bs.taken_hourly_stations.sum(1),fill_value=0)
        
    trips = trips.groupby(pd.Grouper(freq='d')).sum()
    trips = trips[date1:date2]
    trips.index = trips.index.tz_convert(bs.tz)
    trips.index = [x - pd.Timedelta(6,'h') for x in trips.index]

    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.tick_params(axis='x',labelrotation=45)

    ax.bar(trips.index,trips.values,color=color)

    ax.set_ylabel('Daily trips')
    sns.despine(top=True,bottom=True,left=True,right=True)
    ax.tick_params(axis=u'both', which=u'both',length=0)
    ax.grid(which='both')
    return ax


def plot_alltime_trips(bs,kind,ax=None):
    sns.set(style='ticks', palette=bs.palette)  
    color = sns.color_palette()[0]
    color = sns.color_palette()[0]

    if ax is None:
        f,ax = plt.subplots()

    if kind == 'stations':
        trips = bs.data.taken_hourly.sum(1)
    elif kind == 'floating':
        trips = bs.data.free_bike_trips.set_index('time_start').groupby(pd.Grouper(freq='h')).size()
    elif kind == 'hybrid':
        trips = bs.taken_hourly_free_bikes.add(bs.taken_hourly_stations.sum(1),fill_value=0)

    trips.index = trips.index.tz_convert(bs.tz)    
    trips = trips.groupby(pd.Grouper(freq='d')).sum()
    trips = trips.iloc[:-1]



    ax.xaxis.set_major_locator(mdates.YearLocator(tz=trips.index.tz))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y",tz=trips.index.tz))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(tz=trips.index.tz))

    ax.tick_params(axis='x',labelrotation=45)
    ax.plot(trips.index,trips.values)
    ax.set_ylabel('Daily trips')
    sns.despine()
    ax.grid(which='both')
    return ax