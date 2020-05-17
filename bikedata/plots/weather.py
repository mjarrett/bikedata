import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import bikedata.weather as bdw
import seaborn as sns
import numpy as np


c_blue =     '#3286AD' #// primary
c_light_blue='#50AAD3'
c_indigo =   '#8357B2' #// info
c_red =      '#FF5B71' # // danger
c_yellow =   '#E5DE50' #// warning
c_green =    '#77ACA2' #// success


def plot_daily_weather(bs,date1,date2,ax=None):
    try:
        df = bdw.get_weather_range(bs,'daily',date1,date2)
    except:
        return None
    
    if ax is None:
        f,ax = plt.subplots()
        
    ax2 = ax.twinx()

    ax.set_ylabel('Daily high')
    ax2.bar(df.index,df['precipIntensity'].values*24,color=c_light_blue)
#     ax2.bar(df.index,df['precipIntensity'].values,color='#3778bf',zorder=1001,width=1/24)

    ax.plot(df.index,df['temperatureHigh'],color=c_yellow,zorder=1000)
    ax2.set_ylabel('Precipitation')
    ax.yaxis.label.set_color(c_yellow)
    ax2.yaxis.label.set_color(c_light_blue)
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.tick_params(axis='x',labelrotation=45)
    ax2.tick_params(axis='x',labelrotation=45)
    
    sns.despine(ax=ax,top=True,bottom=True,left=True,right=True)
    sns.despine(ax=ax2,top=True,bottom=True,left=True,right=True)
    ax.tick_params(axis='both', which='both',length=0)
    ax2.tick_params(axis='both', which='both',length=0)
    ax.grid(which='both')   
    
    ax.set_yticklabels([])
    ax2.set_yticklabels([])
    

    #ax.text(0,-1.4,'Powered by Dark Sky: https://darksky.net/poweredby/',transform=ax.transAxes,fontdict={'color':'grey','style':'italic','family':'serif','size':8})
    
    
    return ax,ax2


def plot_hourly_weather(bs,date1,date2,ax=None):
    try:
        df = bdw.get_weather_range(bs,'hourly',date1,date2)
    except:
        return None
    
    if ax is None:
        f,ax = plt.subplots()
        
    ax2 = ax.twinx()

    ax.set_ylabel('Temperature')
#     ax2.bar(df.index,df['precipIntensity'].values,color='#3778bf',zorder=1001,width=1/24)
    ax2.plot(df.index,df['precipIntensity'].values,color=c_light_blue,zorder=1001)
    ax2.fill_between(df.index,0,df['precipIntensity'].values,alpha=0.8,color=c_light_blue)
    ax.plot(df.index,df['temperature'],color=c_yellow,zorder=1000)
    ax2.set_ylabel('Precipitation')
    ax.yaxis.label.set_color(c_yellow)
    ax2.yaxis.label.set_color(c_light_blue)
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.set_major_locator(mdates.DayLocator(tz=df.index.tz))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%A",tz=df.index.tz))
    ax.tick_params(axis='x',labelrotation=45)
    ax2.tick_params(axis='x',labelrotation=45)
    
    if df['precipIntensity'].max()>2.5:
        ymax = df['precipIntensity'].max()
    else:
        ymax = 2.5
    ax2.set_ylim(0,ymax)
    
    #ax.text(0,-2.6,'Powered by Dark Sky: https://darksky.net/poweredby/',transform=ax.transAxes,fontdict={'color':'grey','style':'italic','family':'serif','size':8})
    sns.despine(ax=ax,top=True,bottom=True,left=True,right=True)
    sns.despine(ax=ax2,top=True,bottom=True,left=True,right=True)
    ax.tick_params(axis='both', which='both',length=0)
    ax2.tick_params(axis='both', which='both',length=0)
    ax.grid(which='both')   
    
    ax.set_yticklabels([])
    ax2.set_yticklabels([])
    return ax,ax2