from pyabf import abfWriter
import numpy as np
import pandas as pd
import glob
import os
import sys
import ParamParse

# Vars
path = r'C:\Program Files (x86)\HEKA2x903\Data\PyABF'
cclist = ['Rheo', 'ST', 'IGF', 'spiketest']  # DEPRECATED BY PARAMPARSE: Protocol names recognized as current-clamp measures
divfactor = 1/1000000000  # pA -> mV unit scalar
volt_to_mvfactor = 1000  # 1000 for HEKA V->mV
amp_to_picofactor = 1000000000000
colnames = ['Time', 'Trace']
debug = False
def dbg(string):
    if debug == True:
        print(string)
    else:
        pass

### Enable/disable all rows/columns or columns
# pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option("display.max_columns", None)
# pd.set_option("display.max_rows", None)

#Check if parameters present, if so, analyze then load xlsx. If not, break.
if os.path.isfile(path + '\\parameters.asc') and not os.path.isfile(path + '\\parameters.xlsx'):
    ParamParse.parse(path)
elif not os.path.isfile(path + '\\parameters.asc'):
    print('No parameters.asc file present in path.')
    sys.exit()

##### Redefine and refactor 'cclist' from parameters parser
parm_df = pd.read_excel(path + '\\parameters.xlsx', index_col=0, engine='openpyxl')
# Generate dictionaries as needed from parm_df for conversion operations
infilepath = {}  # e.g. 001.asc
outfilepath = {}  # e.g. 001-Ih.abf
voltageclamp = {}  # Boolean
for index in parm_df.index:
    indexpad = str(index).zfill(3)
    infilepath[index] = (path + '\\' + indexpad + '.asc')
    outfilepath[index] = (path + '\\' + indexpad + '-' + parm_df.loc[index][0] + '.abf')
    # outfilepath[index] = outfilepath[index].replace('/', '_')  # For AMPA/NMDA protocol-- change name
    if parm_df.loc[index][3] == 'V-Clamp':
        voltageclamp[index] = True
    else:
        voltageclamp[index] = False

for index in parm_df.index:
    freq = None
    data = None
    # dbg(str('Beginning file conversion for: ', infilepath[index]))
    data = pd.read_csv(infilepath[index], sep='\s+', skipinitialspace=True, names=colnames)
    # dbg(str('Original data: ', '\n', data))
    freq = int(1 / data['Time'].iloc[1])  # Reciprocal first time step, e.g. sampling rate in Hz
    if voltageclamp[index] == False:
        data['Trace'] *= volt_to_mvfactor  # To convert volts -> milli for volts -> millivolts
        # dbg(str('volt->mv data: ', '\n', data))
    elif voltageclamp[index] == True:
        data['Trace'] *= amp_to_picofactor
        # dbg(str('amp->pA data: ', '\n', data))
    # Need to refactor to stack from longform to wide
    data['sweep'] = data.groupby('Time').cumcount()
    # dbg(str('post-cumcount data: ', '\n', data))
    data = data.pivot(index='Time', columns='sweep', values='Trace')
    # dbg(str('post-pivot data: ', '\n', data))
    # data = data.set_index('Time', drop=True)
    if debug is True: print('Reindexed data: ', '\n', data)
    # dbg(str('Hz: ', freq, 'Sweeps: ', data.shape[1], 'VoltageClamp: ', voltageclamp[index], 'File: ', infilepath[index]))
    data = data.transpose().fillna(0)  # Flip so each sweep is row as pyabf expects
    # In partial sweeps, pivot produces NaN where there are no values. Sets these to 0
    data = np.array(data)
    # dbg(str('Final np.array data: ', '\n', data))
    if voltageclamp[index] == False:
        abfWriter.writeABF1(data, outfilepath[index], freq, units='mV')
    elif voltageclamp[index] == True:
        abfWriter.writeABF1(data, outfilepath[index], freq, units='pA')
        # If out of range value struct_pack error, check V-Clamp/C-Clamp for wrong multiplier



def csvabf(infile, outfile):
    if debug is True: print('Beginning file conversion for: ', infile)
    if any(ccname in infile for ccname in cclist): # Checks if any substrings in cclist are in the filenames.
        voltageclamp = False
        #print('For file: ', infile, 'Currentclamp: ', currentclamp)
    else:
        voltageclamp = True
        #print('For file: ', infile, 'Currentclamp: ', currentclamp)
    if '.asc' in infile:  # Units = pA. For HEKA, not "Export table" of Nest-0-Patch
        data = pd.read_csv(infile, sep='\s+', skipinitialspace=True, header=2, index_col=False)
        if debug is True: print('Original data: ', '\n', data)
        freq = int(1 / data['Time[s]'][1])  # Reciprocal first time step, e.g. sampling rate in Hz
        # print('Original data: ', data)
        if voltageclamp == False:
            data['Imon-1[A]'] *= divfactor  # To convert pico -> milli for amps -> volts
            if debug is True: print('Divfactored data: ', data)


        data = data.set_index('Time[s]', drop=True)
        if debug is True: print('Reindexed data: ', '\n', data)
        data = data.transpose().fillna(0)  # Flip so each sweep is row as pyabf expects
        # In partial sweeps, pivot produces NaN where there are no values. Sets these to 0
        if debug is True: print('Final np.array data: ', '\n', data)
        data = np.array(data)
        ### Here, scale from A -> pA. Possible conflict with loop variable persistence and multiple filteypes

    elif '.csv' in infile:  # Units = pA. "Export table" of Nest-0-Patch
        data = pd.read_csv(infile, sep=';', header=None, index_col=False)
    elif '.txt' in infile:  # Units = A, scientific notation. Save as .txt of Nest-0-Patch
        data = pd.read_csv(infile, sep=' ', header=None, index_col=False)
        columns = data.shape[1]
        freq = int(1 / data[0][1])  # Reciprocal first time step, e.g. sampling rate in Hz
        # print('Original data: ', data)
        if columns == 2: # Currently just looks for second column as data: Nest-O-Patch only. Consider modifying for catching Patchmaster exports, tables with N columns; just drop first column and concat.
            if voltageclamp == False:
                data[1] *= divfactor  # To convert pico -> milli for amps -> volts
            if debug is True: print('Pre-melting data: ', '\n', data)
            data = data.melt(0, var_name='sweep')
            if debug is True: print('Melted data: ', '\n', data)
            data['sweep'] = data.groupby(0).cumcount()
            data = data.pivot(index=0, columns='sweep', values='value')
        if debug is True: print('Hz: ', freq, 'Sweeps: ', data.shape[1], 'VoltageClamp: ', voltageclamp, 'File: ', infile)
        # data = data.drop(axis='columns', labels=0) # Drop time column-- NOW DONE ABOVE
        if debug is True: print('Pre-transposed data: ', '\n', data)
        data = data.transpose() # Flip so each sweep is row as pyabf expects .fillna(0)
                                        # In partial sweeps, pivot produces NaN where there are no values. Sets these to 0
        if debug is True: print('post-transposed data: ', '\n', data)
        data = np.array(data)
        if debug is True: print('Final data: ', '\n', data)
    if voltageclamp == False:
        abfWriter.writeABF1(data, outfile, freq, units='mV')
    elif voltageclamp == True:
        abfWriter.writeABF1(data, outfile, freq, units='pA')

"""# Build a list of all .csv, .txt, .asc files in the path folder
infilepath = glob.glob(path + '\*.csv')  # Get all .csv files in directory
infilepath.extend(glob.glob(path + '\*.txt'))
infilepath.extend(glob.glob(path + '\*.asc'))
print(infilepath)

# Define output filenames as initial filenames with .abf instead of whatever extension.
outfilename = []
for i in infilepath:
    outfilename.append(os.path.splitext(os.path.basename(i))[0] + '.abf')
#print(outfilename)
for i in outfilename:
    print('Output: ', i)

# This line actually runs the loop function on the path folder.
#for n, inputfile in enumerate(infilepath): #Enumerate is used to produce index n for outfilename, generated from infile.
    csvabf(inputfile, str(path + "\\" + outfilename[n]))"""
