import pandas as pd
import os
from plotnine import *

# Enable/disable all rows/columns or columns
# pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option("display.max_columns", None)

#Search path
path = r'C:\Program Files (x86)\HEKA2x903\Data\PyRheo'
outputpath = r'C:\Program Files (x86)\HEKA2x903\Data\PyRheo\output.xlsx'

if os.path.exists(outputpath) == True: # If Rheo output.xlsx file is present:
    print('Importing existing analysis output file.')
    #longframenan = pd.read_excel(outputpath)
    xls = pd.ExcelFile(outputpath)
    longframenan = pd.read_excel(xls, 'Longform Data')
    longframemeans = pd.read_excel(xls, 'Means')
    rheobase = pd.read_excel(xls, 'Rheobase')
    longframe = longframenan.dropna()
    #alldata = pd.merge(longframenan, rheobase, on='ID', how='left')
print(longframenan.head(), '\n', rheobase)

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

date_id_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='frequency', color='colorgroup'))
                + geom_point(size=0.05)
                + facet_grid('ID ~ .')
                #+ theme_light()
                + theme(figure_size=(6,100))
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = date_id_stimfreq.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\date-ID_stimfreq.png'), dpi=300)

"""#Half-width Date X ID
date_id_halfwidth = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='Half-width (ms)', color='group'))
                + geom_point(size=0.05)
                + facet_grid('date ~ cell')
                #+ theme_light()
                + theme(aspect_ratio=1/3)
                + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
fig = date_id_halfwidth.draw()
#fig.set_size_inches(9, 108, forward=True)
#group_stimfreq.draw(show=True)
fig.savefig(str(path+ '\\date-ID_half-width.png'), dpi=300)

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