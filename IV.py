import csv
import numpy as np
import scipy as sp
import pandas as pd
import glob
import os
import xlsxwriter
from plotnine import *

# todo: fix day merge. Perhaps find a way to input unique ID's at beginning of parse, and merge from those?
#  Not sure if day_x or day_y or neither is correct. Appear to have duplicate values...
plotbool = input('Generate plots? y/n: ')

pd.set_option("display.max_columns", None)

#Search path
path = r'C:\Users\ckowalski\Dropbox\FileTransfers\Go basal parameters'
group_paths = [x[0] for x in os.walk(path)]
group_paths = group_paths[1:] # Slice removes root folder PyRheo leaving only subdirectories in PyRheo
group_parmpaths = []
group_dict = {}
# Map trace_start to mV. Two dicts for recently shortened protocol-- can deprecate
tracemap = {}
mVmap = [-100 + i for i in range(0, 170, 10)]
for count, i in enumerate(range(0, 17000, 1000)):
    tracemap[i] = mVmap[count]

for count, i in enumerate(group_paths):
    group_parmpaths.append(i + '\\parameters.xlsx')
    group_dict[count] = os.path.basename(i)


def find_nth(hay, needle, n):  # Helper string parsing-- index of nth instance of character 'needle' string 'haystack'
    start = hay.find(needle)
    while start >= 0 and n > 1:
        start = hay.find(needle, start+1)
        n -= 1
    return start

def parse_parameters(paths):  # Create one combined "Parameters" DF reindexed with 'index' for each 'day'
    output = pd.DataFrame()
    for count, i in enumerate(paths):
        df = pd.read_excel(i, index_col=0, engine='openpyxl')
        df['day'] = group_dict[count]
        output = df.append(output)
    output = output.reset_index()
    return output

def parse_IV(path, param):
    ivdf = pd.read_excel(path, index_col=1, engine='openpyxl', sheet_name=None)
    output = pd.DataFrame()
    for i in group_dict:
        date = group_dict[i]
        ivdf_sheet = ivdf[date].reset_index()
        ivdf_sheet['mV'] = ivdf_sheet['Trace'].apply(lambda x: -110+x*10)
        #ivdf_sheet = ivdf[date]
        #ivdf_sheet.insert(0, 'day', date)  # Get subsheet for date, add date to sheet

        # Get parameters matching date in ivdf[date] day column. Create matching FileName column.
        paramslice = param[param['day'].str.contains(date)]  # Get parameters for matching date
        paramslice = paramslice[paramslice['Series'].str.contains('IV')]
        paramslice['FileName'] = paramslice['index'].apply(lambda x: str(x).zfill(3) + '-IV.abf')
        # Convert Amps to pA
        paramslice['C-slow_1'] = paramslice['C-slow_1'].apply(lambda x: x / 1e-12)
        # Merge key parameters with corresponding series.
        ivdf_sheet = pd.merge(paramslice[['FileName', 'Time', 'day', 'Sweeps', 'Gain_1', 'C-slow_1', 'R-series_1']],
                              ivdf_sheet, how='right', on=['FileName', 'FileName'])
        # Append merged sheet to final DF
        output = ivdf_sheet.append(output)
    # Calculate pA/pF normalizations
    output['NaV_papf'] = output['R2S1Antipeak']/output['C-slow_1']
    output['Steady_papf'] = output['R2S1Mean'] / output['C-slow_1']
    # output['mV'] = output['TraceStart'].apply(lambda x: tracemap[x])
    return output.drop(axis=1, labels='Unnamed: 8')  # Not sure how this was produced in .append method...

fdf = pd.DataFrame()  # Final DF
parameters = parse_parameters(group_parmpaths)
ivdf = parse_IV(path + '\\IV.xlsx', parameters)

# Write sheet to enter groups
# Todo: only ask for template if no groups.xlsx
group_bool = os.path.exists(path + '\\groups.xlsx')
if group_bool:
    print('Groups.xlsx, detected, importing...')
    groupdf = pd.read_excel(path + '\\groups.xlsx', engine='openpyxl')
    # Generate unique ID from cell, genotype, condition. Maybe useful later.
    groupdf['id'] = groupdf.apply(lambda x: '%s_%s-%s-%s' % (x['day'], x['Cell'], x['Genotype'], x['Condition']), axis=1)
    ivdf = pd.merge(groupdf, ivdf, how='inner')  # Drops anything removed from groups.xlsx! For culling.
    #ivdf = pd.merge(groupdf, ivdf, how='right', on=['FileName', 'FileName']).drop_duplicates()
    writer = pd.ExcelWriter(path+'\\IV_Data.xlsx', engine='openpyxl')
    ivdf.to_excel(writer, 'Group ID\'s', index=False)
    writer.save()
else:
    print('No groups.xlsx, saving group template for entry...')
    groupdf = ivdf[['FileName', 'day']].drop_duplicates().reset_index(drop=True)
    groupdf['Cell'] = np.nan
    groupdf['Genotype'] = np.nan
    groupdf['Condition'] = np.nan
    writer = pd.ExcelWriter(path + '\\groups.xlsx', engine='openpyxl')
    groupdf.to_excel(writer, 'Group ID\'s', index=False)
    writer.save()

if plotbool == 'y':
    # + geom_errorbar(x='mV', ymin='NaV_papf-mean_se', ymax='NaV_papf+mean_se')\
    group_NaV = ggplot(data=ivdf,  mapping=aes(x='mV', y='NaV_papf', color='id'))\
                + geom_point(size=0.2)\
                + stat_summary(fun_data = 'mean_se')\
                + facet_grid('Genotype ~ Condition', space='free')\
                + theme_light()
    fig = group_NaV.draw()
    fig.set_size_inches(12, 6, forward=True)
    fig.savefig(path + '\\group_NaV.png', dpi=1000)

    cell_NaV = ggplot(data=ivdf,  mapping=aes(x='mV', y='NaV_papf', color='Genotype'))\
                + geom_point(size=0.2)\
                + facet_grid('day ~ Cell', space='free')\
                + theme_light()\
                + theme(aspect_ratio=8/3)
    fig = cell_NaV.draw()
    fig.savefig(path + '\\cell_NaV.png', dpi=600)
                # + stat_summary(fun.y = mean, )
else:
    pass



"""grouplist = []
for i in groupdf.drop_duplicates().reset_index(drop=True).iterrows():  # For unique files and per day;
    print('For file: ', i[1][0], 'on day: ', i[1][1])
    var = input('Enter group ID: ')
    grouplist.append(var)"""
# Add rows for Cslow compensated current
# Add a groups.xlsx to sort filenames into groups for plot faceting.
# Create plots of peak AND mean +/- SEM values faceted by group.

print('Complete!')

