import pandas as pd
import datetime as dt
import timeout_decorator 
import geopandas 
import sys
import os

def log(*args):
    args = [dt.datetime.now()] + list(args)
    print(*args,file=sys.stdout,flush=True)

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

def get_free_bike_trips(s):

    s = s.dropna()
    xs = s.map(lambda x: x[1])
    ys = s.map(lambda x: x[0])
    
    bike_id = s.name
    
    bdf = geopandas.GeoDataFrame(s,geometry=geopandas.points_from_xy(xs, ys), crs={'init':'epsg:4326'})
    bdf.columns = ['coords','geometry']

    bdf['geometry'] = bdf['geometry'].to_crs(epsg=26910)

    bdf['d_from'] = bdf.distance(bdf.shift(1))
    bdf['d_to'] = bdf.distance(bdf.shift(-1))
    bdf[['d_from','d_to']] = bdf[['d_from','d_to']].fillna(0).astype(int)

    # Ignore movement less than 50 meters
    bdf.loc[bdf['d_from']<50, 'd_from'] = 0 
    bdf.loc[bdf['d_to']<50, 'd_to'] = 0 

    bdf['trip_start'] = False
    bdf.loc[(bdf['d_from']==0) & (bdf['d_to'] > 0),'trip_start'] = True

    bdf['trip_end'] = False
    bdf.loc[(bdf['d_to']==0) & (bdf['d_from'] > 0),'trip_end'] = True

    idx_false_start = (bdf['trip_start'] == True) & (bdf['trip_end'].shift(1) == True) 
    idx_false_end = (bdf['trip_end'] == True) & (bdf['trip_start'].shift(-1) == True)

    bdf.loc[idx_false_start,'trip_start'] = False
    bdf.loc[idx_false_end,'trip_end'] = False

    starts = bdf[bdf.trip_start].reset_index()
    ends = bdf[bdf.trip_end].reset_index()

    starts['distance'] = starts.distance(ends)
    starts['bike_id'] = bike_id
    
    starts = starts.rename(columns={'time':'time_start','coords':'coords_start'})
    ends   = ends.rename(columns={'time':'time_end','coords':'coords_end'})

    tripsdf = pd.concat([starts.loc[:,['time_start','coords_start', 'distance','bike_id']], 
                         ends.loc[:,['time_end','coords_end']]], 
                        axis=1)
    tripsdf['lat_start'] = tripsdf['coords_start'].map(lambda x: x[0])
    tripsdf['lon_start'] = tripsdf['coords_start'].map(lambda x: x[1])
    tripsdf['lat_end'] = tripsdf['coords_end'].map(lambda x: x[0])
    tripsdf['lon_end'] = tripsdf['coords_end'].map(lambda x: x[1])
    del tripsdf['coords_start']
    del tripsdf['coords_end']
    
    return tripsdf


def run_persistent_query(bs, save_backups=False,save_interval=600,query_interval=60,weather=True):

        
    try:
        ddf = pd.read_csv('station_data.tmp',dtype={'station_id':str}, parse_dates=['time'], index_col=0)
        ddf = ddf[ddf.time > pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC') - dt.timedelta(seconds=60*10)]
    except:
        ddf = pd.DataFrame()
        
    try:
        bdf = pd.read_csv('free_bikes.tmp',dtype={'bike_id':str}, parse_dates=['time'])
        bdf = bdf.set_index('time')
        bdf = bdf[bdf.index > pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC') - dt.timedelta(seconds=60*10)]
    except:
        bdf = pd.DataFrame()
    
    querytime = pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC')
    savetime = pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC') + dt.timedelta(seconds=save_interval)
    
    while True:
        
        if pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC') < querytime:
            continue
        else:
            querytime = pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC') + dt.timedelta(seconds=query_interval)
        
#         log("Query API")
        station_query = bs.query_stations()
        ddf = pd.concat([ddf,station_query], sort=True)
        ddf.reset_index().to_csv(f'station_data.tmp', index=False)


        bike_query = bs.query_bikes()
        bdf = pd.concat([bdf, bike_query], sort=True)
        
        if len(bdf) > 0:
            bdf.reset_index().to_csv(f'free_bikes.tmp', index=False)
        
        ## Periodically update CSV files 
        if pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC') < savetime:
            continue
        else:
            
            log("Update saved files")
            savetime = pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC') + dt.timedelta(seconds=save_interval)
            hour = dt.datetime.utcnow().hour         
            date_str = pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC').strftime('%Y%m%d%H%M')
            
            
            # Load data
            bs.load_data()
            
            
            ## Update stations csv

            bs.data.stations = pd.concat([bs.data.stations,bs.query_station_info()])
            bs.data.stations = bs.data.stations.drop_duplicates(subset=['station_id'])
            
            ## Update weather csv
            if weather:
                bs.data.weather = pd.concat([bs.data.weather,bs.query_weather()])

                if len(bs.data.weather) > 0:
                    bs.data.weather = bs.data.weather.groupby(pd.Grouper(freq='h')).agg({'rh':'mean',
                                           'pres':'mean',
                                           'clouds':'mean',
                                           'wind_spd':'mean',
                                           'vis':'mean',
                                           'uv':'mean',
                                           'snow':'mean',
                                           'wind_dir':'first', 
                                           'elev_angle':'mean',
                                           'precip':'mean', 
                                           'sunrise':'first', 
                                           'sunset':'first', 
                                           'temp':'mean',
                                           'station':'first', 
                                           'app_temp':'mean',
                                           'ob_time':'first',
                                           'timezone':'first'
                                          })
            
            ## Update taken dataframe
            
            if len(ddf) > 0:
                
                if save_backups:
                    os.rename('station_data.tmp',f'station_data{date_str}.csv')
                
                

                    
                ddf['station_id'] = ddf['station_id'].astype(str)    
                tdf = make_taken_df(ddf)
                bs.data.taken_hourly = pd.concat([bs.data.taken_hourly,tdf], sort=True)
                bs.data.taken_hourly = bs.data.taken_hourly.groupby(pd.Grouper(freq='H')).sum() 
                    

                    
                rdf = make_returned_df(ddf)
                bs.data.returned_hourly = pd.concat([bs.data.returned_hourly,rdf], sort=True)
                bs.data.returned_hourly = bs.data.returned_hourly.groupby(pd.Grouper(freq='H')).sum() 
                
                # interpolate missing data
                #indx = pd.date_range(thdf.index[0],thdf.index[-1], freq='H')
                #thdf = thdf.reindex(indx).interpolate(method='time').astype(int)
                #thdf.index.name = 'time'
                
  
                
            else:
                log("Empty station tracking dataframe")
                
                
            ## Process free bike trips
            if len(bdf) > 0:
                
                if save_backups:
                    os.rename('free_bikes.tmp',f'free_bikes{date_str}.csv')
                

                    
                def pivot(bdf):
                    bdf['coords'] = list(zip(bdf.lat,bdf.lon))
                    pdf = pd.pivot_table(bdf, values='coords',index='time',columns='bike_id', aggfunc='first')
                    return pdf
                
                pdf = pivot(bdf)
                
                for col in pdf.columns:
                    bs.data.free_bike_trips = pd.concat([bs.data.free_bike_trips, get_free_bike_trips(pdf[col])])
                    
                if len(bs.data.free_bike_trips) > 0:
                    bs.data.free_bike_trips = bs.data.free_bike_trips.drop_duplicates(subset=['bike_id','time_start'], keep='last')
                    bs.data.free_bike_trips = bs.data.free_bike_trips.drop_duplicates(subset=['bike_id','time_end'], keep='first')
                    
            else:
                log("Empty bike tracking dataframe")
            

            ## Keep the last bike queries within the last 30 minutes
            if len(bdf) > 0:
                bdf = bdf[bdf.index > pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC') - dt.timedelta(minutes=30)]
            ## Keep the last 5 minutes of station queries
            if len(ddf) > 0:
                ddf = ddf[ddf.index > pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC') - dt.timedelta(minutes=5)]

            ## Save and reset data
            bs.data.save()
            bs.data.clear()

            

