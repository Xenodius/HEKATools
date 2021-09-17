import numpy as np
import pandas as pd
import glob
import os
import sys
# Enable/disable all rows/columns or columns
# pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option("display.max_columns", None)
path = r'C:\Users\ckowalski\Dropbox\FileTransfers\DRG'
EventHeaders = ['Trace', 'Search', 'Category', 'State', 'Event Start', 'Baseline']
RampConvDict = {'DRG-CRamp.atf': 3, 'DRG-FRamp.atf': .3, 'DRG-MRamp': 1, 'DRG-MRamp.atf':1}

# Walk the path
walk = [x for x in os.walk(path)] #1= dirpath, 2 = dirnames, 3 = filenames
groupFolders = walk[0][1] # dirnames in path

#### Notes on Analysis
# Requires:
# Ramp ATF's
# C2 Tau ATF's (DAC Decay first order exponential Tau)
# C3 Tau ATF's (AP Decay fastest of 2nd order exponential Tau)
## C1-HAC-TC xlsx with heading:
# File Name	Trace	Trace Start	R1S1Peak	R3S1Peak	R3S1Antipeak	R1S1Mean	R2S1Mean	R3S1Mean	FilePath
# R1 = HAC Peak, R2 = HAC Steady-state, R3 = Transient peak
## C2-DAC xslx with heading:
# FileName	Trace	TraceStart	R1S1Peak	R3S1Peak	R1S1Antipeak	R3S1Antipeak	R1S1Mean	R2S1Mean	R3S1Mean	FilePath
# R1 = DAC Peak, R2 = DAC steady-state, R3 = Transient peak


#csv fix
"""
walk = [x for x in os.walk(path + '\\9-7_T1')]
wlk = []
for i in walk[0][2]:
    if 'csv' in i:
        wlk.append(i)

for i in wlk:
    with open(path + '\\9-7_T1\\' + i, mode="rU") as infile:
        reader = csv.reader(infile, delimiter=',')
        with open(path + '\\9-7_T1\\' + i+'.atf', mode='w') as outfile:
            writer = csv.writer(outfile, delimiter='	')
            writer.writerows(reader)"""



def find_nth(hay, needle, n):
    start = hay.find(needle)
    while start >= 0 and n > 1:
        start = hay.find(needle, start+1)
        n -= 1
    return start

# Extract full filepaths of any .csv files in group folders
C1GroupDict = {} #C1...3 protocol parameters
C2GroupDict = {}
C3GroupDict = {}
EventFilePaths = [] #Event fitting of ramps


for i in groupFolders:
    folder = glob.glob(path + '\\' + i + '\\*.xlsx') # list of CSV in each DRG subfolder
    if len(folder) > 0: # if folder actually has any CSV's:
        #nestedGroupCSV.append(folder) # append to list.
        for ii in folder:
            if 'C1' in ii:
                C1GroupDict[i] = ii
            elif 'C2' in ii:
                C2GroupDict[i] = ii
            elif 'C3' in ii:
                C3GroupDict[i] = ii

for i in groupFolders:
    folder = glob.glob(path + '\\' + i + '\\*.atf') # list of CSV in each DRG subfolder
    if len(folder) > 0: # if folder actually has any CSV's:
        for ii in folder:
            if 'C2' in ii:
                C2GroupDict[i] = ii
            elif 'C3' in ii:
                C3GroupDict[i] = ii
            elif not 'C2' in ii and not 'C3' in ii:
                EventFilePaths.append(ii)

#CellGroups = pd.read_excel(path + '\\DRG.xlsx', engine='openpyxl')

#for i in nestedGroupCSV: # For day/group in list:
#    for ii in i: # for CSV file in list:
#        if 'C1' in ii:
#            C1XL.append(ii) # append to new, un-nested list.
        #if 'C2' and '.atf' in ii:
#data = pd.read_csv(C1XL[0], sep='	', header = 0, index_col = False, encoding ='cp1252')

CellGroups = pd.read_excel(path + '\\DRG.xlsx', engine='openpyxl')
finaldata_ramps = pd.DataFrame()
finaldata_c1 = pd.DataFrame()
finaldata_c23 = pd.DataFrame()
#AnalysisColumns = ['C1Baseline', 'C2Baseline', 'C3Baseline', 'RampBaseline', 'C1Treat', 'C2Treat', 'C3Treat', 'RampTreat', 'C3Recov', 'RampRecov']
AnalysisColumns = ['C1Baseline', 'C2Baseline', 'C3Baseline', 'RampBaseline', 'C2Treat', 'C3Treat', 'RampTreat',
                   'C2Recov', 'C3Recov', 'RampRecov', 'C2Retreat', 'C3Retreat', 'RampRetreat',
                   'C2Rerecov', 'C3Rerecov', 'RampRerecov']

for date in CellGroups['Date'].dropna().unique():
    CellDate = CellGroups[CellGroups['Date'] == date]
    dataC1 = pd.read_excel(C1GroupDict[date], engine='openpyxl')
    dataC1 = dataC1.rename(columns={'R1S1Mean': 'HACBase', 'R2S1Mean': 'HACPeak', 'R3S1Mean': 'TACMean', 'R3S1Antipeak': 'TACAntipeak'})
    dataC2 = pd.read_csv(C2GroupDict[date], sep='	', header=2, index_col=False, encoding='cp1252')
    dataC3 = pd.read_csv(C3GroupDict[date], sep='	', header=2, index_col=False, encoding='cp1252')
    for cell in CellDate['Cell'].dropna().unique():
        CellSlice = CellDate[CellDate['Cell']==cell].fillna(0)
        for column in AnalysisColumns:
            print('Processing', date, 'Cell ', str(int(cell)).zfill(3), column)
            filenum = str(int(CellSlice[column])).zfill(3)
            if 'Ramp' in column:
                EventFile = [i for i in EventFilePaths if filenum in i and filenum != 0 and date in i]  # If filenum not NaN, and its num/date in filepath:
                lenEventFile = len(EventFile)
                if lenEventFile > 0:
                    print('Identified', column, '___', EventFile)
                    eventdata = pd.read_csv(EventFile[0], sep='	', header=2, index_col=False, encoding='cp1252') # cp1252 (HEKA default) or UTF-8 (Notepad++ default)
                    eventdata['Delta Peak Amp (mV)'] = eventdata['Baseline (mV)'] + eventdata['Peak Amp (mV)']
                    eventdata = eventdata[['Inst. Freq. (Hz)', 'Event Start Time (ms)', 'Time to Peak (ms)',
                       'Time to Antipeak (ms)', 'Delta Peak Amp (mV)', 'Rise Tau (ms)', 'Decay Tau (ms)',
                       'Rise Slope 10% to 90% (mV/ms)', 'Area (mV · ms)']]
                    efpath = EventFile[0]
                    efpathend = efpath[(len(efpath)-6):]
                    trimloc = find_nth(efpath, date, 1)  # Date\\File index
                    trimloc2 = find_nth(efpath[trimloc:], '\\', 1) + trimloc + 5  # File index
                    if 'T1' in efpathend or 'T2' in efpathend:
                        try:
                            filename = efpath[trimloc2:(trimloc2 + find_nth(efpath[trimloc2:], '-',
                                                                            2))]  # clip to 2nd hyphen after DRG-MRamp
                        except Exception as e:
                            print(e)
                    else:
                        filename = efpath[trimloc2:]
                    eventdata['Stim (pA)'] = eventdata['Event Start Time (ms)'] / RampConvDict[filename]
                    eventdata['Rheobase'] = eventdata['Stim (pA)'].min()
                    Genotype = CellSlice['Genotype'].iloc[0]
                    eventdata['Genotype'] = Genotype
                    eventdata['Cell'] = cell
                    eventdata['Date'] = date
                    eventdata['Protocol'] = column
                    eventdata['File Path'] = efpath
                    eventdata['File Name'] = filename
                    eventdata['ID'] = str(int(cell)).zfill(3) + '_' + date + '_' +  column
                    outdata = pd.merge(CellSlice, eventdata, how='right')
                    finaldata_ramps = finaldata_ramps.append(outdata)
            elif 'C1' in column:
                print('Identified ', column)
                C1Slice = dataC1[dataC1['File Name'].str.contains(filenum)]
                Genotype = CellSlice['Genotype'].iloc[0]
                C1Slice['HACDiff'] = C1Slice['HACBase'] - C1Slice['HACPeak']
                C1Slice['Genotype'] = Genotype
                C1Slice['Cell'] = cell
                C1Slice['Date'] = date
                C1Slice['Protocol'] = column
                C1Slice['ID'] = str(int(cell)).zfill(3) + '_' + date + '_' +  column
                outdata = pd.merge(CellSlice, C1Slice, how='right')
                finaldata_c1 = finaldata_c1.append(outdata)
            elif 'C2' in column:
                print('Identified ', column)
                C2Slice = dataC2[dataC2['File Name'].str.contains(filenum)]
                Genotype = CellSlice['Genotype'].iloc[0]
                C2Slice['Genotype'] = Genotype
                C2Slice['Cell'] = cell
                C2Slice['Date'] = date
                C2Slice['Protocol'] = column
                C2Slice['ID'] = str(int(cell)).zfill(3) + '_' + date + '_' +  column
                outdata = pd.merge(CellSlice, C2Slice, how='right')
                finaldata_c23 = finaldata_c23.append(outdata)
            elif 'C3' in column:
                print('Identified ', column)
                C3Slice = dataC3[dataC3['File Name'].str.contains(filenum)]
                Genotype = CellSlice['Genotype'].iloc[0]
                C3Slice['Genotype'] = Genotype
                C3Slice['Cell'] = cell
                C3Slice['Date'] = date
                C3Slice['Protocol'] = column
                C3Slice['ID'] = str(int(cell)).zfill(3) + '_' + date + '_' +  column
                outdata = pd.merge(CellSlice, C3Slice, how='right')
                finaldata_c23 = finaldata_c23.append(outdata)
        #print('hook')

#Filter double marked events
finaldata_ramps = finaldata_ramps[finaldata_ramps['Inst. Freq. (Hz)'] < 100] # Frequency cutoff

#Split C2/C3's
finaldata_c2 = finaldata_c23[finaldata_c23['Protocol'].str.contains('C2')].copy()
finaldata_c3 = finaldata_c23[finaldata_c23['Protocol'].str.contains('C3')].copy()

writer = pd.ExcelWriter(path + '\\' + 'finaldata.xlsx', engine='openpyxl')
finaldata_ramps.to_excel(writer, 'Ramps')
finaldata_c1.to_excel(writer, 'C1')
finaldata_c2.to_excel(writer, 'C2')
finaldata_c3.to_excel(writer, 'C3')
writer.save()

print('Finished. Have some coffee.')

"""for date in CellGroups['Date'].dropna().unique():
    dataC1 = pd.read_excel(C1GroupDict[date], engine='openpyxl')
    dataC1 = dataC1.rename(columns={'R1S1Mean': 'HACBase', 'R2S1Mean': 'HACPeak', 'R3S1Mean': 'TACMean', 'R3S1Antipeak': 'TACAntipeak'})
    dataC2 = pd.read_csv(C2GroupDict[date], sep='	', header=2, index_col=False, encoding='cp1252')
    dataC3 = pd.read_csv(C3GroupDict[date], sep='	', header=2, index_col=False, encoding='cp1252')
    for cell in CellGroups['Cell'].dropna().unique(): #List of cells from date:
        print('Beginning ', date, 'cell number ', int(cell))
        NewData = False
        for i in EventFilePaths:
            if date in i:
                #print('date:', date, i)
                trimloc = find_nth(i, date, 1) #Date\\File index
                trimloc2 = find_nth(i[trimloc:], '\\', 1) + trimloc + 1 #File index
                filename = i[trimloc2:]
                filenum = filename[:3]
                # Slice masterlist to find row of date/cell combo:
                CellSlice = CellGroups[CellGroups['Cell'] == int(cell)][CellGroups['Date'] == date]
                print('debughook')
                #if int(CellSlice['Include']):
                try:
                    if int(filenum) == int(CellSlice['RampBaseline']): # if baseline ramp:
                        title = date + '_' + cell + '_' + str(int(filenum)).zfill(3) + '_' + 'BaselineRamp'
                        print('matchyfind! ', title)
                    elif int(filenum) == int(CellSlice['RampTreat']): # if treat ramp:
                        title = date + '_' + cell + '_' + str(int(filenum)).zfill(3) + '_' + 'TreatRamp'
                        print('matchyfind! ', title)
                    elif int(filenum) == int(CellSlice['RampRecov']): # if recov ramp:
                        title = date + '_' + cell + '_' + str(int(filenum)).zfill(3) + '_' + 'RecovRamp'
                        print('matchyfind! ', title)
                    else:
                        print('date: ', date, 'cell: ', cell, 'file: ', filename, 'not matched.')
                        continue
                except Exception:
                    continue
                eventdata = pd.read_csv(i, sep='	', header=2, index_col=False, encoding='cp1252')
                eventdata = eventdata[['Inst. Freq. (Hz)', 'Event Start Time (ms)', 'Rise Tau (ms)', 'Decay Tau (ms)']]
                eventdata['Genotype'] = CellSlice['Genotype'].iloc[0]
                eventdata['Cell'] = cell
                eventdata['Date'] = date
                eventdata['ID'] = title
                outdata = pd.merge(CellSlice, eventdata, how='right')
                NewData = True
                print(title, 'Processed')
        if NewData:
            finaldata = finaldata.append(outdata)

print('debughook')
"""
        #eventdata = pd.read_csv(i, sep='	', header=2, index_col=False, encoding='cp1252')
        #eventdata = eventdata.copy()[['Inst. Freq. (Hz)', 'Event Start Time (ms)', 'Rise Tau (ms)', 'Decay Tau (ms)']]
        #print(filename)

"""for date in Groups:
    dataC1 = pd.read_excel(C1GroupDict[date], engine='openpyxl')
    dataC1 = dataC1.rename(columns={'R1S1Mean': 'HACBase', 'R2S1Mean': 'HACPeak', 'R3S1Mean': 'TACMean', 'R3S1Antipeak': 'TACAntipeak'})
    dataC2 = pd.read_csv(C2GroupDict[date], sep='	', header=2, index_col=False, encoding='cp1252')
    dataC3 = pd.read_csv(C3GroupDict[date], sep='	', header=2, index_col=False, encoding='cp1252')
    for i in EventFilePaths:
        # for ii in CellListFrom DRG.xlsx
        if date in i:
            eventdata = pd.read_csv(i, sep='	', header=2, index_col=False, encoding='cp1252')
            #eventdata = eventdata.copy()[['Event Start Time (ms)', 'Event End Time (ms)', 'Baseline (mV)', 'Peak Amp (mV)', 'Time to Peak (ms)',
            #     'Time of Peak (ms)', 'Antipeak Amp (mV)', 'Time to Decay Half-amplitude (ms)', 'Rise Tau (ms)',
            #     'Decay Tau (ms)', 'Max Rise Slope (mV/ms)', 'Max Decay Slope (mV/ms)', 'Area (mV · ms)',
            #     'Inst. Freq. (Hz)', 'Interevent Interval (ms)']]



# Date, Genotype, Cell, CellFileStart, CellType, Include, C1Baseline, C2Baseline, C3Baseline, RampBaseline,
# C1Treat, C2Treat, C3Treat, RampTreat, C3Recov, RampRecov


print('debughook')


#Not needed trash;

outdata = eventdata.groupby(by='Trace', axis=0).apply(lambda x: x['Time of Peak (ms)'].unique()).reset_index()
outdata.rename(columns={0: 'spiketime'}, inplace=True)  # Rename column header int:0 as str:spiketime
sweepfreq = []
for index, spikes in enumerate(outdata['spiketime']): #Run once per sweep and count sweeps.
    # print('Index: ', index, 'Length: ', len(spikes), 'list: ', spikes)
    hzlist = []
    startlist = []
    indexlist = []
    # if spikes == 0:
    # hzlist.append(0)
    #try:
    #    if len(spikes) < 2:  # If contains less than two spikes in sweep, outdata = 0
    #        hzlist.append(0)
    #except TypeError:  # len(0) -> typerror, for sweeps with no spikes, outdata = 0
    #    hzlist.append(0)
    #else:
    for i, time in enumerate(spikes):
        if i == len(spikes) - 1: #stop last loop indexerror
            pass
        else:
            freq = 1/((spikes[i + 1] - spikes[i])/1000)  # Get next interevent interval
        hzlist.append(freq)  # Append interevent interval to list
        startlist.append(spikes[i])
        indexlist.append[i]
    outdata['instfrequency'] = pd.Series(hzlist, index=indexlist)
    outdata['spiketime'] = pd.Series(startlist, index=indexlist)

outdata['frequency'] = sweepfreq
outdata['spikenum'] = outdata['spiketime'].str.len()
outdata = outdata.drop(columns='spiketime')"""