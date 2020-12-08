import os
import pandas as pd 
import time
from datetime import date

from parse_utils import *

csv_file_path = '../../SWSec_Crawler/data/crawl_sites_sw.csv'

def modify_csv_file(urls):
        
        while True:                   
                df_urls_recent = pd.read_csv(csv_file_path, names=['id','url','processed'])
                df_urls_recent['processed'] =  df_urls_recent.apply( lambda x: 1 if ((x['id']) in urls or x['processed']==1 )else 0, axis=1)
                if os.access(csv_file_path, os.W_OK):
                        df_urls_recent.to_csv(csv_file_path, index=False, header=False)
                        print('file modified!!')
                        break

def fetch_urls_from_file():
        df_urls = pd.read_csv(csv_file_path, names=['id','url','processed'])
        df_urls = df_urls.where(df_urls['processed']==0)
        urls ={}
        for _,row in df_urls.iterrows():
                urls[row[0]] = row[1]
        print(urls) 
        modify_csv_file(urls)
        return urls
                
def get_service_worker_files(urls):
        import tarfile

        def get_file_name(url):
                fname = url.split('/')[-1]
                fname = fname if '?' not in fname else fname.split('?')[0]
                return fname

        
        dir_path = '../../SWSec_Crawler/crawl_containers_data/'  
        sw_dir_path = '../../SWSec_Data/ServiceWorkers/'
        for id,url in urls.items():
                try:
                        id = 'container_'+id
                        print(url)
                        if os.path.exists(dir_path+id+'/'):
                                log_tar_dir = dir_path+id+'/chrome_log_0.tar'
                                t = tarfile.open(log_tar_dir,'r')
                                chrome_log_file = 'chrome_debug.log'
                                if chrome_log_file in t.getnames():
                                        f = t.extractfile(chrome_log_file)
                                        line = f.readline()
                                        while(line):
                                                if '=registerServiceWorker' in line:
                                                        entries = parse_log_entry(f)
                                                        url  = entries['request_url']
                                                        log_sw_url(url)
                                                        
                                                if any([lbl in line for lbl in ['=RunClassicScript','=FetchClassicImportedScript'] ]):
                                                        entries = parse_log_entry(f)
                                                        code = entries['sw_info'] if 'sw_info' in entries else entries['data'] if 'data' in entries else None
                                                        if code != None:
                                                                f_name = str(id).replace('container_','')+'_'+get_file_name(entries['request_url']) 
                                                                with open(sw_dir_path + f_name,'w') as jsf:
                                                                        jsf.write(code)

                                                line = f.readline()
                except Exception as e:
                        print(e)
                        continue

def log_sw_url(sw_url):
        sw_dir_path = '../../SWSec_Data/'
        with open(sw_dir_path+'sw_urls_tmp.csv', 'a+') as swf:
                swf.write(','.join([sw_url,'False', date.today().strftime('%d/%m/%Y'), 'False', date.today().strftime('%d/%m/%Y'),'-1','','','0' ,'\n']))


def main():
        while True:
                urls = fetch_urls_from_file()
                get_service_worker_files(urls)                
                time.sleep(1800)



if __name__ == "__main__":
        main()
