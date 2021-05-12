import numpy as np
import pandas as pd
import os
from scipy.stats import sem
from plotnine import *

# Enable/disable all rows/columns or columns
# pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option("display.max_columns", None)

#Search path
path = r'C:\Users\ckowalski\Dropbox\FileTransfers\Go\Go new basal parameters\PyRheo'
outputpath = r'C:\Users\ckowalski\Dropbox\FileTransfers\Go\Go new basal parameters\PyRheo\output.xlsx'

if os.path.exists(outputpath) == True: # If Rheo output.xlsx file is present:
    print('Importing existing analysis output file.')
    #longframenan = pd.read_excel(outputpath)
    xls = pd.ExcelFile(outputpath, engine='openpyxl')
    longframenan = pd.read_excel(xls, 'Longform Data')
    longframemeans = pd.read_excel(xls, 'Means')
    rheobase = pd.read_excel(xls, 'Rheobase')
    longframe = longframenan.dropna()
    #alldata = pd.merge(longframenan, rheobase, on='ID', how='left')


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
for i in longframenan['ID'].unique():
    id = '\'' + i + '\''
    adj = int(rheobase[rheobase['ID'] == id]['rheo_adj'])
    mask = longframenan['ID'] == i
    loop_dict = longframenan[mask]['stim_pA'].apply(lambda x: x+adj).to_dict()
    for i in loop_dict.keys():
        longframenan.loc[i, 'stim_pA'] = loop_dict[i]


#Debug hook/check:
print(longframenan.head(), '\n', rheobase)

rheobase['rheobase'] = rheobase['rheobase_stim_pA'] + rheobase['rheo_adj']

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

group_rheo_box = (ggplot(data=rheobase, mapping=aes(x='group', y='rheobase', color='genotype'))
    #+ geom_point()
    + geom_boxplot()
    + theme_light())
fig = group_rheo_box.draw()
fig.savefig(str(path+ '\\group_rheo_box.png'), dpi=300)

"""date_id_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='frequency', color='group'))
                + geom_point(size=0.05)
                + facet_grid('date ~ cell', space='free')
                #+ theme_light()
                + theme(aspect_ratio=1/3)
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = date_id_stimfreq.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\date-ID_stimfreq.png'), dpi=300)"""

'''
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
fig.savefig(str(path+ '\\date-ID_stimfreq_v2.png'), dpi=300)'''

# Stimulus frequency response Groups
"""group_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='frequency', color='genotype'))
                + geom_point(size=0.1)
                + facet_grid('. ~ group', space='free')
                + scale_x_continuous(limits=[0,500])
                + theme_light())
fig = group_stimfreq.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_stimfreq_v2.png'), dpi=1000)


group_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='spikenum', color='genotype'))
                + geom_point(size=0.1)
                + facet_grid('. ~ group', space='free')
                + scale_x_continuous(limits=[0,500])
                + theme_light())
fig = group_stimfreq.draw()
fig.set_size_inches(15,6, forward=True)
fig.savefig(str(path+ '\\group_stimnum_v2.png'), dpi=1000)
"""
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