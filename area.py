import pandas as pd
import numpy as np

from os.path import *

thaiArea =  dirname(__file__) + '/timelineform.xlsx'
thaiAreaDf = pd.read_excel(thaiArea, sheet_name="District&Province")
thaiAreaDf = thaiAreaDf.loc[:, 'เขต':]
thaiAreaDf.fillna(0, inplace=True)

districtTh = thaiAreaDf['เขต'].tolist()
districtEn = thaiAreaDf['District'].tolist()
provinceTh = [i for i in thaiAreaDf['จังหวัด'].tolist() if i != 0]
provinceEn = [i for i in thaiAreaDf['Province'].tolist() if i!= 0]