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


def make_taken_free_bikes(df):
    # Count how many bikes are reported at each query time
    df = df['bike_id'].groupby(df.index).agg(lambda x: len(set(x.values)))
    # Count the change in reported bikes at each query time
    df = df - df.shift(1)
    
    takendf = df.fillna(0.0).astype(int)
    takendf[takendf>0] = 0
    takendf = takendf*-1
    takendf.name = 'trips'
    return takendf

def make_returned_free_bikes(df):
    # Count how many bikes are reported at each query time
    df = df['bike_id'].groupby(df.index).agg(lambda x: len(set(x.values)))
    # Count the change in reported bikes at each query time
    df = df - df.shift(1)
    returneddf = df.fillna(0.0).astype(int)
    returneddf[returneddf<0] = 0
    returneddf.name = 'trips'
    return returneddf


def make_taken_free_bikes_grid(df,grid):
    
    df = df.reset_index().drop_duplicates(['bike_id','time']).set_index('time')
    df['coords'] = list(zip(df.lat,df.lon))
    
    
    gdf = geopandas.GeoDataFrame(df)

    gdf['geometry'] = geopandas.points_from_xy(gdf.lon,gdf.lat)

    gdf.crs = {'init' :'epsg:4326'}
    gdf = gdf.to_crs({'init': 'epsg:3857'}) 
    
    # Merge grid and bikes so that each bike has the FID of a grid. If not in the city grid,
    # set FID = -1 
    mdf = geopandas.sjoin(grid,gdf.reset_index(),op='contains',how='right')    
    mdf.FID = mdf.FID.fillna(-1).astype(int)
    
    pdf = pd.pivot_table(mdf,values='coords',index='time',columns='FID',aggfunc='count')
    
    ddf = pdf.copy()
    for col in pdf.columns:
        ddf[col] = pdf[col] - pdf[col].shift(-1)
    takendf = ddf.fillna(0.0).astype(int)
    takendf[takendf>0] = 0
    takendf = takendf*-1

    takendf.columns = takendf.columns.astype(str)
    
    return takendf

def make_returned_free_bikes_grid(df,grid):
    
    df = df.reset_index().drop_duplicates(['bike_id','time']).set_index('time')
    df['coords'] = list(zip(df.lat,df.lon))
    gdf = geopandas.GeoDataFrame(df)

    gdf['geometry'] = geopandas.points_from_xy(gdf.lon,gdf.lat)

    gdf.crs = {'init' :'epsg:4326'}
    gdf = gdf.to_crs({'init': 'epsg:3857'}) 
    
    # Merge grid and bikes so that each bike has the FID of a grid. If not in the city grid,
    # set FID = -1 
    mdf = geopandas.sjoin(grid,gdf.reset_index(),op='contains',how='right')    
    mdf.FID = mdf.FID.fillna(-1).astype(int)
    
    pdf = pd.pivot_table(mdf,values='coords',index='time',columns='FID',aggfunc='count')
    
    ddf = pdf.copy()
    for col in pdf.columns:
        ddf[col] = pdf[col] - pdf[col].shift(-1)
    returneddf = ddf.fillna(0.0).astype(int)
    returneddf[returneddf<0] = 0
    returneddf.columns = returneddf.columns.astype(str)
    return returneddf

def run_persistent_query(bs, save_backups=False,save_interval=600,
                         query_interval=60,weather=True,
                         track_stations=True, track_bikes=True):

    try:
        os.mkdir(f'{bs.workingdir}/data/')
    except:
        pass
    
    try:
        ddf = pd.read_csv(f'{bs.workingdir}/data/station_data.tmp',dtype={'station_id':str}, parse_dates=['time'], index_col=0)
        ddf = ddf[ddf.time > now() - dt.timedelta(seconds=60*10)]
    except:
        ddf = pd.DataFrame()
        
    try:
        bdf = pd.read_csv(f'{bs.workingdir}/data/free_bikes.tmp',dtype={'bike_id':str}, parse_dates=['time'])
        bdf = bdf.set_index('time')
        bdf = bdf[bdf.index > now() - dt.timedelta(seconds=60*10)]
    except:
        bdf = pd.DataFrame()
    
    querytime = now()
    savetime = now() + dt.timedelta(seconds=save_interval)
    
    while True:
        
        if now() < querytime:
            continue
        else:
            querytime = now() + dt.timedelta(seconds=query_interval)
        
#        log("Query API")

        if track_stations:
            station_query = bs.query_stations()
            ddf = pd.concat([ddf,station_query], sort=True)
            if len(ddf) > 0:
                ddf.reset_index().to_csv(f'{bs.workingdir}/data/station_data.tmp', index=False)


        if track_bikes:
            bike_query = bs.query_bikes()
            bdf = pd.concat([bdf, bike_query], sort=True)

            if len(bdf) > 0:
                bdf.reset_index().to_csv(f'{bs.workingdir}/data/free_bikes.tmp', index=False)
        
        ## Periodically update CSV files 
        if now() < savetime:
            continue
        else:
            
            log("Update saved files")
            savetime = now() + dt.timedelta(seconds=save_interval)
            hour = dt.datetime.utcnow().hour         
            date_str = now().strftime('%Y%m%d%H%M')
            
            
            # Load data
            bs.load_data()
            
            
            ## Update stations csv
            if track_stations:
                bs.data.stations = pd.concat([bs.data.stations,bs.query_station_info()],sort=True)
                bs.data.stations = bs.data.stations.drop_duplicates(subset=['station_id'])
                bs.data.stations['active'] = bs.data.stations.station_id.isin(bs.query_stations().station_id)
            
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
            
            if track_stations and len(ddf) > 0:
                
                if save_backups:
                    os.rename(f'{bs.workingdir}/data/station_data.tmp',f'{bs.workingdir}/data/station_data{date_str}.csv')
                
                

                    
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
                
                ## Keep the last 5 minutes of station queries
                if len(ddf) > 0:
                    ddf = ddf[ddf.index > now() - dt.timedelta(minutes=5)]

                
                
            ## Process free bike trips
            if track_bikes and len(bdf) > 0:
                
                if save_backups:
                    os.rename(f'{bs.workingdir}/data/free_bikes.tmp',f'{bs.workingdir}/data/free_bikes{date_str}.csv')
               

                tdf = make_taken_free_bikes(bdf)
                bs.data.taken_bikes_hourly = pd.concat([bs.data.taken_bikes_hourly,tdf], sort=True)
                bs.data.taken_bikes_hourly = bs.data.taken_bikes_hourly.groupby(pd.Grouper(freq='H')).sum() 

                rdf = make_returned_free_bikes(bdf)
                bs.data.returned_bikes_hourly = pd.concat([bs.data.returned_bikes_hourly,tdf], sort=True)
                bs.data.returned_bikes_hourly = bs.data.returned_bikes_hourly.groupby(pd.Grouper(freq='H')).sum() 

                try:
                    bs.data.grid
                    tdf = make_taken_free_bikes_grid(bdf,bs.data.grid)
                    bs.data.taken_bikes_grid_hourly = pd.concat([bs.data.taken_bikes_grid_hourly,tdf], sort=True)
                    bs.data.taken_bikes_grid_hourly = bs.data.taken_bikes_grid_hourly.groupby(pd.Grouper(freq='H')).sum() 

                    rdf = make_returned_free_bikes_grid(bdf,bs.data.grid)
                    bs.data.returned_bikes_grid_hourly = pd.concat([bs.data.returned_bikes_grid_hourly,tdf], sort=True)
                    bs.data.returned_bikes_grid_hourly = bs.data.returned_bikes_grid_hourly.groupby(pd.Grouper(freq='H')).sum() 

                except AttributeError:
                    # If no grid ignore this
                    log("No city grid (bs.data.grid)")
                except Exception as e:
                    # Other error print and continue
                    log("Error when trying to create taken_grid csv")
                    log(e)

            

            

            ## Save and reset data
            bs.data.save()
            bs.data.clear()

            bdf = pd.DataFrame()
            ddf = pd.DataFrame()
            
            
def now():
    return pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC')
