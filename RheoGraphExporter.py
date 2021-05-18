import numpy as np
import pandas as pd
import os
from scipy import stats as scistat
from plotnine import *
from functools import reduce

def find_nth(hay, needle, n):
    start = hay.find(needle)
    while start >= 0 and n > 1:
        start = hay.find(needle, start+1)
        n -= 1
    return start

# Enable/disable all rows/columns or columns
# pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option("display.max_columns", None)

#Search path
path = r'C:\Program Files (x86)\HEKA2x903\Data\PyRheo'
outputpath = r'C:\Program Files (x86)\HEKA2x903\Data\PyRheo\Rheo_Data.xlsx'

if os.path.exists(outputpath) == True: # If Rheo output.xlsx file is present:
    print('Importing existing analysis output file.')
    #longframenan = pd.read_excel(outputpath)
    xls = pd.ExcelFile(outputpath, engine='openpyxl')
    longframenan = pd.read_excel(xls, 'Longform Data')
    longframemeans = pd.read_excel(xls, 'Means')
    rheobase = pd.read_excel(xls, 'Rheobase')
    longframe = longframenan.dropna()
    #alldata = pd.merge(longframenan, rheobase, on='ID', how='left')
else:
    print('What do you think you\'re doing?')


#For coloring by genotype/group:
longframenan['colorgroup'] = longframenan['genotype'] + longframenan['group']

#to find broken mixed-type cells:
"""for i in range(16769):
    if not type(longframenan['Rise Tau (ms)'].loc[i]) == float:
        print(i, type(longframenan['Rise Tau (ms)'].loc[i]), longframenan['Rise Tau (ms)'].loc[i])"""

#To fix broken mixed-type columns:
#longframenan['Time to Peak (ms)'] = longframenan['Time to Peak (ms)'].to_numeric()
#longframenan['Rise Tau (ms)'] = pd.to_numeric(longframenan['Rise Tau (ms)'])
#longframenan['Decay Tau (ms)'] = pd.to_numeric(longframenan['Decay Tau (ms)'])

#pull rheo_adj from excel
"""for i in longframenan['ID'].unique():
    id = '\'' + i + '\''
    try:
        adj = int(rheobase[rheobase['ID'] == id]['rheo_adj'])
    except Exception as e:
        adj = 0
        print('rheobase id exception:', e)
    mask = longframenan['ID'] == i
    loop_dict = longframenan[mask]['stim_pA'].apply(lambda x: x+adj).to_dict()
    for i in loop_dict.keys():
        longframenan.loc[i, 'stim_pA'] = loop_dict[i]"""


#Debug hook/check:
#print(longframenan.head(), '\n', rheobase)

#rheobase['rheobase'] = rheobase['rheobase_stim_pA'] + rheobase['rheo_adj']
longframenan['spikenum'] = longframenan['spikenum'].replace({0:np.nan})

lf_means = longframenan.groupby(['stim_pA', 'genotype', 'group']).agg([np.mean, scistat.sem]).reset_index()
#Flatten multiindex to _sem/_mean
lf_means.columns = ['_'.join(col).strip() for col in lf_means.columns.values]
#lf_sem = longframenan.groupby(['Trace', 'genotype', 'group']).agg(np.nanstd).reset_index()



"""rheoadjust = {}
for i in range(43):
    print(rheobase['ID'].loc[i], rheobase['rheo_adj'].loc[i])
    rheoadjust[rheobase['ID'].loc[i]] = rheobase['rheo_adj'].loc[i]"""

#longadj = pd.merge(longframenan, rheobase, how='outer', on=['ID', 'ID'])
#longadj['stim_adj'] = longadj['stim_pA'] + longadj['rheo_adj']

#mask = rheobase['ID'] == "'03-10_1_ctd2c_004-Rheo5'"

#rheo_id = ggplot(data=rheobase, mapping=aes(x='group', y='rheobase', color ='genotype'))


# DEBUG HOOK
#ldf = longframenan.copy()

#Graphpad outputter;
ldf = longframenan.copy()
#ldfagg = ldf.groupby(['colorgroup', 'stim_pA']).agg([np.mean, sem])
#writer = pd.ExcelWriter(path+'\\ldfagg.xlsx', engine='xlsxwriter')
#lf_means.to_excel(writer, 'Agg')
#writer.save()

ldflist = [rows for _, rows in ldf.groupby('colorgroup')]
#ldflist2 = [rows for _, rows in ldflist[0].groupby('ID')]
ldflist2 = []
for n, i in enumerate(ldflist):
    ldflist2.append([rows for _, rows in i.groupby('ID')])

#ldflist2[0][['date', 'cell', 'ID', 'stim_pA', 'frequency']]

#for n, i in enumerate(ldflist):
#    for nn, ii in enumerate(ldflist2):
#        print('group:', n, 'cell:', nn)
#        slice = ii['date', 'cell', 'ID', 'stim_pA', 'frequency']

writer = pd.ExcelWriter(path + '\\graphing.xlsx')

#Graphing tables for frequency
fdict = {}
for n, i in enumerate(ldflist2):
    group = i[0]['colorgroup'].unique()[0]
    fdict[group] = []
    for nn, ii in enumerate(i):
        print('group:', n, 'cell:', nn)
        val = str(n) + '_' + str(nn)
        #test[val] = ii[['date', 'cell', 'colorgroup', 'ID', 'Trace', 'stim_pA', 'frequency']].drop_duplicates(subset='stim_pA').set_index('stim_pA')
        #test[val] = ii[['stim_pA', 'frequency']].drop_duplicates(subset='stim_pA').set_index('stim_pA')
        fdict[group].append(ii[['stim_pA', 'frequency']].drop_duplicates(subset='stim_pA').set_index('stim_pA'))
        #slice = ii[['date', 'cell', 'ID', 'stim_pA', 'frequency']]
        #slicecols = slice.columns.tolist()
        #newcols = {}
        #for i in slicecols:
        #    newcols[i] = i + str(ii['cell'].unique()[0])
        #    print(newcols)
#convert dict to list
#testlist = []
#for i in test.keys():
#    testlist.append(test[i])
#pd.concat(testlist, join='outer', axis=1)
for i in fdict.keys():
    fdf = reduce(lambda df_left, df_right: pd.merge(df_left, df_right, on='stim_pA', how='outer'), fdict[i])
    fdf = fdf.dropna(how='all').sort_index(axis=0)
    title = i + '_frequency'
    fdf.to_excel(writer, title)
#fdf = reduce(lambda df_left,df_right: pd.merge(df_left, df_right, on='stim_pA', how='outer'), fdflist)

#Graphing Tables for Spikenumber
fdict = {}
for n, i in enumerate(ldflist2):
    group = i[0]['colorgroup'].unique()[0]
    fdict[group] = []
    for nn, ii in enumerate(i):
        print('group:', n, 'cell:', nn)
        val = str(n) + '_' + str(nn)
        fdict[group].append(ii[['stim_pA', 'spikenum']].drop_duplicates(subset='stim_pA').set_index('stim_pA'))
for i in fdict.keys():
    fdf = reduce(lambda df_left, df_right: pd.merge(df_left, df_right, on='stim_pA', how='outer'), fdict[i])
    fdf = fdf.dropna(how='all').sort_index(axis=0)
    title = i + '_spikenum'
    fdf.to_excel(writer, title)

#Graphing Tables for Rn arrays (unfit)
fdict = {}
for n, i in enumerate(ldflist2):
    group = i[0]['colorgroup'].unique()[0]
    fdict[group] = []
    for nn, ii in enumerate(i):
        print('group:', n, 'cell:', nn)
        val = str(n) + '_' + str(nn)
        #test[val] = ii[['date', 'cell', 'colorgroup', 'ID', 'Trace', 'stim_pA', 'frequency']].drop_duplicates(subset='stim_pA').set_index('stim_pA')
        #test[val] = ii[['stim_pA', 'frequency']].drop_duplicates(subset='stim_pA').set_index('stim_pA')
        df = ii[['stim_pA', 'R1S1Mean', 'frequency']].drop_duplicates(subset='stim_pA').reset_index().drop(columns='index')
        cutindex = df['frequency'].first_valid_index()-1
        fdict[group].append(df.loc[0:cutindex].drop(columns='frequency').set_index('stim_pA'))
        #fdict[group].append(ii[['stim_pA', 'R1S1Mean', 'frequency']].drop_duplicates(subset='stim_pA').set_index('stim_pA'))

for i in fdict.keys():
    fdf = reduce(lambda df_left, df_right: pd.merge(df_left, df_right, on='stim_pA', how='outer'), fdict[i])
    fdf = fdf.dropna(how='all').sort_index(axis=0)
    title = i + '_RnArrays'
    fdf.to_excel(writer, title)

writer.save()