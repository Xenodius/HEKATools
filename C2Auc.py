import pyabf as pa
import numpy as np
from scipy import integrate
import os
import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

path = r'C:\Program Files (x86)\HEKA2x91\Data\YM'
plot = True

def ms(milli):
    return int(milli*20)

def sweep(file, left,right):
    return file[ms(left):ms(right)]

def parse_auc(date, filepath):
    #Glob
    filename = file[len(path + '\\' + date) + 1:len(file) - 4]
    #Data
    c2abf = pa.ABF(filepath)
    c2abf.setSweep(5)
    baseline = np.mean(c2abf.sweepY[ms(929):ms(949)])
    peak = np.argmax(sweep(c2abf.sweepY, 751,780))/20 + 750
    print(date, ', ', filename, ', ', peak)
    trace = sweep(c2abf.sweepY, peak, 949) - baseline
    samples = len(trace)
    xtime = np.linspace(0, samples/20, samples)
    #Quality Control Plot
    traceplot = sweep(c2abf.sweepY, peak - 50, 999) - baseline
    absxtime = np.linspace(0, (samples+2000)/20, samples+2000) + peak-50 # (samples+2000) based on 100ms*20 margin for traceplot
    if plot:
        sns.relplot(x=absxtime, y=traceplot, kind="line", linewidth=.5)
        plt.axvline(peak, 0, c2abf.sweepY[int(peak*20)], color='red', linestyle='--', linewidth=.5) # x val, min, max
        plt.axvline(949, 0, c2abf.sweepY[int(peak*20)], color='red', linestyle='--', linewidth=.5)  # x val, min, max
        plt.axhline(0, 0, 1, color='black', linewidth=.2)
        plt.rcParams['savefig.dpi'] = 900
        plt.savefig(path + '\\' + date + '__' + filename + '.png')
    #plt.close(fig)
    return integrate.simps(trace, xtime)

walk = [x for x in os.walk(path)][0][1]
c2d = {}
output = pd.DataFrame()

for i in walk:
    files = glob.glob(path + '\\' + i + '\\*DRG-C2*')
    c2d[i] = files

for date, files in c2d.items():
    for file in files:
        try:
            area = parse_auc(date, file)
            # df = pd.DataFrame([date, file, area]).T.rename({0: 'date', 1: 'file', 2: 'area'}, axis=1)
            dict = {'date': date, 'file': file, 'area': area}
            output = output.append(dict, ignore_index=True)
        except Exception as e:
            print('Exception: ', e , file)
            pass

writer = pd.ExcelWriter(path+'\\'+'outdata.xlsx', engine='openpyxl')
output.to_excel(writer, 'C2Area')
writer.save()
writer.close()

print('debughook')