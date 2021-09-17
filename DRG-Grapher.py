import numpy as np
import pandas as pd
import os
#from scipy import stats as scistat
import scipy.optimize as opt
from plotnine import *
from openpyxl import load_workbook
from functools import reduce

pd.set_option("display.max_columns", None)
path = r'C:\Users\ckowalski\Dropbox\FileTransfers\DRG'
xlspath = path + '\\' + 'finaldata.xlsx'
xls = pd.ExcelFile(xlspath, engine='openpyxl')
dataramp = pd.read_excel(xls, 'Ramps')
datac1 = pd.read_excel(xls, 'C1')
datac2 = pd.read_excel(xls, 'C2')
datac3 = pd.read_excel(xls, 'C3')
datafit = pd.read_excel(xls, 'HillFit')
#datac2 = datac23[datac23['Protocol'].str.contains('C2')].copy()
#datac3 = datac23[datac23['Protocol'].str.contains('C3')].copy()

#Switches
bool_fitting        = 0
bool_id_EC50        = 0
bool_id_TAC         = 0
bool_id_HAC         = 0
bool_id_HACBase     = 0
bool_id_C2DecayTau  = 0
bool_id_C3DecayTau  = 0
bool_id_ramptime    = 0
bool_id_ramp        = 1
bool_id_rampfree    = 0
bool_id_Rheo        = 0

#Compensate HEKA CC gain:
dataramp['Stim (pA)'] = dataramp['Stim (pA)']/5
#Drop by Include column:
#dataramporig = dataramp.copy()
dataramp = dataramp[dataramp['Include'] > 0]
#Add CellID for funky free-axis facets
#todo: maybe just make iterator to plot individually...
dataramp['CellID'] = dataramp['Date'] + str(dataramp['Cell'])
#dataramp = dataramp.replace('RampTreat', 'RampBase').replace('RampBaseline', 'RampTreat')

#Rheobase:
# Groupby ID combineddata + 9-15 -> Min(Stim (pA)) -> subset -> xlsx

#Curve Fitting
def ll4(x,b,c,d,e):
    '''This function is basically a copy of the LL.4 function from the R drc package with
     - b: hill slope
     - c: min response
     - d: max response
     - e: EC50'''
    return(c+(d-c)/(1+np.exp(b*(np.log(x)-np.log(e)))))

if bool_fitting:
    RampsList = []
    for i in dataramp['ID'].unique():
        RampsList.append(i)
    datafit = pd.DataFrame()
    for i in RampsList:
        print(i)
        rampslice = dataramp[dataramp['ID']==i]
        initc = rampslice['Inst. Freq. (Hz)'].min()
        initd = rampslice['Inst. Freq. (Hz)'].max()
        inite = rampslice['Stim (pA)'].mean()
        initials = [0.05, initc, initd, inite]
        fitco, covm = opt.curve_fit(ll4, rampslice['Stim (pA)'], rampslice['Inst. Freq. (Hz)'], p0=initials, maxfev=10000)
        rampslice['RawResiduals'] = rampslice['Inst. Freq. (Hz)'].apply(lambda x: ll4(x,*fitco))
        curfit = dict(zip(['b', 'c', 'd', 'e'], fitco))
        curfit['ID']=i
        curfit['Residual'] = sum(rampslice['RawResiduals']**2)
        for key in curfit.keys():
            rampslice[key] = curfit[key]
        datafit = datafit.append(rampslice)

    book = load_workbook(path + '\\finaldata.xlsx')
    writer = pd.ExcelWriter(path + '\\finaldata.xlsx', engine='openpyxl')
    writer.book = book
    datafit.to_excel(writer, 'HillFit')
    writer.save()
    writer.close()


if bool_id_EC50:
    id_EC50 = (ggplot(data=datafit, mapping=aes(x='Cell', y='e', color='Protocol'))
                    + geom_point(size=1)
                    + facet_grid('Date ~ .', space='free')
                    #+ theme_light()
                    + theme(aspect_ratio=1)
                    + theme(subplots_adjust={'right': 0.75})
                    + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
    fig = id_EC50.draw()
    #fig.set_size_inches(9, 108, forward=True)
    #group_stimfreq.draw(show=True)
    fig.savefig(str(path+ '\\id_ec50.png'), dpi=300)

if bool_id_TAC:
    id_TAC = (ggplot(data=datac1, mapping=aes(x='Trace', y='TACAntipeak', color='Protocol'))
                    + geom_line(size=1)
                    + facet_grid('Cell ~ Date', space='free')
                    #+ theme_light()
                    + theme(aspect_ratio=1)
                    + theme(subplots_adjust={'right': 0.75})
                    + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
    fig = id_TAC.draw()
    #fig.set_size_inches(9, 108, forward=True)
    #group_stimfreq.draw(show=True)
    fig.savefig(str(path+ '\\id_TAC.png'), dpi=300)

if bool_id_HAC:
    id_HAC = (ggplot(data=datac1, mapping=aes(x='Trace', y='HACDiff', color='Protocol'))
                    + geom_line(size=1)
                    + facet_grid('Cell ~ Date', space='free')
                    #+ theme_light()
                    + theme(aspect_ratio=1)
                    + theme(subplots_adjust={'right': 0.75})
                    + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
    fig = id_HAC.draw()
    #fig.set_size_inches(9, 108, forward=True)
    #group_stimfreq.draw(show=True)
    fig.savefig(str(path+ '\\id_HAC.png'), dpi=300)

if bool_id_HACBase:
    id_HACbase = (ggplot(data=datac1, mapping=aes(x='Trace', y='HACBase', color='Protocol'))
              + geom_line(size=1)
              + facet_grid('Cell ~ Date', space='free')
              # + theme_light()
              + theme(aspect_ratio=1)
              + theme(subplots_adjust={'right': 0.75})
              + theme(strip_text_y=element_text(angle=0, ha='left')))
    fig = id_HACbase.draw()
    # fig.set_size_inches(9, 108, forward=True)
    # group_stimfreq.draw(show=True)
    fig.savefig(str(path + '\\id_HACbase.png'), dpi=300)

if bool_id_C2DecayTau:
    id_C2DecayTau = (ggplot(data=datac2, mapping=aes(x='A', y='tau', color='Protocol'))
                    + geom_point(size=1)
                    + facet_grid('Date ~ Cell', space='free')
                    #+ theme_light()
                    + theme(aspect_ratio=1)
                    + theme(subplots_adjust={'right': 0.75})
                    + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
    fig = id_C2DecayTau.draw()
    #fig.set_size_inches(9, 108, forward=True)
    #group_stimfreq.draw(show=True)
    fig.savefig(str(path+ '\\id_C2DecayTauByIntercept.png'), dpi=300)

if bool_id_C3DecayTau:
    id_C3DecayTau = (ggplot(data=datac3, mapping=aes(x='tau1', y='tau2', color='Protocol'))
                    + geom_point(size=1)
                    + facet_grid('Date ~ Cell', space='free')
                    #+ theme_light()
                    + theme(aspect_ratio=1)
                    + theme(subplots_adjust={'right': 0.75})
                    + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
    fig = id_C3DecayTau.draw()
    #fig.set_size_inches(9, 108, forward=True)
    #group_stimfreq.draw(show=True)
    fig.savefig(str(path+ '\\id_C3DecayTauByTau.png'), dpi=300)

if bool_id_ramp:
    id_ramp = (ggplot(data=dataramp, mapping=aes(x='Stim (pA)', y='Inst. Freq. (Hz)', color='Protocol'))
                    + geom_point(size=.05)
                    + facet_grid('Cell ~ Date', space='free')
                    #+ theme_light()
                    #+ theme(aspect_ratio=2)
                    + theme(subplots_adjust={'right': 0.75})
                    + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
    fig = id_ramp.draw()
    #fig.set_size_inches(9, 108, forward=True)
    #group_stimfreq.draw(show=True)
    fig.savefig(str(path+ '\\id_ramp.png'), dpi=300)

if bool_id_rampfree:
    id_rampfree = (ggplot(data=dataramp, mapping=aes(x='Stim (pA)', y='Inst. Freq. (Hz)', color='Protocol'))
                    + geom_point(size=.05)
                    + facet_wrap('CellID', scales='free')
                    #+ theme_light()
                    #+ theme(aspect_ratio=2)
                    + theme(subplots_adjust={'right': 0.75})
                    + theme(subplots_adjust={'wspace': 0.25})
                    + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
    fig = id_rampfree.draw()
    #fig.set_size_inches(9, 108, forward=True)
    #group_stimfreq.draw(show=True)
    fig.savefig(str(path+ '\\id_rampfree.png'), dpi=300)

if bool_id_ramptime:
    id_ramptime = (ggplot(data=dataramp, mapping=aes(x='Event Start Time (ms)', y='Inst. Freq. (Hz)', color='Protocol'))
                    + geom_point(size=.05)
                    + facet_grid('Cell ~ Date', space='free')
                    #+ theme_light()
                    #+ theme(aspect_ratio=2)
                    + theme(subplots_adjust={'right': 0.75})
                    + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
    fig = id_ramptime.draw()
    #fig.set_size_inches(9, 108, forward=True)
    #group_stimfreq.draw(show=True)
    fig.savefig(str(path+ '\\id_ramptime.png'), dpi=300)

if bool_id_Rheo:
    id_Rheo = (ggplot(data=dataramp, mapping=aes(x='Cell', y='Rheobase', color='Protocol'))
                    + geom_point(size=1)
                    + facet_grid('Date ~ ', space='free')
                    #+ theme_light()
                    + theme(aspect_ratio=1/3)
                    + theme(subplots_adjust={'right': 0.75})
                    + theme(strip_text_y= element_text(angle = 0, ha = 'left')))
    fig = id_Rheo.draw()
    #fig.set_size_inches(9, 108, forward=True)
    #group_stimfreq.draw(show=True)
    fig.savefig(str(path+ '\\id_Rheo.png'), dpi=300)