import numpy as np
import pandas as pd
import os
#from scipy import stats as scistat
import scipy.optimize as opt
from scipy.stats import sem
from scipy.stats import ttest_ind
from plotnine import *
from openpyxl import load_workbook
from functools import reduce

def find_nth(hay, needle, n):  # Helper string parsing-- index of nth instance of character 'needle' string 'haystack'
    start = hay.find(needle)
    while start >= 0 and n > 1:
        start = hay.find(needle, start+1)
        n -= 1
    return start

path =
files = []
for i in os.walk(path):
    files.append(i)
    print(i)
files = files[0][2:][0]

KOL = []
fdf = pd.DataFrame()
for i in files:
    parm_df = pd.read_excel(path + '\\' + i, index_col=0, engine='openpyxl')
    pdf = parm_df[parm_df['Series'].isin(['DRG-C1', 'DRG-C1-2'])].reset_index()
    date = i[:find_nth(i, '.', 1)]
    pdf['Date'] = date
    if date in KOL:
        pdf['Genotype'] = 'PTKO'
    else:
        pdf['Genotype'] = 'Ctrl'
    fdf = fdf.append(pdf)

writer = pd.ExcelWriter(path + '\\' + 'capacitance.xlsx', engine='openpyxl')
fdf.to_excel(writer, 'Cap')
writer.save()
writer.close()

