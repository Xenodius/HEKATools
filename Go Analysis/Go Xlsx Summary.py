import numpy as np
from scipy import integrate
import os
import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
pd.set_option("display.max_columns", None)

rootpath = r'A:\Graphpad\GoExp'
Go1path = r'A:\Graphpad\GoExp\Experiments\Go\Go flx\Open Field\Raw Data'

walk = [x for x in os.walk(Go1path)][0][2]

"""writer = pd.ExcelWriter(rootpath + '\\GoD1_OF_data.xlsx', engine='xlsxwriter')

for i in walk:
    titlen = len(i)
    title = i[0:(titlen-4)]
    data = pd.read_table(Go1path + '\\' + i)
    data['Group'] = title
    data.to_excel(writer, title[0:30])

writer.save()"""

writer = pd.ExcelWriter(rootpath + '\\Go_OF_summary.xlsx', engine='xlsxwriter')
finaldata = pd.DataFrame()

for i in walk:
    titlen = len(i)
    title = i[0:(titlen-4)]
    data = pd.read_table(Go1path + '\\' + i)
    data['Group'] = title
    finaldata = finaldata.append(data)
    data.to_excel(writer, title[0:30])

finaldata.to_excel(writer, 'All')
writer.save()

print(walk)