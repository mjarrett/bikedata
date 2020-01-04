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








def plot_heatmap(bs,date1,date2=None):
    
    if date2 is None:
        date2 = date1
    
    trips = list(bs.data.taken_bikes[date1:date2].reset_index().itertuples(index=False, name=None))
    trips = [x[:5] for x in trips]
    trips_rolledout = []
    for trip in trips:
        trips_rolledout = trips_rolledout + [trip[:4]] * int(trip[4])


    trips_df = pd.DataFrame(trips_rolledout)

    trips_df.columns = ['time','coords','lat','lon']
    trips_df = trips_df.set_index('time')
    trips_df.index = pd.to_datetime(trips_df.index)


    extent = [bs.lon_min,bs.lon_max,bs.lat_min,bs.lat_max]


    bins=(100,100) 
    smoothing=1.3
    cmap='jet'

    #x = bs.data.taken_bikes.coords.map(lambda x: x[1])
    #y = bs.data.taken_bikes.coords.map(lambda x: x[0])
    x = trips_df.lon
    y = trips_df.lat

    heatmap, xedges, yedges = np.histogram2d(y, x, bins=bins, density=True,range=[extent[2:],extent[:2]])

    logheatmap = np.log(heatmap)
    logheatmap[np.isneginf(logheatmap)] = 0
    logheatmap = ndimage.filters.gaussian_filter(logheatmap, smoothing, mode='nearest')
    logheatmap = np.ma.masked_less(logheatmap,1)
    logheatmap.mask[0,:] = True
    logheatmap.mask[:,0] = True
    logheatmap.mask = ndimage.binary_closing(logheatmap.mask,border_value=0)
    logheatmap.mask[0,:] = True
    logheatmap.mask[:,0] = True
    
    
    
    
    f,ax = plt.subplots(subplot_kw={'projection': ccrs.epsg(3857)})

    tile = MapboxStyleTiles(bs.MAPBOX_TOKEN,'mjarrett','ck3gggjkl03gp1cpfm927yo7c')
    ax.set_extent(extent)
    ax.add_image(tile,15,interpolation='spline36')

    ax.outline_patch.set_visible(False)
    ax.background_patch.set_visible(False)

    # Make mesh
    lat = np.linspace(extent[0],extent[1],logheatmap.shape[0])
    lon = np.linspace(extent[2],extent[3],logheatmap.shape[1])

    Lat,Lon = np.meshgrid(lat,lon)




    ax.pcolormesh(Lat,Lon,logheatmap,alpha=0.6, transform=ccrs.PlateCarree())



    # if sdf is not None:
    #     sdf['geometry'] = [Point(xy) for xy in zip(sdf.lon, sdf.lat)]

    #     sdf = geopandas.GeoDataFrame(sdf)
    #     sdf.crs = {'init' :'epsg:4326'}
    #     sdf = sdf.to_crs({'init': 'epsg:3857'})

    #     sdf.plot(ax=ax,markersize=1,color='k')


    ax.axis('off')
    
    return f, ax