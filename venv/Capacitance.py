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
import csv

def find_nth(hay, needle, n):
    start = hay.find(needle)
    while start >= 0 and n > 1:
        start = hay.find(needle, start+1)
        n -= 1
    return start

path = r'D:\Dropbox (Personal)\FileTransfers\DRG\Capacitance'
files = []
for i in os.walk(path):
    files.append(i)
    print(i)
files = files[0][2:][0]

KOL = ['8-12', '9-7', '9-21', '11-10', '11-23', '12-7', '12-10']
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

print('hook')