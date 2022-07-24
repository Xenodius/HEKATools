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

pd.set_option("display.max_columns", None)
path = r'C:\Users\ckowalski\Dropbox\FileTransfers\DRG\DRGChol'

xls = pd.ExcelFile(path + '\\' + 'combinedata.xlsx', engine='openpyxl')
#dataramp = pd.read_excel(xls, 'Ramps')
#datac1 = pd.read_excel(xls, 'C1')
#datac2 = pd.read_excel(xls, 'C2')
#datac3 = pd.read_excel(xls, 'C3')
datarheo = pd.read_excel(xls, 'RheoGB')

datarheo['CellGroup'] = datarheo.apply(lambda x: '%s_%s_%s' % (x['Genotype'], x['Date'], x['Cell'],), axis=1) #String concat

#New RheoDiffInhib:
datarheoInhib = dict()
datarheoDiff = dict()
#for i in datarheo['CellID.1']:
#    ldf = datarheo[datarheo['CellID.1']==i]
#    ldf[ldf['Protocol']=='RampBaseline']
dfrheo = pd.DataFrame()
for i in datarheo['CellGroup'].unique():
    try:
        dfs = datarheo[datarheo['CellGroup'] == i].copy()
        checktreat = True in dfs['Protocol'].str.contains('RampBaseline').unique() and True in dfs['Protocol'].str.contains('RampTreat').unique() # If RampTreat/Baseline in slice:
        checkretreat = True in dfs['Protocol'].str.contains('RampRecov').unique() and True in dfs['Protocol'].str.contains('RampRetreat').unique() # If RampRetreat/Recov in slice:
        checkbaserecov = checktreat and checkretreat and True in dfs['Protocol'].str.contains('RampRerecov').unique()
        checktreatrecov = checktreat and True in dfs['Protocol'].str.contains('RampRecov').unique()
        if checktreat:
            rowtreat = dfs[dfs['Protocol'] == 'RampTreat'].index[0]
            inhibval = 1/(dfs[dfs['Protocol']=='RampBaseline']['Rheobase'].iloc[0] / dfs[dfs['Protocol']=='RampTreat']['Rheobase'].iloc[0])
            diffval = dfs[dfs['Protocol']=='RampTreat']['Rheobase'].iloc[0] - dfs[dfs['Protocol']=='RampBaseline']['Rheobase'].iloc[0]

            dfs.loc[rowtreat, 'RheoDiff'] = diffval
            dfs.loc[rowtreat, 'RheoInhibition'] = inhibval*100
        if checkretreat:
            rowretreat = dfs[dfs['Protocol'] == 'RampRetreat'].index[0]
            reinhibval = 1/(dfs[dfs['Protocol'] == 'RampBaseline']['Rheobase'].iloc[0] / dfs[dfs['Protocol'] == 'RampRetreat']['Rheobase'].iloc[0])
            rediffval = dfs[dfs['Protocol'] == 'RampRetreat']['Rheobase'].iloc[0] - dfs[dfs['Protocol'] == 'RampRecov']['Rheobase'].iloc[0]
            dfs.loc[rowretreat, 'RheoDiff'] = rediffval
            dfs.loc[rowretreat, 'RheoInhibition'] = reinhibval*100
        if checktreat and checkretreat:
            basedv = 1 - (rediffval / diffval)
            recovdv = 100 - (100 * dfs[dfs['Protocol'] == 'RampRetreat']['Rheobase'].iloc[0] / \
                            dfs[dfs['Protocol'] == 'RampRecov']['Rheobase'].iloc[0])
            treatdv = 100 - (100 * dfs[dfs['Protocol'] == 'RampRetreat']['Rheobase'].iloc[0] / \
                            dfs[dfs['Protocol'] == 'RampTreat']['Rheobase'].iloc[0])
            dfs.loc[rowtreat, 'RheoBaselineDesensitization'] = basedv*100
            dfs.loc[rowtreat, 'RheoRecovDesensitization'] = recovdv
            dfs.loc[rowtreat, 'RheoLastTreatDesensitization'] = treatdv
        if checktreatrecov:
            #treatrecov = dfs[dfs['Protocol']=='RampRecov']['Rheobase'].iloc[0] / dfs[dfs['Protocol']=='RampTreat']['Rheobase'].iloc[0]
            treatrecov = 1-((dfs[dfs['Protocol']=='RampRecov']['Rheobase'].iloc[0] - dfs[dfs['Protocol']=='RampBaseline']['Rheobase'].iloc[0])/diffval) #Subtract baseline from recov/treat vs. above
            dfs.loc[rowtreat, 'TreatRecovery'] = treatrecov*100
        if checkbaserecov:
            #retreatrecov = dfs[dfs['Protocol']=='RampRerecov']['Rheobase'].iloc[0] / dfs[dfs['Protocol']=='RampRetreat']['Rheobase'].iloc[0]
            retreatrecov = 1-((dfs[dfs['Protocol'] == 'RampRerecov']['Rheobase'].iloc[0] - dfs[dfs['Protocol'] == 'RampRecov']['Rheobase'].iloc[0]) / \
                           (dfs[dfs['Protocol'] == 'RampRetreat']['Rheobase'].iloc[0] - dfs[dfs['Protocol'] == 'RampRecov']['Rheobase'].iloc[0]))
            dfs.loc[rowtreat, 'RetreatRecovery'] = retreatrecov*100
        if checktreat or checkretreat:
            dfrheo = pd.concat([dfrheo, dfs], axis=0, ignore_index=True)
    except Exception:
        print('Error in InhibDiff loop:', Exception, '\n', i)
        pass

#drop empties for easy pasting
#dfr = dfrheo[['ID','Date','Genotype','Cell','Protocol','Include','Rheobase','Group','CellGroup','RheoDiff','RheoInhibition', 'RheoBaselineDesensitization', 'RheoRecovDesensitization', 'RheoLastTreatDesensitization']].dropna()
dfr2 = dfrheo.dropna(axis=0, subset=['RheoBaselineDesensitization'])
dfr3 = dfrheo.dropna(axis=0, subset=['TreatRecovery'])
dfr = dfrheo.dropna(axis=0, subset=['RheoDiff'])


writer = pd.ExcelWriter(path + '\\' + 'dfrheo.xlsx', engine='openpyxl')
dfr.to_excel(writer, 'dfr')
dfr2.to_excel(writer, 'dfrDiffPaste')
dfr3.to_excel(writer, 'dfrRecovPaste')
dfrheo.to_excel(writer, 'dfrheoAll')
writer.save()
writer.close()
print('hook')
#datarheo = dfrheo.copy()


'''datarheoMean = datarheo.groupby('Group').mean()
#datarheoSEM = datarheo.groupby('Group').apply(lambda x: sem(x))
datarheoSEM = datarheo.groupby('Group').sem()

datarheo['Group'] = pd.Categorical(datarheo.Group, categories=['KO-MBCDRampRerecov', 'KORampBaseline', 'KORampTreat', 'KORampRecov', 'KORampRetreat', 'KORampRerecov','KO-MBCDRampBaseline', 'KO-MBCDRampTreat', 'KO-MBCDRampRecov', 'KO-MBCDRampRetreat'], ordered=True)
#datarheo['Group'] = pd.Categorical(datarheo.Group, categories=['Ctrl_RampBaseline', 'Ctrl_RampTreat', 'Ctrl_RampRecov', 'Ctrl_RampRetreat', 'Ctrl_RampRerecov', 'Chol_RampBaseline', 'Chol_RampTreat', 'Chol_RampRecov', 'Chol_RampRetreat', 'Chol_RampRerecov'], ordered=True)
#rheocat = pd.api.types.CategoricalDtype(categories=['Ctrl_RampBaseline', 'Ctrl_RampTreat', 'Ctrl_RampRecov', 'Ctrl_RampRetreat', 'Ctrl_RampRerecov', 'KO_RampBaseline', 'KO_RampTreat', 'KO_RampRecov', 'KO_RampRetreat', 'KO_RampRerecov'], ordered=True)
#datarheo['Group'].astype(rheocat)
datarheostat = pd.DataFrame.merge(datarheoMean, datarheoSEM, on='Group', how='outer', suffixes=('_mean', '_sem')).reset_index()
datarheostatdiff = datarheostat.copy().dropna()
datarheostatdiff['Group'] = pd.Categorical(datarheostatdiff.Group, categories=['KORampBaseline', 'KORampTreat', 'KORampRecov', 'KORampRetreat', 'KORampRerecov','KO-MBCDRampBaseline', 'KO-MBCDRampTreat', 'KO-MBCDRampRecov', 'KO-MBCDRampRetreat', 'KO-MBCDRampRerecov'], ordered=True)
'''