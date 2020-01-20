# Bikedata

A package for processing real-time [GBFS bikeshare feeds](https://github.com/NABSA/gbfs). This package is experimental and subject to change at any time.


## Installation

`pip install git+https://github.com/mjarrett/bikedata.git`

## Usage

The Bikedata package provides an interface for querying GBFS bikeshare feeds and returning Pandas dataframes. The system name is determined by the System ID field in [systems.csv](https://github.com/NABSA/gbfs/blob/master/systems.csv).

```
import bikedata

bs = bd.BikeShareSystem('mobi_bikes')

station_data = bs.query_stations()
free_bike_data = bs.query_bikes()
station_info = bs.query_station_info()
```

## conf.py
When initializing a bikedata.BikeShareSystem object, the package will look for an optional conf.py file in the current directory. This file may contain some or all of the following fields:

```
system = 'mobi_bikes' # System name
url = 'https://vancouver-gbfs.smoove.pro/gbfs/gbfs.json'  # feed URL


DARKSKY_KEY = '' # DarkSky API key (for querying weather in system city)
MAPBOX_TOKEN = '' # MapBox API key (for creating system maps) 


# Rectangular bounds of system (for mapping)
lon_min = -123.185
lon_max = -123.056
lat_min = 49.245
lat_max = 49.315

# System timezone
tz = 'America/Vancouver'
```


## Persistent monitoring
The `bikedata.BikeShareSystem` class also exposes the `bs.monitor()` method for persistent monitoring of a bikeshare system. This method will run until killed, periodically querying the GBFS feed, computing trip counts and saving data files. Use with your daemon application of choice.

```
import bikedata

bs = bd.BikeShareSystem('mobi_bikes')
bs.monitor(save_backups=False, # save intermediary files
	save_interval=600, # seconds
	query_interval=60, # seconds
	track_stations=True, # track stations
	track_bikes=True     # track free bikes
```
Data files are saved in the `./data/` sub directory. To retrieve saved data run: `bs.load_data()`. The data will be held in Pandas dataframes as children of `bs.data`.

Use `bs.load_data(clean=True)` to convert times to system timezone (from UTC) and convert station ids to station names.



## Plotting
Some plotting functions are provided in the bikedata.plots submodule. Matplotlib and cartopy are required.
```
import bikedata as bd
import bikedata.plots as bdp

bs = bd.BikeShareSystem()
bs.load_data(clean=True)

# Plot daily trip counts with weather subplot
f,ax = plt.subplots(2,sharex=True,gridspec_kw={'height_ratios':[4.5,1]})
bdp.plot_daily_trips(bs,'stations',day1,day2,ax=ax[0])
bdp.plot_daily_weather(bs,day1,day2,ax[1])

# Plot hourly trip counts with weather subplot
f,ax = plt.subplots(2,sharex=True,gridspec_kw={'height_ratios':[4.5,1]})
bdp.plot_hourly_trips(bs,'stations',yday_min7,today,yday,ax=ax[0])
bdp.plot_hourly_weather(bs,day1,day2,ax[1])

# Plot station activity on day1 on a map
f,ax = bdp.plot_stations(bs,day1)

```
