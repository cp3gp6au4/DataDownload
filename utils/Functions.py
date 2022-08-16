#Define basic functions
#ver.220715
#1.update Mask to ver1-1-220715


__all__=['GetInputDir', 'GetDicomDict', 'Add2DF', 'CreateOutputDir', 'GetUnique', 'GetFullPath', 'GetFolderPath','DcmAnonymous','Mask','GetConcatedDF']

#import packages
import os
import pandas as pd
import pydicom


# GetInputDir: ver2-0-200326
#自動讀取指定路徑下包含dicom的資料夾作為input_dir
def GetInputDir(aim_path,filetype='.dcm',folder_only=False,dir_uniq=True):
    input_dir=[]
    for dirpath, dirname, filename in os.walk(aim_path):
        for f in filename:
            if filetype in f:
                if folder_only==True:  #新增dir_only開關 (update:2020/03/26)
                    path=dirpath     #開啟則回傳含有filetype的"資料夾"路徑清單(不重複) (update:2020/03/26)
                else:                             
                    path=os.path.join(dirpath,f)  #關閉則回傳含有filetype的"檔案"路徑經單 (update:2020/03/26)
                
                if dir_uniq==True:
                    if path not in input_dir:
                        input_dir.append(path)    #取不重複的值
                else:
                    input_dir.append(path)
    return(input_dir)


# GetDicomDict: ver1-3-200316
#將dicom的指定資料取出做成dictionary
def GetDicomDict(input_dcm,key=['StudyDate','Modality','AccessionNumber','PatientID','PatientSex','PatientAge',
                                'PatientName','OtherPatientIDs','PatientBirthDate',
                                'Manufacturer','StationName','InstitutionName','ReferringPhysicianName','BodyPartExamined','InstanceCreationDate','InstanceCreationTime',
    'ProtocolName','StudyDescription','RequestedProcedureDescription','PerformedProcedureStepDescription','CodeMeaning','SeriesDescription','SeriesNumber','InstanceNumber'
                               ],empty='NotInDicomInfo'):
    if type(input_dcm)==pydicom.dataset.FileDataset:
        dcminfo=input_dcm
    else:
        try:
            dcminfo=pydicom.dcmread(input_dcm)
        except:
            print('Input must be DICOM (in full path) or DICOM info',input_dcm,sep='\n')   #方便除錯，加印錯誤的輸入input_dcm (update:2020/03/16)
            raise TypeError       

    dcm_dict={}
    for i in key:
        try:  
            updater={i:str(dcminfo[i].value)}  #change value to str
        except:
            updater={i:empty}
        dcm_dict.update(updater) 
    return dcm_dict


#Add2Df: ver2-3-200507
#Add Dicom Info to a DataFrame
#DEPEND on "GetDicomDict"
def Add2DF(input_data,input_df=False,empty='NotInDict'):   
    
    #取得dcm_dict & col:  (#update:2020/05/07)
    dcm_dict={}
    col=[]
    if type(input_data)==dict:
        dcm_dict=input_data
        col=input_data.keys()

    elif type(input_data)==list:
        for i in range(len(input_data)):
            dcm_dict.update({i:input_data[i]})
        col=input_data

    else:
        if type(input_data)==pydicom.dataset.FileDataset:
            dcminfo=input_data
        else:
            try:
                dcminfo=pydicom.dcmread(input_data)
            except:
                print('Input can be DICOM (in full path) or DICOM info',input_dcm,sep='\n') 
                raise TypeError  
        
        col=dcminfo.dir()
        try:
            dcm_dict=GetDicomDict(dcminfo,col,empty='NotInDicomInfo')

        except:
            print('NOTE: function Add2DF DEPENDS on function GetDicomDict')
            raise NameError


    DF=pd.DataFrame()
    if type(input_df)!=bool:
        if type(input_df)==pd.DataFrame:
            DF=input_df
        elif type(input_df)==dict:
            DF=pd.DataFrame.from_dict([input_df])            
        else:# type(input_df)==list:
            for i in input_df:
                DF[i]=i 

        col=DF.columns
    
    
    row={}
    if type(input_data)==list:
        for i in range(len(col)):
            try:
                row.update({col[i]:dcm_dict[i]})
            except:
                row.update({col[i]:'TooManyColunms'})
    else:
        for i in col:
            try:
                row.update({i:dcm_dict[i]})
            except:
                row.update({i:empty})
       
    output_df=DF.append(row,ignore_index=True)
    return(output_df)


#CreateOutputDir: ver1-3-200401
#定義"建立存檔路徑"的函數  #update:2020/04/01
#DEPEND on "GetDicomDict"
#input a dictionary and rules to create ouput directory
#rules are in list, default as "Modality/StationName/StudyDate/AccessionNumber_PatientID"   #Default說明之前好像忘記改，修正 (update:2020/04/01)
def CreateOutputDir(output_path,output_folder='',saparator='_',input_dcm=False,dcm_dir_rule=['Modality','StationName','StudyDate'],
                    dcm_folder_rule=['AccessionNumber','PatientID'],by_date=False):   #取date的tag由InstanceCreationDate改為StudyDate (update:2020/04/01)
    Dir=''
    if type(output_path)==list:
        for i in output_path:
            Dir=os.path.join(Dir,i)
    else: 
        Dir=os.path.join(Dir,output_path)
    
    Folder=[]
    if type(output_folder)==list:
        for i in output_folder:
            Folder.append(i)
    else: 
        if output_folder=='':
            pass
        else:
            Folder=[output_folder] 
    
    
    if input_dcm!=False:   #因GetDicomDict本身已有除錯機制，故判斷式改成僅 "!=False" (update:2020/04/01)
        try:
            dcm_dict=GetDicomDict(input_dcm,key=dcm_dir_rule+dcm_folder_rule,empty='NotInDicomInfo')
        except:
            print('NOTE: function CreateOutputDir DEPENDS on function GetDicomDict')   #修正NOTE標語: "Add2DF">>"CreateOutputDir" depend on ... (update:2020/04/01)
            raise NameError

        for i in dcm_dir_rule:
            if i == 'StudyDate':   #取date的tag由InstanceCreationDate改為StudyDate (update:2020/04/01)
                if by_date==True:
                    Date=os.path.join(dcm_dict[i][0:4],dcm_dict[i][4:6],dcm_dict[i][6:])
                else:
                    Date=dcm_dict[i]
                Dir=os.path.join(Dir,Date)
            else:
                Dir=os.path.join(Dir,dcm_dict[i])

        for i in dcm_folder_rule:
            Folder.append(dcm_dict[i])


    folder=saparator.join(Folder)    
    output_dir=os.path.join(Dir,folder)
    
    return(output_dir)


#ver2-1-220713  
#Get specific column Unique DataFrame as output_df and count repeat Size  #update: 2020/07/13
#DEPEND on "Add2DF"
def GetUnique(input_df,output_df,unique='AccessionNumber',empty='NotInDF'):
    unique_obj={}
    obj_count={}
    for p,q in enumerate(input_df[unique]):
        column_values={}
        
        try:   #2022/7/13: 增加除錯，以免input_df內沒有'SeriesDescription'
            seq=input_df.loc[p,'SeriesDescription']   #2022/1/20: 取序列資料SeriesDescription
        except:
            seq=empty
        try:   #2022/7/13: 增加讀取資料夾InputFolder
            inputdir=input_df.loc[p,'InputDir']
            infolder='/'.join(inputdir.split('storage/')[-1].split('/')[:-1])
        except:
            infolder=empty
            
        if q not in unique_obj.keys():
            count=1
            sequences=[seq]   #2022/1/20: 第一次先建立序列list
            infolders=[infolder]   #2022/7/13: 第一次先建立序列list
            for i in output_df.columns:
                try:
                    column_values.update({i:input_df[i][p]})
                except:
                    column_values.update({i:empty})
                    
            unique_obj.update({q:column_values})
        else:
            sequences=obj_count[q][1]   #2022/1/20: 取obj_count內的序列list
            infolders=obj_count[q][2]  #2022/7/13: 取obj_count內的infolder list
            count=obj_count[q][0]+1   #2022/1/20: obj_count的value變為tuple
            if seq not in sequences:
                sequences.append(seq)
            if infolder not in infolders:
                infolders.append(infolder)
            
        obj_count.update({q:(count,sequences,infolders)})   #2022/1/20: 將list of SeriesDescription加到obj_count  #2022/7/13: 將infolder資訊新增到obj_count tuple內
        unique_obj[q].update({'Size':obj_count[q][0]})   #2022/1/20: obj_count的value變為tuple，Size=0、sequences=1
        unique_obj[q].update({'Sequence':obj_count[q][1]})   #2022/1/20: 將序列資料更新到unique_obj
        unique_obj[q].update({'InputFolder':obj_count[q][2]})  #2022/7/13: 將infolder資訊新增到unique_obj
    
    for k in unique_obj.keys():            
        output_df=Add2DF(unique_obj[k],output_df)
        
    return(output_df)


#GetFullPath: ver1-0-210601
#Get full son folder/file path of root; Get blank list if the root is not a directory  #update: 2021/06/01
def GetFullPath(root,printerror=False):
    #list all contents by os.listdir if root is a directory
    if os.path.isdir(root):
        branch_list=os.listdir(root)
        full_path=[]
        for branch in branch_list:
            full_path.append(os.path.join(root,branch))
            
    #Get blank list if root is not a directory
    else:
        full_path=[]
        if printerror==True:
            print('{} is not directory'.format(root))  #Optional: to print the wrong input
    
    return(full_path)


#GetFolderPath: ver1-0-210601
#Get full son folder/file path of specific layers of aim_path; Optional to print the input which was not a directory  #update: 2021/06/01
#DEPEND on "GetFullPath"
def GetFolderPath(aim_path,layers,printerror=False):
    layer=0
    path=[aim_path]
    
    while layer<layers:
        folders=path
        folderpath=[]
        
        for folder in folders:
            folderpath.extend(GetFullPath(folder,printerror))
            
        path=folderpath
        layer+=1
        
    return(folderpath)


#DcmAnonymous: ver2-0-200222
#將指定(Dicom)dcminfo中 特定欄位的值 取代
#default remove PatientName, BirthDay and OtherPatientID (replace as "")
def DcmAnonymous(input_dcm,replace_rule=['PatientName','PatientBirthDate','OtherPatientIDs'],replacer=''):
    
    if type(input_dcm)==pydicom.dataset.FileDataset:
        dcminfo=input_dcm
    else:
        dcminfo=pydicom.dcmread(input_dcm)
    
    for i in replace_rule:
        try:
            dcminfo[i].value=replacer
        except:
            pass
        
    return dcminfo


#ver1-1-220715
#Return if the input sample in the key or quals to the key
#判斷sample是否包含於指定的key中，same可設定文字類型的key是True"完全相同"或False"包含"
def Mask(sample,key='ALL',same=True): 
    mask=False
    #檢查Input  #2022/7/15 add
    try:
        str(sample)
    except:
        raise TypeError('INPUT PARAMETER ERROR, TYPE of "sample" must be string')  #2022/7/15: raise可以直接print描述(不須另外print)
        
    #判斷key的type,再進行比對
    if key=='ALL' or key==['ALL']:  #若為ALL代表不需要篩選
        mask=True
    elif type(key)==tuple:  #若為tuple擇要篩選介於兩個數字間的區間
        if int(key[0])<=int(sample)<=int(key[1]):
            mask=True
    else:  #其他狀況是文字篩選，先將key轉為list，再迭代判斷
        if type(key)==str or type(key)==int:
            key=[str(key)]
        else:
            try:
                list(key)
            except:
                raise TypeError('INPUT KEY ERROR, PLEASE CHECK')  #2022/7/15: raise可以直接print描述(不須另外print)
        
        #判斷key是否包含於sample中 
        if same==True:  #完全相同 #2022/7/15 update
            if sample in key:
                mask=True
        elif same==False:  #包含
            for k in key:
                if k=='':  #2022/7/15: '' always in a string，增加判斷式以排除錯誤篩選
                    pass
                elif str(k).lower() in sample.lower():  #2022/7/15: 將k轉換為str,避免輸入int導致錯誤; 用str.lower()排除大小寫問題
                    mask=True
                    break
        else:
            raise TypeError('INPUT PARAMETER ERROR, PLEASE SET "same" as "TRUE" or "FALSE"')  #2022/7/15: raise可以直接print描述(不須另外print)
    return(mask)


#ver2-0-220127
#Concat df in input_df_list by specific cols and replace specific value and NaN by replacer
#將指定的df路徑列表內所有的df依照指定欄位串接，並取代特定值及缺失值NaN
def GetConcatedDF(input_df_list,cols=False,replace_value=False,ignore_missing=True,replacer=''):
    output_df=pd.DataFrame()
    for i in input_df_list:
        df=pd.read_csv(i,dtype='str')  #讀取路徑列表input_df_list內的csv
            
        #篩選coluns:
        if cols!=False:
            for c in cols:
                try:
                    col=df[c]
                except:
                    if KeyError:
                        df[c]=''
            df=df[cols]
        
        output_df=output_df.append(df,ignore_index=True)  #將df串接到output_df
        
        #output_df完成後，取代將缺失值及特定值:  #2022/1/27 update
        if replace_value!=False:
            output_df=output_df.replace(replace_value,replacer)  #replace specific value with replacer
        if ignore_missing:
            output_df=output_df.fillna(replacer)   #將NaN取代成''
            
    return(output_df)