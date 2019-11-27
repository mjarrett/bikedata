try:
    import conf
except:
    pass

try:
    palette = conf.palette
except:
    palette = None
    
    
import seaborn as sns
sns.set(style='ticks', palette=palette)