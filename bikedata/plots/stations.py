from shapely.geometry import Point
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import seaborn as sns
from cartopy.io.img_tiles import MapboxStyleTiles,MapboxTiles, GoogleTiles
import cartopy.crs as ccrs



def plot_stations(bs,date1,date2=None):
    if date2 is None:
        date2 = date1
    
    color=sns.color_palette()[0]
    
    
    f,ax = plt.subplots(subplot_kw={'projection': ccrs.epsg(3857)},figsize=(7,7))

    tile = MapboxStyleTiles(bs.MAPBOX_TOKEN,'mjarrett','ck3gggjkl03gp1cpfm927yo7c')

    extent = [bs.lon_min,bs.lon_max,bs.lat_min,bs.lat_max]
    ax.set_extent(extent)
    ax.add_image(tile,15,interpolation='spline36')
    
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)
    
    sdf = bs.data.stations
    sdf['geometry'] = [Point(xy) for xy in zip(sdf.lon, sdf.lat)]

    thdf = bs.data.taken_hourly
    thdf.index = thdf.index.tz_convert(bs.tz)
    thdf = thdf[date1:date2]
    thdf = thdf.sum(0).reset_index()

    thdf.columns = ['station_id','trips']
    
    sdf = pd.merge(sdf,thdf,how='inner',on='station_id')
    sdf = geopandas.GeoDataFrame(sdf)
    sdf.crs = {'init' :'epsg:4326'}
    sdf = sdf.to_crs({'init': 'epsg:3857'})
    sdf.plot(ax=ax,markersize='trips',color=color,alpha=0.7)
    
    l1 = ax.scatter([0],[0], s=10, edgecolors='none',color=color,alpha=0.7)
    l2 = ax.scatter([0],[0], s=100, edgecolors='none',color=color,alpha=0.7)
    l3 = ax.scatter([0],[0], s=10, marker='x',edgecolors='none',color=color,alpha=0.7)

    labels=['0','10','100']
    ax.legend([l3,l1,l2],labels,title=f'Station Activity')
    
    return f,ax