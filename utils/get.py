#Define advanced functions
#ver.220713
#1.add get_save_file_name


__all__=['GetInputDir', 'GetDicomDict', 'Add2DF', 'CreateOutputDir', 'GetUnique', 'GetFullPath', 'GetFolderPath','get_target_list',
         'get_database','DcmAnonymous','Mask','get_filted_col_by_keys','get_filted_database','get_download_database','get_download_dicom',
         'get_save_file_name']  #2022/7/13 update
#import packages
from datetime import datetime  #2022/7/13 update
import os
import pandas as pd
import pydicom
from tqdm import tqdm
from utils.Functions import *
from utils.default import *

#輸入要取得的資料年、月、種類以及server路徑即可取得該月份的檔案列表
def get_target_list(Year,Month,Type='raw',Mount_point='../storage'):
    dir_path=[]
    tar_list=[]
    dcm4chee='dcm/dcm4chee-2.18.0-mysql/server/default/archive'
    
    if Type=='raw':
        target='{}/{}/{}/{}'.format(Mount_point,dcm4chee,str(Year),str(Month))
        date=os.listdir(target)
        for i in tqdm(date):
            path=os.path.join(target,i)
            dir_path.append(path)
            k=GetInputDir(path,filetype='',folder_only=False,dir_uniq=True)
            tar_list.extend(k)

    elif Type=='anonymous':
        target=Mount_point
        monthly_list=GetFolderPath(target,layers=4,printerror=False)   #layer是從mount point起算的第4層子資料夾(mount point/1st/2nd/3rd/4th/...)
        for path in tqdm(monthly_list):
            year=path.split('/')[-2]
            month=path.split('/')[-1]
            if year==str(Year) and month==str(Month):
                dir_path.append(path)
                k=GetInputDir(path,filetype='',folder_only=False,dir_uniq=True)
                tar_list.extend(k)

    else:
        print(Red.format('Please set parameters'))
    
    return(tar_list)
    
    
#讀取dicom head建立DataBase
def get_database(Target_list,Output_template,Save_csv_name=False):
    Output_df=Output_template
    for i,dcm in tqdm(enumerate(Target_list)):
        Output_df=Add2DF(dcm,Output_df,empty='')
        Output_df['InputDir'][i]=dcm

        #加上OutputDir
        p=CreateOutputDir(output_path='StorageServer:/dicom/',output_folder='',saparator='_',input_dcm=dcm,dcm_dir_rule=['InstitutionName','Modality','StudyDate'],
                        dcm_folder_rule=['AccessionNumber','PatientID','SOPInstanceUID'],by_date=True)
        s=p.split('_')
        output_path=s[0]+'_'+s[-2]+'/'+s[-1]
        Output_df['OutputDir'][i]=output_path

    if Save_csv_name!=False:
        Output_df.to_csv(Save_csv_name,index=0)   #excel欄位上限(1,048,576*16,384)
        print(Output_df.shape,GreenItalic.format(Save_csv_name), 'saved')
    
    return(Output_df)


#篩選對應的cols and keys(此步驟只是加速，即使沒篩選也可以直接放入get_ftiled_database)
def get_filted_col_by_keys(filter_cols,filter_keys,rule_out='ALL'):
    filted_col=[]
    filted_key=[]
    for i in range(len(filter_cols)):
        if filter_keys[i]!=rule_out:
            filted_col.append(filter_cols[i])
            filted_key.append(filter_keys[i])
    return(filted_col,filted_key)


#篩選放入的資料庫DataBase中，符合指定條件的rows，並建立篩選後的資料表database
def get_filted_database(Input_DB,Filted_key=filter_keys,Filted_col=filter_cols,Save_csv_name=False,Same=False):
    Index=[]
    for i in range(Input_DB.shape[0]):
        mask=[]
        for p,q in enumerate(Filted_key):
            sample=Input_DB.loc[i,Filted_col[p]]
            if Filted_col[p]=='PatientAge':  #因年齡欄位的格式是'xxxY'，要除去Y並換成數字
                sample=int(sample.split('Y')[0])
            mask.append(Mask(sample,q,same=Same))  #利用function Mask判斷X是否符合篩選條件
            
        if all(mask):  #所有條件都符合才會取該sample
            Index.append(i)

    Output_DB=Input_DB.loc[Index,:]  #篩選後的DB
    Output_DB.reset_index(drop=True,inplace=True)  #重新排列index，drop捨棄舊的index、inplace指定回df

    if Save_csv_name!=False:  #存檔
        Output_DB.to_csv(Save_csv_name,index=0)   #excel欄位上限(1,048,576*16,384)
        print(Output_DB.shape,GreenItalic.format(Save_csv_name), 'saved')
    
    return(Output_DB)


#將放數的資料庫DataBase中的路徑轉為container的相對路徑，並建立下載用的資料表database  #update:2022/7/1
def get_download_database(Input_DB,Dicom_point='../storage',Download_path='../128_C/Dicom-default',Save_csv_name=False):
    for i,InputDir in tqdm(enumerate(Input_DB['InputDir'])):
        Output_DB=Input_DB
        InputDir=Input_DB.loc[i,'InputDir']  #從InputDir取得檔案路徑
        #置換root of I/O:
        try:  #NaN會導致錯誤，加上除錯功能 (update:2022/7/1)
            split=InputDir.split('storage/')  #20220521 update: '/storage' replaced by 'storage/'
            file=split[1]
            IN=os.path.join(Dicom_point,file)  #new InputDir  #20220521 update: '/storage' replaced by 'storage/'

            month=str(Input_DB.loc[i,'StudyDate'])[4:6]
            RIS=str(Input_DB.loc[i,'AccessionNumber'])
            filename=str(Input_DB.loc[i,'SOPInstanceUID'])+'.dcm'
            OutputDir=os.path.join(Download_path,month,RIS,filename)  #new OutputDir

            #更新I/O to Output_DB:
            Output_DB.loc[i,'InputDir']=IN
            Output_DB.loc[i,'OutputDir']=OutputDir
        except:
            pass
        
        if Save_csv_name!=False:  #存檔
            Output_DB.to_csv(Save_csv_name,index=0)   #excel欄位上限(1,048,576*16,384)
            print(Output_DB.shape,GreenItalic.format(Save_csv_name), 'saved')
            
    return(Output_DB)

#將下載資料表內的資料去連結並存至指定位置，另外建立下載影像清單download_sorting_list作為病歷對照表  #update:2022/7/1
def get_download_dicom(Input_DB):
    for p,q in tqdm(enumerate(Input_DB['InputDir'])):
        try:    #新增除錯 (update:2022/7/1)
            dcm=DcmAnonymous(q,replace_rule=['PatientName','PatientBirthDate','OtherPatientIDs','PatientID'],replacer='')  #dicom去連結
            o=Input_DB.loc[p,'OutputDir']  #取得full name of output dicom

            #取得資料夾名稱，並建立子資料夾        
            split=o.split('/')
            folder=''
            for s in split[:-1]:
                folder=os.path.join(folder,s)
            if os.path.exists(folder)==False:
                os.makedirs(folder)

            dcm.save_as(o)  #儲存去連結dicom
        except:
            pass
        

#define a list of output files' name:  #2022/7/13 update
def get_save_file_name(Output_path,Save_file=['DataBase','sorting_list'],Prefix='',Suffix='',Filetype='csv'):
    DT=datetime.now()
    timestamp=datetime.strftime(DT,'%Y%m%d%H%M%S')
    
    #define output file name:
    Save_file_name=[]
    for file in Save_file:
        Save_file_name.append('{}/{}{}{}-{}.{}'.format(Output_path,Prefix,file,Suffix,timestamp,Filetype))
    
    return(Save_file_name)