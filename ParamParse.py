'''Basal parameters:
Rewrite Rheo with dataframe columns/plots build on "if switch is true:" statements for
1. building the dataframe 2. creating grid of per-cell multiplots.

Resting membrane potential: Immediately after whole-cell mode established
Rn: Linear fit of subthreshold currents that did not evoke any active conductance
    (e.g. R1S1Mean slope for Frequency = 0 or NaN)
Rheobase: Stimulus current at first potential
AP threshold: membrane potential at first spike
AP amplitude: threshold event baseline + event peak delta from baseline
AP half-width: --> from event half-width
mAHP: median afterhyperpolarization; median of minimum potentials in ~100ms after AP
Delay to 1st spike: Time to first spike after the stimulus (use init var to set time of stim in sweep)

To build from new Patchmaster auto-export: Keep in mind different headers of Patchmaster vs. Nestopatch binaries.
Fill in list of filenames-- cell_protocol, and var date. Convert to list of (MM-DD_Cell_###-Protocol)
    using _### from original filename, and
    !!! Use Parameters, group flags, and Target to Notebook to generate a .txt to rename every sweep.
    Review what could be done with parameters.
        1. Control Vclamp/Cclamp
        2. Compare relative time of series, to optionally plot one series type in
           real "experimental" vs. just concatenated times
        3.
'''
import numpy as np
import pandas as pd
import glob
import os

# Enable/disable all rows/columns or columns
# pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option("display.max_columns", None)
# pd.set_option("display.max_rows", None)

#Vars
path = r'C:\Program Files (x86)\HEKA2x903\Data\PyABF'
debug = True # For print statements throughout
series_column_names = ['Series', 'Sweeps', 'Time']
column_range = range(1, 7, 1)
amp_column_names = ['ClampMode', 'V-pipette', 'Gain', 'C-fast', 'C-slow', 'R-series']
amp1_column_names = {}
amp2_column_names = {}
for i in column_range:
    amp1_column_names[i] = amp_column_names[i - 1] + '_1'
    amp2_column_names[i] = amp_column_names[i - 1] + '_2'
writer = pd.ExcelWriter(path + '\\parameters.xlsx', engine='xlsxwriter')

#Read line-by-line and construct series to generate Dataframe, to avoid column discarding or errors.
paramfilepath = glob.glob(path + '\*parameter*') # Get notebook output from file including name "parameters"
print('filepath; ', paramfilepath)

df = pd.DataFrame()
with open(paramfilepath[0], 'r') as f:
    for line in f:
        df = pd.concat([df, pd.DataFrame([tuple(line.strip().split('\t'))])], ignore_index=True)
# print(df)
seriesnum = df.iloc[0,1]  # 2nd element of first row. Number of series
df = df.iloc[1:] # Drop first row after retrieving total seriesnum
# print(df)
# rows = df.shape[0]  # Number of rows

## Subset df by series, amp1, amp2 rows
amp1_df = df[df[0].str.contains('EPC10_USB/2-1')]
amp2_df = df[df[0].str.contains('EPC10_USB/2-2')]
ser_df = df[~df[0].str.contains('EPC10')]
# Rename columns
amp1_df = amp1_df.rename(columns=amp1_column_names).drop(labels=0, axis=1)
amp2_df = amp2_df.rename(columns=amp2_column_names).drop(labels=0, axis=1)
ser_df = ser_df.dropna(axis=1, how='all')
ser_df.columns = series_column_names
ser_df['Series'] = ser_df['Series'].str.replace(r'\"', '') # Remove apostrophes from series df
amp1_df['ClampMode_1'] = amp1_df['ClampMode_1'].str.strip()  # Remove whitespace preceding clamp mode
amp2_df['ClampMode_2'] = amp2_df['ClampMode_2'].str.strip()
# ser_df = ser_df.assign(Series=ser_df[0].str.replace(r'\"', '')) ### Chained assignment seems not to matter here.
# ser_df = ser_df.loc[,ser_df[0].str.replace(r'\"', '')]

if debug is True: print('Preindex: ', amp1_df)
if debug is True: print('Preindex: ', amp2_df)
if debug is True: print(ser_df)

amp1_df.index = ser_df.index # Unify indices
amp2_df.index = ser_df.index
if debug is True: print('Postindex: ', amp1_df)
if debug is True: print('Postindex: ', amp2_df)
parm_df = ser_df.join(amp1_df, how='outer').join(amp2_df, how='outer') # Join dataframes
parm_df.index = np.arange(1, len(parm_df)+1) # Reindex to actual series number
if debug is True: print('Joined: ', '\n', parm_df)

parm_df.to_excel(writer, 'Parameters') # Write to excel sheet
writer.save()






