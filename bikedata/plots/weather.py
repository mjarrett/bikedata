import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import bikedata.weather as bdw


def plot_daily_weather(bs,date1,date2,ax=None):
    df = bdw.get_weather_range(bs,'daily',date1,date2)
    
    
    if ax is None:
        f,ax = plt.subplots()
        
    ax2 = ax.twinx()

    ax.set_ylabel('High ($^\circ$C)')
    ax2.bar(df.index,df['precipIntensity'].values,color='#3778bf')
#     ax2.bar(df.index,df['precipIntensity'].values,color='#3778bf',zorder=1001,width=1/24)

    ax.plot(df.index,df['temperatureHigh'],color='#feb308',zorder=1000)
    ax2.set_ylabel('Precip (mm)')
    ax.yaxis.label.set_color('#feb308')
    ax2.yaxis.label.set_color('#3778bf')
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.tick_params(axis='x',labelrotation=45)
    ax2.tick_params(axis='x',labelrotation=45)
    
    ax.text(0,-1.4,'Powered by Dark Sky: https://darksky.net/poweredby/',transform=ax.transAxes,fontdict={'color':'grey','style':'italic','family':'serif','size':8})
    
    
    return ax,ax2


def plot_hourly_weather(bs,date1,date2,ax=None):
    df = bdw.get_weather_range(bs,'hourly',date1,date2)
    if ax is None:
        f,ax = plt.subplots()
        
    ax2 = ax.twinx()

    ax.set_ylabel('Temp ($^\circ$C)')
#     ax2.bar(df.index,df['precipIntensity'].values,color='#3778bf',zorder=1001,width=1/24)
    ax2.plot(df.index,df['precipIntensity'].values,color='#3778bf',zorder=1001)
    ax2.fill_between(df.index,0,df['precipIntensity'].values,alpha=0.8,color='#3778bf')
    ax.plot(df.index,df['temperature'],color='#feb308',zorder=1000)
    ax2.set_ylabel('Precip (mm)')
    ax.yaxis.label.set_color('#feb308')
    ax2.yaxis.label.set_color('#3778bf')
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.set_major_locator(mdates.DayLocator(tz=df.index.tz))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%A",tz=df.index.tz))
    ax.tick_params(axis='x',labelrotation=45)
    ax2.tick_params(axis='x',labelrotation=45)
    
    ax.text(0,-1.6,'Powered by Dark Sky: https://darksky.net/poweredby/',transform=ax.transAxes,fontdict={'color':'grey','style':'italic','family':'serif','size':8})
    
    
    return ax,ax2