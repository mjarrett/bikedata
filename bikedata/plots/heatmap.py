import pandas as pd
from glob import glob
import matplotlib.pyplot as plt

import geopandas


from cartopy.io.img_tiles import MapboxTiles, GoogleTiles, MapboxStyleTiles
import cartopy.crs as ccrs

from shapely.geometry import Point, LineString, Polygon, shape
import numpy as np

import numpy as np
from scipy import ndimage








def plot_heatmap(bs):
    bdf = bs.data.free_bike_trips
    
    bdf['trip_time'] = bdf.time_end - bdf.time_start
    bdf['geom_start'] = [Point(xy) for xy in zip(bdf.lon_start, bdf.lat_start)]
    bdf['geom_end'] = [Point(xy) for xy in zip(bdf.lon_end, bdf.lat_end)]
    bdf['geom_trip'] = [LineString([x,y]) for x,y in zip(bdf.geom_start,bdf.geom_end)]

    bdf = geopandas.GeoDataFrame(bdf)
    bdf.geometry = bdf['geom_trip']
    bdf.crs = {'init' :'epsg:4326'}
    bdf = bdf.to_crs({'init': 'epsg:3857'})


    
    extent = [bs.lon_min,bs.lon_max,bs.lat_min,bs.lat_max]

    bdf.geometry = bdf['geom_start']

    logheatmap = make_heatmap(bs,bdf,extent)

    sdf = bs.data.stations


    f,ax = draw_heatmap(bs,logheatmap,extent,sdf)

    return f,ax
    
def make_heatmap(bs,gdf,extent):
    bins=(100,100) 
    smoothing=1.3
    cmap='jet'

    x = gdf.geometry.x
    y = gdf.geometry.y

    heatmap, xedges, yedges = np.histogram2d(y, x, bins=bins, density=True,range=[extent[2:],extent[:2]])

    logheatmap = np.log(heatmap)
    logheatmap[np.isneginf(logheatmap)] = 0
    logheatmap = ndimage.filters.gaussian_filter(logheatmap, smoothing, mode='nearest')
    logheatmap = np.ma.masked_less(logheatmap,1)
    logheatmap.mask = ndimage.binary_closing(logheatmap.mask)
    
    logheatmap = np.flip(logheatmap,axis=0)
    
    return logheatmap



def draw_heatmap(bs,logheatmap,extent,sdf=None):
    

    f,ax = plt.subplots(subplot_kw={'projection': ccrs.epsg(3857)})

    tile = MapboxStyleTiles(bs.MAPBOX_TOKEN,'mjarrett','ck3gggjkl03gp1cpfm927yo7c')
    ax.set_extent(extent)
    ax.add_image(tile,15,interpolation='spline36')


    # Make mesh
    lat = np.linspace(extent[0],extent[1],logheatmap.shape[0])
    lon = np.linspace(extent[2],extent[3],logheatmap.shape[1])
    
    Lat,Lon = np.meshgrid(lat,lon)



    
    ax.pcolormesh(Lat,Lon,logheatmap,alpha=0.6, transform=ccrs.PlateCarree())



    if sdf is not None:
        sdf['geometry'] = [Point(xy) for xy in zip(sdf.lon, sdf.lat)]

        sdf = geopandas.GeoDataFrame(sdf)
        sdf.crs = {'init' :'epsg:4326'}
        sdf = sdf.to_crs({'init': 'epsg:3857'})
    
        sdf.plot(ax=ax,markersize=1,color='k')
    
    
    #ax.axis('off')
    #f.subplots_adjust(left=0, right=1, top=1, bottom=0)
    # make transparent 
    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)

    # no margin through axes
    #ax.set_xmargin(0)
    #ax.set_ymargin(0)
    #f.savefig("ubc.png")
    #f.savefig(fname,pad_inches=0,bbox_inches = 'tight')
    
    return f,ax



