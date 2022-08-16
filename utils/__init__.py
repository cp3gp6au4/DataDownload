#to indicate the directory as a module
#ver.220127

#import packages
import pydicom
import os
import pandas as pd
from tqdm import tqdm
from shutil import copy
import time
from datetime import datetime


#import default varialbes and paramerters:
from utils.default import *


#時間戳記
DT=datetime.now()
timestamp=datetime.strftime(DT,'%Y%m%d %H:%M:%S')


#create output folder
if not os.path.exists(output_path):
      os.makedirs(output_path)

        
#read default templates:
df=pd.read_csv(df_template)  #預設的資料庫DataBase的資料表欄位
df_sorting=pd.read_csv(sorting_template)  #預設的sorting_list的資料表欄位
DB=pd.read_csv(DB_path,dtype='str').replace('NotInDict','')  #預設的篩選前資料庫



print(timestamp,'PACKAGES IMPORT SUCCESS!\n請執行下一個步驟')
