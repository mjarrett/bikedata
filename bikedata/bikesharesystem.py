from .daemon_functions import *
from .query_functions import *
from .grid_functions import *
from .bikesharesystemdata import BikeShareSystemData



import sys


class BikeShareSystem(object):
    def __init__(self,*args,**kwargs):
        
        """
        BikeShareSystem(system=None,url=None)
        One or none of [system|url] is required
        system : Short name of bikeshare system according
        url    : Url of GBFS API 
        """
        
        self.gbfs_master_csv = 'https://raw.githubusercontent.com/NABSA/gbfs/master/systems.csv'

        
        if len(args) == 1:
            kwargs['system'] = args[0]
        elif len(args) > 1:
            raise ValueError("Too many arguments in constructor")
            
        if 'system' in kwargs.keys() and 'url' in kwargs.keys():
            raise ValueError("Too many arguments in constructor")
        
        if 'system' in kwargs.keys():
            self._system = kwargs['system']
            try:
                self.url = get_sys_url(self)
            except:
                self.url = None
                
        elif 'url' in kwargs.keys():
            self._system = None
            self.url = kwargs['url']
        else:
            self._system = None
            self.url = None
            
        if 'workingdir' in kwargs.keys():
            self.workingdir = os.path.abspath(kwargs['workingdir'])
        else:
            self.workingdir = './'
            
        
        
        
        self._load_conf()
        
        if self.url is None:
            try:
                self.url = get_sys_url(self)
            except:
                pass
            
        
        
        self._set_canon_latlon()
            
    def __repr__(self):
        if self.system is not None:
            return f"BikeShareSystem(system='{self.system}')"
        elif self.url is not None:
            return f"BikeShareSystem(url='{self.url}')"
        else:
            return f"BikeShareSystem()"
    

    @property
    def system(self):
        """
        System ID in https://github.com/NABSA/gbfs/blob/master/systems.csv
        """
        return self._system
    
    @system.setter
    def system(self,value):
        self._system = value
        try:
            self.url = get_sys_url(self)
        except: 
            self.url = None
    

        
    @property
    def taken_hourly_stations(self):
        """
        Retrieve hourly trip data from system stations
        """
        
        
        df = self.data.taken_hourly
        if len(df) > 0:
            return df
        else:
            return pd.DataFrame()
     
    @property
    def taken_hourly_free_bikes(self):
        """
        Retrieve free bike trip data
        """
        try:
            df = self.data.taken_bikes['trips'].groupby(pd.Grouper(freq='h')).sum()
            return df
        except:
            return pd.DataFrame()            
            
    
    def query_stations(self):
        """
        Query station_status.json
        """
        return  query_station_status(self)
        
    def query_bikes(self):
        """
        Query free_bikes.json
        """
        return  query_free_bikes(self)

        
    def query_station_info(self):
        """
        Query station_information.json
        """
        return query_station_info(self)
        
    def query_system_info(self):
        """
        Query system_information.json
        """
        return query_system_info(self)
       
        
    def monitor(self, save_backups=False,save_interval=600,
                         query_interval=60,
                         track_stations=True, track_bikes=True): 
        
        """
        This method will run until killed, periodically querying the GBFS feed, computing trip counts and saving data files. Us\
e with your daemon application of choice.

        bs = bd.BikeShareSystem('mobi_bikes)
        
        bs.monitor(save_backups=False, # save intermediary files
                    save_interval=600, # seconds
                    query_interval=60, # seconds
                    track_stations=True, # track stations
                    track_bikes=True     # track free bikes

        """
        
        
        run_persistent_query(self,save_backups=save_backups,
                             save_interval=save_interval,query_interval=query_interval,
                             track_stations=track_stations,
                             track_bikes=track_bikes)
    

    def load_data(self,clean=False):
        
        """
        Load saved data files created by BikeShareSystem.monitor() into Pandas dataframe
        """
        self.data = BikeShareSystemData(workingdir=self.workingdir)
        if clean:
            self.data.clean(self.tz)
            
    def now(self):
        return pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC').tz_convert(self.tz)
  

    def make_city_grid(self,resolution):
        gdf = make_city_grid(self,resolution)
        gdf.to_file(f'{self.workingdir}/data/city_grid.shp')
        return gdf
   

    def _load_conf(self):
        sys.path = [self.workingdir] + sys.path
        
        try:
            import conf
        except:
            return
        
        
        try:
            self.DARKSKY_KEY = conf.DARKSKY_KEY
        except:
            pass    
        try:
            self.MAPBOX_TOKEN = conf.MAPBOX_TOKEN
        except:
            pass
        try:
            self.WEATHERBIT_KEY = conf.WEATHERBIT_KEY
        except:
            pass
        try:
            self.system = conf.system
        except:
            pass
        
        try:
            self.lat_min = conf.lat_min
            self.lat_max = conf.lat_max
            self.lon_min = conf.lon_min
            self.lon_max = conf.lon_max
        except:
            pass
        
        try:
            self.tz = conf.tz
        except:
            self.tz = 'UTC'
            
        try:
            self.palette = conf.palette
        except:
            self.palette = None
            
        if self.url is None:
            try:
                self.url = conf.url
            except:
                pass

        
    def _set_canon_latlon(self):
        try:
            self.lat = (self.lat_min + self.lat_max)/2
            self.lon = (self.lon_min + self.lon_max)/2
            return 
        except (NameError, AttributeError):
            pass
        
        try:
            df = self.query_station_info()
            self.lat = df['lat'].mean()
            self.lon = df['lon'].mean()
            self.lat_min = df['lat'].min()
            self.lat_max = df['lat'].max()
            self.lon_min = df['lon'].min()
            self.lon_max = df['lon'].max()
            return
        except:
            pass
        
        try:
            df = self.query_bikes()
            self.lat = df['lat'].mean()
            self.lon = df['lon'].mean()
            self.lat_min = df['lat'].min()
            self.lat_max = df['lat'].max()
            self.lon_min = df['lon'].min()
            self.lon_max = df['lon'].max()
        except:
            pass
            