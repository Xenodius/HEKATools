import numpy as np
import pandas as pd
import os
from scipy.stats import sem
from plotnine import *
from functools import reduce

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
    longframenan = pd.read_excel(xls, 'Event Data')
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
rheobase.rename(columns = {'rheobase_stim_pA':'rheobase'})

longframenan['spikenum'] = longframenan['spikenum'].replace({0:np.nan})

lf_means = longframenan.groupby(['stim_pA', 'genotype', 'group']).agg([np.mean, sem]).reset_index()
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

#test = {}
#fdflist = []
#for n, i in enumerate(ldflist2):
#    for nn, ii in enumerate(i):
#        print('group:', n, 'cell:', nn)
#        val = str(n) + '_' + str(nn)
        #test[val] = ii[['date', 'cell', 'colorgroup', 'ID', 'Trace', 'stim_pA', 'frequency']].drop_duplicates(subset='stim_pA').set_index('stim_pA')
        #test[val] = ii[['stim_pA', 'frequency']].drop_duplicates(subset='stim_pA').set_index('stim_pA')
        #test.append(ii[['stim_pA', 'frequency']].drop_duplicates(subset='stim_pA').set_index('stim_pA'))
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

#fdf = reduce(lambda df_left,df_right: pd.merge(df_left, df_right, on='stim_pA', how='outer'), fdflist)
#writer = pd.ExcelWriter(path + '\\graphing')
#fdf.to_excel(writer, 'Frequency')
#writer.save()
#Create slice of dataframe with frequencies for a single cell
#ldflist2[1][['date', 'cell', 'ID', 'Trace', 'stim_pA', 'frequency']].drop_duplicates(subset='stim_pA').set_index('Trace')

"""group_rheo_box = (ggplot(data=rheobase, mapping=aes(x='group', y='rheobase', color='genotype'))
    #+ geom_point()
    + geom_boxplot()
    + theme_light())
fig = group_rheo_box.draw()
fig.savefig(str(path+ '\\group_rheo_box.png'), dpi=300)"""

date_id_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='frequency', color='cell'))
                + geom_point(size=0.05)
                + facet_grid('date ~ ', space='free')
                #+ theme_light()
                + theme(aspect_ratio=1/3)
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = date_id_stimfreq.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\date_stimfreq.png'), dpi=300)


date_id_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='frequency', color='colorgroup'))
                + geom_point(size=0.05)
                + facet_grid('ID ~ .')
                + scale_x_continuous(limits=[0,500])
                #+ theme_light()
                + theme(figure_size=(6,100))
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = date_id_stimfreq.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\date-ID_stimfreq.png'), dpi=300)

# Stimulus frequency response Groups
"""group_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='frequency', color='genotype'))
                + geom_point(size=0.1)
                + facet_grid('. ~ group', space='free')
                + scale_x_continuous(limits=[0,500])
                + theme_light())
fig = group_stimfreq.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_stimfreq_v2.png'), dpi=300)


group_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='spikenum', color='genotype'))
                + geom_point(size=0.1)
                + facet_grid('. ~ group', space='free')
                + scale_x_continuous(limits=[0,500])
                + theme_light())
fig = group_stimfreq.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_stimnum_v2.png'), dpi=1000)

group_stimfreq = (ggplot(data=lf_means, mapping=aes(x='stim_pA_', y='spikenum_mean', color='genotype_'))
                + geom_point(size=0.1)
                + geom_errorbar(aes(ymin = 'spikenum_mean - spikenum_sem', ymax = 'spikenum_mean + spikenum_sem'))
                + facet_grid(' ~ group_', space='free')
                + scale_x_continuous(limits=[0,500])
                + theme_light())
fig = group_stimfreq.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_meanSEM_stimnum_v2.png'), dpi=1000)

group_stimfreq = (ggplot(data=lf_means, mapping=aes(x='stim_pA_', y='frequency_mean', color='genotype_'))
                + geom_point(size=0.1)
                + geom_errorbar(aes(ymin = 'frequency_mean - frequency_sem', ymax = 'frequency_mean + frequency_sem'))
                + facet_grid(' ~ group_', space='free')
                + scale_x_continuous(limits=[0,500])
                + theme_light())
fig = group_stimfreq.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_meanSEM_stimfreq_v2.png'), dpi=1000)
"""

"""group_stimfreq_means = (ggplot(data=lf_means, mapping=aes(x='stim_pA', y='frequency', color='genotype'))
                + geom_point(size=0.1)
                + facet_grid('genotype ~ group', space='free')
                + theme_light())
fig = group_stimfreq_means.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_stimfreq_means_v2.png'), dpi=1000)

group_stimfreq_means = (ggplot(data=lf_means, mapping=aes(x='stim_pA', y='spikenum', color='genotype'))
                + geom_point(size=0.1)
                + facet_grid('genotype ~ group', space='free')
                + theme_light())
fig = group_stimfreq_means.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_spikenum_means_v2.png'), dpi=1000)
"""
#Half-width Date X ID
"""group_halfwidth = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='Half-width (ms)', color='group'))
                + geom_point(size=0.05)
                + facet_grid('genotype ~ group')
                #+ theme_light()
                #+ theme(aspect_ratio=1/3)
                + scale_x_continuous(limits=[0,500])
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = group_halfwidth.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\group_half-width_v2.png'), dpi=300)

#TimetoPeak Date X ID
date_ID_timetopeak = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='Time to Peak (ms)', color='group'))
                + geom_point(size=0.05)
                + facet_grid('date ~ cell')
                #+ theme_light()
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = date_ID_timetopeak.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\date-ID_timetopeak.png'), dpi=300)

#TimetoAntipeak Date X ID
date_ID_timetoantipeak = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='Time to Antipeak (ms)', color='group'))
                + geom_point(size=0.05)
                + facet_grid('date ~ cell')
                #+ theme_light()
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = date_ID_timetoantipeak.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\date-ID_timetoantipeak.png'), dpi=300)

#RiseTau Date X ID
date_ID_risetau = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='Rise Tau (ms)', color='group'))
                + geom_point(size=0.05)
                + facet_grid('date ~ cell')
                #+ theme_light()
                + theme(aspect_ratio=1/3)
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = date_ID_risetau.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\date-ID_risetau.png'), dpi=300)

#decayTau Date X ID
date_ID_decaytau = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='Decay Tau (ms)', color='group'))
                + geom_point(size=0.05)
                + facet_grid('date ~ cell')
                #+ theme_light()
                + theme(aspect_ratio=1/3)
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = date_ID_decaytau.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\date-ID_decaytau.png'), dpi=300)

#Rheobases Date X ID
rheo_id = (ggplot(data=rheobase, mapping=aes(x='rheo_max_volts', y='rheobase_stim_pA', color='group'))
           + geom_point(size=0.05)
           + facet_grid('date ~ cell')
           + theme(aspect_ratio=1/3)
           + theme(strip_text_y = element_text(angle=0, ha='left')))
fig = rheo_id.draw()
fig.savefig(str(path+ '\\rheo-ID_stimfreq.png'), dpi=300)
"""
#Rheo.py Plots
# Stimulus frequency response looper
"""for key in cell_df_dict:
    stimhz = (ggplot(cell_df_dict[key], aes('stim_pA', 'frequency', color='ID'))
                    + geom_point()
                    + facet_grid('ID ~ .')
                    + theme(aspect_ratio=1/3))
    fig = stimhz.draw()
    fig.savefig(str(path+ '\\cell_stimfreq_' + key + '.png'))"""

# Stimulus frequency response Groups
"""group_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='frequency', color='ID'))
                + geom_point(size=0.1)
                + facet_grid('genotype ~ group', space='free')
                + theme_light())
fig = group_stimfreq.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_stimfreq_alt.png'), dpi=1000)

group_voltfreq = (ggplot(data=longframenan, mapping=aes(x='R1S1Mean', y='frequency', color='ID'))
                + geom_point(size=0.1)
                + facet_grid('genotype ~ group', space='free')
                + theme_light())
fig = group_voltfreq.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_voltfreq_alt.png'), dpi=1000)

group_stimspikenum = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='spikenum', color='ID'))
                + geom_point(size=0.1)
                + facet_grid('genotype ~ group', space='free')
                + theme_light())
fig = group_stimspikenum.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_stimnum_alt.png'), dpi=1000)

#Stimulus frequency response means of each unique Trace(row) x Genotype x Group combination
group_stimfreq_means = (ggplot(data=lf_means, mapping=aes(x='stim_pA', y='frequency', color='genotype'))
                + geom_point(size=0.1)
                + facet_grid('genotype ~ group', space='free')
                + theme_light())
fig = group_stimfreq_means.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_stimfreq_means_alt.png'), dpi=1000)"""

"""for key in group_df_dict:
    stimhz = (ggplot(group_df_dict[key], aes('stim_pA', 'frequency', color='cell'))
                    + geom_point()
                    + facet_grid('group ~ .')
                    + theme(aspect_ratio=1/3))
    fig = stimhz.draw()
    fig.savefig(str(path+ '\\group_stimfreq_' + key + '.png'))"""

# Membrane potential frequency response
"""for key in cell_df_dict:
    sweepfreq = (ggplot(cell_df_dict[key], aes('R1S1Mean', 'frequency', color='ID'))
                    + geom_point()
                    + facet_grid('ID ~ .')
                    + theme(aspect_ratio=1/3))
    fig = sweepfreq.draw()
    fig.savefig(str(path+ '\\cell_sweepfreq_' + key + '.png'))
# Stimulus spike# response
for key in cell_df_dict:
    sweepfreq = (ggplot(cell_df_dict[key], aes('stim_pA', 'spikenum', color='ID'))
                    + geom_point()
                    + facet_grid('ID ~ .')
                    + theme(aspect_ratio=1/3))
    fig = sweepfreq.draw()
    fig.savefig(str(path+ '\\cell_stimnum_' + key + '.png'))"""
