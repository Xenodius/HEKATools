import numpy as np
#from scipy import integrate
import os
#import glob
import pandas as pd
#import seaborn as sns
#import matplotlib.pyplot as plt
from sylk_parser import SylkParser as sylk
from io import StringIO
#import sqlite3
import sqlalchemy
pd.set_option("display.max_columns", None)

rootpath = r'A:\Graphpad\GoExp'
datapath = r'A:\Graphpad\GoExp\Experiments\Go\Go flx\Open Field\Raw Data'

walk = [x for x in os.walk(datapath)][0][2] #Gather raw filepaths
dfpaths = pd.DataFrame.from_dict({'file': walk})
dfpaths['filepath'] = dfpaths['file']
dfpaths[['file', 'n']] = dfpaths['file'].str.split(' - Test ', expand=True) #Split filename into group, num.slk
dfpaths['n'] = dfpaths['n'].str.split('.', expand=True).iloc[:, 0] #split and discard .slk
dfpaths['file'] = dfpaths['file'].replace({'saline 2': 'Saline'}) #Clean saline 2/saline
dfpaths = dfpaths[['n', 'file', 'filepath']] #Reorder

finaldf = pd.DataFrame()
for row, file in enumerate(dfpaths['filepath']):
    print('Beginning ', file)
    group = dfpaths.loc[row]['file']
    #Parse SLK
    parser = sylk(datapath + '\\' + file)
    fbuf = StringIO()
    parser.to_csv(fbuf)
    parsedata = fbuf.getvalue()
    csvIO = StringIO(parsedata)
    df = pd.read_csv(csvIO)

    df = df.drop(df.loc[df['Centre posn X'] == ' '].index) #Clean null rows without position data
    df['Centre posn X'] = df['Centre posn X'].astype(int) #Numeric convert
    df['Centre posn Y'] = df['Centre posn Y'].astype(int)
    #Qlow = df['Centre posn X'].quantile(0.005)
    #Qhi = df['Centre posn X'].quantile(0.995)
    #df['Centre posn X'] = df['Centre posn X'].clip(Qlow, Qhi)
    #df['Centre posn Y'] = df['Centre posn Y'].clip(Qlow, Qhi)
    df['Centre posn X'] = df['Centre posn X'] - np.min(df['Centre posn X'])
    df['Centre posn Y'] = df['Centre posn Y'] - np.min(df['Centre posn Y'])
    df['Centre posn X'] = df['Centre posn X'] / df['Centre posn X'].max() * 100 # Normalize
    #df['Centre posn X'] = df['Centre posn X'] / Qhi * 100  # Normalize
    df['Centre posn Y'] = df['Centre posn Y'] / df['Centre posn Y'].max() * 100
    #df['Centre posn Y'] = df['Centre posn Y'] / Qlow * 100
    df['group'] = group
    finaldf = pd.concat([finaldf, df])

db_engine = sqlalchemy.create_engine('sqlite:///'+rootpath+'\\heatmap_data.db', echo=True) #Create db in root
finaldf.to_sql('finaldf', db_engine, if_exists='replace') #Overwrite processed file db
db_engine.dispose()

#cxn = sqlite3.connect(rootpath + '\\heatmap_data.db')
#finaldf.to_sql(name='finaldf', con=cxn)
##finaldf.to_pickle(rootpath + '\\' + 'heatmap_data.pkl') #Pickled as dataset too large for

print('done!')