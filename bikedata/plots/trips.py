import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd

def plot_hourly_trips(bs,kind,idxstart,idxend,idxstart_hl=None,idxend_hl=None):
    color = sns.color_palette()[0]

    f,ax = plt.subplots()

    
    if kind == 'stations':
        trips = bs.data.taken_hourly.sum(1)
    elif kind == 'bikes':
        trips = bs.data.free_bike_trips.set_index('time_start').groupby(pd.Grouper(freq='h')).size()
    elif kind == 'both':
        trips = bs.data.taken_hourly.sum(1) + bs.data.free_bike_trips.set_index('time_start').groupby(pd.Grouper(freq='h')).size()
    trips.index = trips.index.tz_convert(bs.tz)
    trips = trips[idxstart:idxend]


    trips_hl = trips[idxstart_hl:idxend_hl]


    ax.xaxis.set_major_locator(mdates.DayLocator(tz=trips.index.tz))

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%A",tz=trips.index.tz))
    #ax.xaxis.get_ticklabels()[-1].set_visible(False)
    ax.tick_params(axis='x',labelrotation=45)
    line = ax.plot(trips.index,trips.values,color=color)
    ax.fill_between(trips_hl.index,0,trips_hl.values,alpha=0.8,color=color)
    ax.fill_between(trips.index,0,trips.values,alpha=0.2,color=color)
    ax.xaxis.get_ticklabels()[-1].set_visible(False)
    ax.set_ylabel('Hourly trips')
    sns.despine()
    f.tight_layout()
    return f,ax
    
def plot_daily_trips(bs,kind,idxstart,idxend):
    f,ax = plt.subplots()

    if kind == 'stations':
        trips = bs.data.taken_hourly.sum(1)
    elif kind == 'bikes':
        trips = bs.data.free_bike_trips.set_index('time_start').groupby(pd.Grouper(freq='h')).size()
    elif kind == 'both':
        trips = bs.data.taken_hourly.sum(1) + bs.data.free_bike_trips.set_index('time_start').groupby(pd.Grouper(freq='h')).size()
        
    trips = trips.groupby(pd.Grouper(freq='d')).sum()
    trips = trips[idxstart:idxend]
    trips.index = trips.index.tz_convert(bs.tz)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.tick_params(axis='x',labelrotation=45)

    ax.bar(trips.index,trips.values)
    ax.xaxis.get_ticklabels()[-1].set_visible(False)
    ax.set_ylabel('Daily trips')
    sns.despine()
    f.tight_layout()
    return f,ax


def plot_alltime_trips(bs,kind):
    color = sns.color_palette()[0]

    f,ax = plt.subplots()

    if kind == 'stations':
        trips = bs.data.taken_hourly.sum(1)
    elif kind == 'bikes':
        trips = bs.data.free_bike_trips.set_index('time_start').groupby(pd.Grouper(freq='h')).size()
    elif kind == 'both':
        trips = bs.data.taken_hourly.sum(1) + bs.data.free_bike_trips.set_index('time_start').groupby(pd.Grouper(freq='h')).size()

    trips.index = trips.index.tz_convert(bs.tz)    
    trips = trips.groupby(pd.Grouper(freq='d')).sum()




    ax.xaxis.set_major_locator(mdates.YearLocator(tz=trips.index.tz))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y",tz=trips.index.tz))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(tz=trips.index.tz))

    ax.tick_params(axis='x',labelrotation=45)
    ax.plot(trips.index,trips.values)
    ax.set_ylabel('Daily trips')
    sns.despine()
    ax.grid(which='both')
    f.tight_layout()
    return f,ax