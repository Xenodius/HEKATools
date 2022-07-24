import numpy as np
from scipy import integrate
import os
import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
pd.set_option("display.max_columns", None)
from sylk_parser import SylkParser as sylk
from io import StringIO

rootpath = r'A:\Graphpad\GoExp'
Gopath = r'A:\Graphpad\GoExp\Go'

walk = [x for x in os.walk(Gopath)][0][2]
dfwalk = pd.DataFrame.from_dict({'file': walk})
dfwalk['filepath'] = dfwalk['file']
dfwalk[['file', 'n']] = dfwalk['file'].str.split(' - Test ', expand=True) #Split filename into group, num.slk
dfwalk['n'] = dfwalk['n'].str.split('.', expand=True).iloc[:,0] #split and discard .slk
#Clean saline 2/saline
dfwalk['file'] = dfwalk['file'].replace({'saline 2':'Saline'})
#Reorder
dfwalk = dfwalk[['n', 'file', 'filepath']]

"""writer = pd.ExcelWriter(rootpath + '\\Go_OF_summary.xlsx', engine='xlsxwriter')
finaldata = pd.DataFrame()

for i in walk:
    titlen = len(i)
    title = i[0:(titlen-4)]
    data = pd.read_table(Gopath + '\\' + i)
    data['Group'] = title
    finaldata = finaldata.append(data)
    data.to_excel(writer, title[0:30])

finaldata.to_excel(writer, 'All')
writer.save()"""

"""for i in walk:
    print('Beginning ', i)
    parser = sylk(Gopath + '\\' + i)
    fbuf = StringIO()
    parser.to_csv(fbuf)
    parsedata = fbuf.getvalue()
    csvStringIO = StringIO(parsedata)
    df = pd.read_csv(csvStringIO)
    df = df.drop(df.loc[df['Centre posn X'] == ' '].index)
    df['Centre posn X'] = df['Centre posn X'].astype(int)
    df['Centre posn Y'] = df['Centre posn Y'].astype(int)

    bins = [x for x in range(0,505,5)]
    sns_plot = sns.displot(df, x='Centre posn X', y='Centre posn Y', bins=bins)
    sns_plot.savefig(rootpath + '\\' + i[0:(len(i)-4)])
    print('Done ', i)"""

finaldf = pd.DataFrame()
for row, file in enumerate(dfwalk['filepath']):
    print('Beginning ', file)
    group = dfwalk.loc[row]['file']
    #Parse SLK
    parser = sylk(Gopath + '\\' + file)
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

#writer = pd.ExcelWriter(rootpath + '\\' + 'heatmap_data.xlsx', engine='openpyxl')
finaldf.to_pickle(rootpath + '\\' + 'heatmap_data.pkl')

"""plotcolors = sns.color_palette('magma', as_cmap=True)
sns_plot = sns.displot(finaldf, col='group', x='Centre posn X', y='Centre posn Y', bins=[x for x in range(0,101,1)], palette=plotcolors)
sns_plot.savefig(rootpath + '\\' + 'heatmap.svg')"""


print('done!')