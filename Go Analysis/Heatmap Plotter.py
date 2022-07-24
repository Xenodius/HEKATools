import numpy as np
#from scipy import integrate
from scipy.ndimage.filters import gaussian_filter
#import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sqlalchemy
pd.set_option("display.max_columns", None)

rootpath = r'A:\Graphpad\GoExp'
Gopath = r'A:\Graphpad\GoExp\Experiments\Go\Go flx\Open Field\Raw Data'

print('Reading...')
#df = pd.read_pickle(rootpath + '\\' + 'heatmap_data.pkl').reset_index()
db_engine = sqlalchemy.create_engine('sqlite:///'+rootpath+'\\heatmap_data.db', echo=True) #Create db in root
df = pd.read_sql('SELECT * FROM finaldf', db_engine)
db_engine.dispose()

#df2 = df.sample(n=1000000, replace=False).reset_index()
print('Plotting...')

"""
Alternative themes;
#plotcolors = sns.color_palette("YlOrBr", as_cmap=True)
#plotcolors = sns.color_palette('vlag', as_cmap=True)
plotcolors = sns.color_palette("dark:salmon_r", as_cmap=True)
#sns.set_palette(plotcolors)
"""

df2 = df[['Centre posn X', 'Centre posn Y', 'group']].rename({'Centre posn X':'x', 'Centre posn Y':'y'}, axis=1)
df2['x'] = df2['x']*10 #Unit conversion
df2['y'] = df2['y']*10 #Unit conversion

dfsal = df2[df2['group']=='Saline'].reset_index().drop(['group','index'], axis='columns') #Clean/group for plot
dfmor = df2[df2['group']=='1mgkg'].reset_index().drop(['group','index'], axis='columns') #Clean for plot
dfnav = df2[df2['group']=='Naive'].reset_index().drop(['group','index'], axis='columns') #Clean for plot

#Generate heatmap histogram
heatmap, xedges, yedges = np.histogram2d(dfsal['x'], dfsal['y'], bins=128) #density=True for prob func
heatmap = gaussian_filter(heatmap, sigma=0.5) # Optional gaussian filter
#Plot heatmap
sns_plot = sns.heatmap(np.clip(heatmap, 0, 100), cmap='coolwarm')
sns_plot.figure.savefig(rootpath + '\\' + 'saline_heatmap.png')
sns_plot.figure.savefig(rootpath + '\\' + 'saline_heatmap.svg')
plt.clf()

heatmap, xedges, yedges = np.histogram2d(dfmor['x'], dfmor['y'], bins=128) #density=True for prob func
heatmap = gaussian_filter(heatmap, sigma=0.5) # Optional gaussian filter
sns_plot = sns.heatmap(np.clip(heatmap, 0, 100), cmap='coolwarm')
sns_plot.figure.savefig(rootpath + '\\' + '1mgkg_heatmap.png')
sns_plot.figure.savefig(rootpath + '\\' + '1mgkg_heatmap.svg')
plt.clf()

heatmap, xedges, yedges = np.histogram2d(dfnav['x'], dfnav['y'], bins=128) #density=True for prob func
heatmap = gaussian_filter(heatmap, sigma=0.5) # Optional gaussian filter
sns_plot = sns.heatmap(np.clip(heatmap, 0, 100), cmap='coolwarm')
sns_plot.figure.savefig(rootpath + '\\' + 'naive_heatmap.png')
sns_plot.figure.savefig(rootpath + '\\' + 'naive_heatmap.svg')
plt.clf()

print('Plotted')