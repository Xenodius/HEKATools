import csv
import numpy as np
import pandas as pd
import glob
import os
import xlsxwriter
import matplotlib.pyplot as plt # Deprecate
#from plotnine import ggplot, geom_point, aes, stat_smooth, facet_wrap
from plotnine import *

#Search path
path = r'C:\Program Files (x86)\HEKA2x903\Data\PyRheo'
outputpath = r'C:\Program Files (x86)\HEKA2x903\Data\PyRheo\output.xlsx'

if os.path.exists(outputpath) == True: # If Rheo3 output.xlsx file is present:
    print('Importing existing analysis output file.')
    longframenan = pd.read_excel(outputpath)

print(longframenan)

group_stimfreq = (ggplot(data=longframenan, mapping=aes(x='stim_pA', y='frequency', color='ID'))
                + geom_point(size=0.05)
                + facet_grid('group ~ genotype')
                + theme_light())
fig = group_stimfreq.draw()
fig.savefig(str(path+ '\\group_stimfreq.png'), dpi=1000)