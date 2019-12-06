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
            self.is_known = is_known(self)
            self._url = None
                
        elif 'url' in kwargs.keys():
            self._system = None
            self._url = kwargs['url']
            self.is_known = False
        else:
            self._system = None
            self._url = None
            self.is_known = False
            
        if 'workingdir' in kwargs.keys():
            self.workingdir = kwargs['workingdir']
        else:
            self.workingdir = './'
            
            
        
        self._load_conf()
        
        self._set_canon_latlon()
            
    def __repr__(self):
        if self.system is not None:
            return f"BikeShareSystem(system='{self.system}')"
        elif self.url is not None:
            return f"BikeShareSystem(url='{self.url}')"
        else:
            return f"BikeShareSystem()"
    
    @property
    def url(self):
        if self.is_known:
            return get_sys_url(self)
        else:
            return self._url
    
    @url.setter
    def url(self,value):
        if not self.is_known:
            self._url = value
        else:
            self._url = self._url
            
    @property
    def system(self):
        return self._system
    
    @system.setter
    def system(self,value):
        self._system = value
        self.is_known = is_known(self)
        if self.is_known:
            self._url = get_sys_url(self)
        else: 
            self._url = None
            
    def query_stations(self):
        try:
            return  query_station_status(self)
        except Exception as e:
#             log(e)
            return pd.DataFrame()
        
    def query_bikes(self):
        try:
            return  query_free_bikes(self)
        except Exception as e:
#             log(e)
            return pd.DataFrame()
        
    def query_station_info(self):
        try:
            return query_station_info(self)
        except Exception as e:
#             log(e)
            return pd.DataFrame()
        
    def query_system_info(self):
        try:
            return query_system_info(self)
        except Exception as e:
            return dict()
        
    def query_weather(self):
        try:
            return query_weather(self)
        except Exception as e:
#             log(e)
            return pd.DataFrame()
        

        
    def monitor(self, save_backups=False,save_interval=600,
                         query_interval=60,weather=False,
                         track_stations=True, track_bikes=True): 
        
        run_persistent_query(self,save_backups=save_backups,
                             save_interval=save_interval,query_interval=query_interval,
                             weather=weather, track_stations=track_stations,
                             track_bikes=track_bikes)
    

    def load_data(self,clean=False):
        self.data = BikeShareSystemData(workingdir=self.workingdir)
        if clean:
            self.data.clean(self.tz)
            
    def now(self):
        return pd.Timestamp(dt.datetime.utcnow()).tz_localize('UTC').tz_convert(self.tz)
  

    def make_city_grid(self,resolution):
        gdf = make_city_grid(self,resolution)
        gdf.to_file(f'{self.workingdir}/data/city_grid.shp')
        
   

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
            