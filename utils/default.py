#set up default parameters
#ver.220715
#1.新增variables: my_CSV, CSV, ID, RIS, column_PatientID, column_RIS, accession
#2.filter_cols新增AccessionNumber; filter_keys新增對應的RIS


#I/O paths:
dicom_point='../storage'  #資料路徑，StorageServer絕對路徑/dicom的資料夾掛載的節點
Storage_C='../128_C'  #儲存路徑，StorageServer絕對路徑/C的儲存空間掛載的節點
USB='../usb'  #USB裝置路徑，USB裝置掛載的節點
test='test'  #測試用資料夾
test_dcm='test/test_dcm'  #測試用dicom
df_template='utils/wanted_dcminfo_list_210121.csv'    #建立資料庫DataBase的資料表，讀取dicom head資料的欄位
my_CSV='my_CSV_template_220715.csv'  #2022/7/15新增
sorting_template='utils/sorting_list_220713.csv'    #建立sorting_list的資料表，讀取DataBase資料的欄位  #新增column "InputFolder" (update:2022/7/13)
DB_path='test/DataBase_test.csv'  #放入Filter篩選前的DataBase資料庫csv
input_path='input'  #輸入路徑，篩選前資料庫DataBase的資料表的存檔位置
output_path='output'  #輸出路徑，資料庫DataBase、sorting_list、篩選後的資料表的存檔位置
download_path=Storage_C+'/Dicom-default'  #下載路徑，去連結的dicom的存檔位置


#default of DataBase:
Type='raw'  #資料庫類別，指定讀取原始檔案(raw)或是去名化檔案(anonymous)
Period='000000'  #日期區間yyyymm
#default output names
save_csv_name='{}/DataBase_{}_{}-{}.csv'.format(output_path,Type,Period,'default')  #default name of DataBase Output_df  
save_sorting_csv_name='{}/sorting_list_{}_{}-{}.csv'.format(output_path,Type,Period,'default')   #default name of DataBase sorting list


#variables for Filter:
ALL='ALL'
CSV='CSV'  #2022/7/15新增
ID='ALL'  #2022/7/15新增
RIS='ALL'  #2022/7/15新增
ERCT='ERCT'  #GE BrightSpeed 急診CT
ct660='ct660'  #GE Optima 2樓CT
CT2F='ct660'  #GE Optima 2樓CT
vct660='vct660'  #GE Optima 情人湖CT
VCT='vct64'  #GE Optima 情人湖CT
MR3T='AWP45410'  #Siemens Skyra 3T MR
MR15:'HOST-FVJN2IHBD3'  #Philips Ingenia 1.5T MR
CT='CT'
MR='MR'
F='F'
M='M'
#可篩選的欄位的DB column names 與 keys的列表(*注意: filter_cols and filter_keys有對應關係)
column_PatientID,column_RIS='PatientID','AccessionNumber'  #2022/7/15新增
filter_cols=['PatientID','PatientSex','PatientAge','StudyDate','Modality','StationName','SeriesDescription','PerformedProcedureStepDescription','AccessionNumber']  #DB column names (2022/7/15: 新增AccessionNumber)
patient,sex,age,date,modality,station,sequence,description,accession='ALL','ALL','ALL','ALL','ALL','ALL','ALL','ALL','ALL'  #Default (2022/7/15: 新增RIS='ALL')
filter_keys=[patient,sex,age,date,modality,station,sequence,description,accession]  #對應的key (2022/7/15: 新增RIS)
#default output names
save_filted_csv_name='{}/filted_DataBase-{}.csv'.format(output_path,'default')   #default filted database saving name
save_filted_sorting_csv_name='{}/filted_sorting_list-{}.csv'.format(output_path,'default')   #default name of filted sorting list


#default of Download:
#default output names
save_download_csv_name='{}/download_DataBase-{}.csv'.format(output_path,'default')   #default download database saving name
save_download_sorting_csv_name='{}/download_sorting_list-{}.csv'.format(output_path,'default')   #default name of download sorting list


#hint:
check_above='請確認上述內容無誤後再執行下一步驟'
check_DB='資料路徑: {}\n即將建立 {} {} 的資料庫'
check_input='請確認input資料夾內容{}'
cut_float='%.{}f'
time_spend='{}，建立費時:{} {}'
total='共有 {} 個{}檔案'
DB_build='建立資料庫DataBase'
sort_build='sorting_list已建立'
built='{}已建立'
waiting='請稍等...'
unlink='去連結'
anonymous='匿名'
save='{} saved'
done='\n執行結束!'
#colors:  encode=0~5 & 31~48 & 91~99
BlueUnderline='\033[4;36m{}\033[0;0m'  
GreenUnderline='\033[4;32m{}\033[0;0m'  
RedBold='\033[1;31m{}\033[0;0m'
Blue='\033[94m{}\033[0;0m'
Red='\033[31m{}\033[0;0m'
BlueLight='\033[2;34m{}\033[0;0m'
PurpleLight='\033[2;35m{}\033[0;0m'
GreenItalic='\033[3;32m{}\033[0;0m'
YellowBG='\033[0;43m{}\033[0;0m'


print('DEFAULT PARAMETERS IMPROT SCCESS!')
print('對話框回報內容: {}；{}；{}；{}；粉紅色背景表示程式碼錯誤'.format(Red.format('紅色標示注意事項'),PurpleLight.format('亮紫色提示類別'),
    BlueLight.format('藍色標示input資料夾及{}'.format(Blue.format('input detail資料內容'))),GreenItalic.format('綠色標示output資料')))