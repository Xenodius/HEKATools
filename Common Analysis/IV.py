import csv
import numpy as np
from scipy import stats
import pandas as pd
import glob
import os
import xlsxwriter
from plotnine import *

#Search path
path = r'C:\Program Files (x86)\HEKA2x903\Data\PyRheo'
group_paths = [x[0] for x in os.walk(path)]
group_paths = group_paths[1:] # Slice removes root folder PyRheo leaving only subdirectories in PyRheo
group_parmpaths = []
group_dict = {}

#Fix day merge
plotbool = input('Generate plots? y/n: ')

pd.set_option("display.max_columns", None)

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

def gen_stats(df, cols):
    pass

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

    return output  # Not sure how this was produced in .append method...

parameters = parse_parameters(group_parmpaths)
ivdf = parse_IV(path + '\\IV.xlsx', parameters)

# Write sheet to enter groups
group_bool = os.path.exists(path + '\\groups.xlsx')
if group_bool:
    print('Groups.xlsx, detected, importing...')
    groupdf = pd.read_excel(path + '\\groups.xlsx', engine='openpyxl')

    # Generate unique ID from cell, genotype, condition. Maybe useful later.
    groupdf['id'] = groupdf.apply(lambda x: '%s_%s-%s-%s' % (x['day'], x['Cell'], x['Genotype'], x['Condition']), axis=1)
    ivdf = pd.merge(groupdf, ivdf, how='inner')  # Drops anything removed from groups.xlsx! For culling.

    # Generate traceID for trace/cell specific statistics mapping
    ivdf['traceid'] = ivdf.apply(
        lambda x: '%s-%s_%s' % (x['Trace'], x['Genotype'], x['Condition']), axis=1)

    # Generate statistics
    statdf = ivdf.groupby(by=['Trace', 'Genotype', 'Condition'], axis=0)\
        .agg({'Steady_papf':[np.mean, stats.sem], 'NaV_papf':[np.mean, stats.sem]})
    statcol = statdf.columns
    newcol = []
    for i in statcol:
        newcol.append(i[0] + '_' + i[1])
    statdf.columns = newcol
    statdf = statdf.reset_index()
    statdf.reset_index()
    statdf['mV'] = statdf['Trace'].apply(lambda x: -110 + x * 10)
    statdf['Steady_papf_sem_min'] = statdf.apply(lambda x: x['Steady_papf_mean'] - x['Steady_papf_sem'], axis=1)
    statdf['Steady_papf_sem_max'] = statdf.apply(lambda x: x['Steady_papf_mean'] + x['Steady_papf_sem'], axis=1)
    statdf['NaV_papf_sem_min'] = statdf.apply(lambda x: x['NaV_papf_mean'] - x['NaV_papf_sem'], axis=1)
    statdf['NaV_papf_sem_max'] = statdf.apply(lambda x: x['NaV_papf_mean'] + x['NaV_papf_sem'], axis=1)
    # Filter test groups
    statdf = statdf[statdf['Condition'] != 'morph2']
    statdf = statdf[statdf['Condition'] != 'recov2']
    # statdf['Steady_papf_sem_min'] = statdf[['Steady_papf_sem', 'Steady_papf_mean']].apply(lambda x: x['Steady_papf'])
    # statdf['NaV_papf_sem_min'] = statdf['NaV_papf_sem'].apply(lambda x: -x)
    # statdf['Steady_papf'] = ivdf.groupby(by='traceid', axis=0).apply(lambda x: stats.sem(x['Steady_papf']))
    # ivdf = pd.merge(groupdf, ivdf, how='right', on=['FileName', 'FileName']).drop_duplicates()

    print('Final data:', '\n', ivdf)
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
    print('Analysis saved.')

if plotbool == 'y':
    # + geom_errorbar(x='mV', ymin='NaV_papf-mean_se', ymax='NaV_papf+mean_se')\
    # Individual cells, genotype X condition
    grouped_cells_NaV = ggplot(data=ivdf, mapping=aes(x='mV', y='NaV_papf', color='id')) \
                        + geom_point(size=0.2) \
                        + facet_grid('Genotype ~ Condition', space='free') \
                        + theme_light()
    fig = grouped_cells_NaV.draw()
    fig.set_size_inches(12, 6, forward=True)
    fig.savefig(path + '\\grouped_cells_NaV.png', dpi=300)
    # (Mean +/- SEM), genotype X condition
    grouped_stats_NaV = ggplot(data=statdf) \
        + geom_point(size = 0.25, mapping=aes(x='mV', y='NaV_papf_mean', color='Genotype'))\
        + geom_errorbar(mapping=aes(x='mV', ymax='NaV_papf_sem_max', ymin='NaV_papf_sem_min', color='Genotype'))\
        + facet_grid('Genotype ~ Condition', space='free') \
        + theme_light()
    fig = grouped_stats_NaV.draw()
    fig.set_size_inches(12, 6, forward=True)
    fig.savefig(path + '\\grouped_stats_NaV.png', dpi=300)
    # Individual cells, day x cell
    indiv_cells_NaV = ggplot(data=ivdf,  mapping=aes(x='mV', y='NaV_papf', color='Cell'))\
                + geom_point(size=0.2)\
                + facet_grid('day ~ Condition', space='free')\
                + theme_light()\
                + theme(aspect_ratio=1.5)
    fig = indiv_cells_NaV.draw()
    fig.savefig(path + '\\individual_cells_NaV.png', dpi=300)

    # Steady_State
    # Individual cells, genotype X condition
    grouped_cells_ss = ggplot(data=ivdf, mapping=aes(x='mV', y='Steady_papf', color='id')) \
           + geom_point(size=0.2) \
           + facet_grid('Genotype ~ Condition', space='free') \
           + theme_light()
    fig = grouped_cells_ss.draw()
    fig.set_size_inches(12, 6, forward=True)
    fig.savefig(path + '\\grouped_cells_ss.png', dpi=300)
    # (Mean +/- SEM), genotype X condition
    grouped_stats_ss = ggplot(data=statdf) \
           + geom_point(size=0.25, mapping=aes(x='mV', y='Steady_papf_mean', color='Genotype')) \
           + geom_errorbar(mapping=aes(x='mV', ymax='Steady_papf_sem_max', ymin='Steady_papf_sem_min', color='Genotype')) \
           + facet_grid('Genotype ~ Condition', space='free') \
           + theme_light()
    fig = grouped_stats_ss.draw()
    fig.set_size_inches(12, 6, forward=True)
    fig.savefig(path + '\\grouped_stats_ss.png', dpi=300)
    # Individual cells, day x cell
    indiv_cells_ss = ggplot(data=ivdf, mapping=aes(x='mV', y='Steady_papf', color='Cell')) \
           + geom_point(size=0.2) \
           + facet_grid('day ~ Condition', space='free') \
           + theme_light() \
           + theme(aspect_ratio=1.5)
    fig = indiv_cells_ss.draw()
    fig.savefig(path + '\\individual_cells_ss.png', dpi=300)
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

