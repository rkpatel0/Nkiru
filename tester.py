import pandas as pd
import numpy as np
import webgen.web_report as web

COL = ['name', 'title', 'data', 'type']
df = pd.DataFrame(np.arange(12).reshape(4,3))
pages = pd.DataFrame(columns=COL, index=[0,1,2,3,4])
pages.ix[0] = ['try', 'Does it work 1', 'salkjfaskdfja', 'TEXT']
pages.ix[1] = ['try', 'Does it work 2', 'salkjfaskdfja', 'TEXT']
pages.ix[2] = ['try', 'Does it work 3', 'salkjfaskdfja', 'TEXT']
pages.ix[3] = ['New', 'Do it work 4', 'salkjfaskdfja', 'TEXT']
pages.ix[4] = ['New', 'Do it work 4', 'na', 'DATA']
pages['data'][4] = df

oGen = web.ReportGen()
oGen.web_report(pages.dropna())