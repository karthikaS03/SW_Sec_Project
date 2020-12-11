import os
import pandas as pd 

dir_path = './demo_code/demo_logs/'
csv_file_path = '../SWSec_Data/crawl_sites_sw.csv'

url_ids = []

# def fetch_urls_from_file():
# 	url_file = pd.read_csv('./data/malicious_sites.csv')
# 	links = url_file['link']
# 	urls = {'M'+str(i):u for i,u in enumerate(links)}
# 	return urls
        
# malicious_sites = []
# for file in os.listdir(dir_path):
#         try:
#             urls = fetch_urls_from_file()
#             id = file.replace('M','')  
#             if os.path.exists(dir_path+file+'/'):
#                     #print('Processing folder '+dir_path+file+'/'+str(0))	
#                     chrome_log_file = dir_path+file+'/chrome_log.log'
#                     if os.path.exists(chrome_log_file):
#                         with open(chrome_log_file,'r') as f:
#                                 data = f.read()
#                                 res = data.find('=registerServiceWorker')
#                                 res2 = data.find('=requestNotification')
#                                 if res >-1:
#                                         print('Service Worker Found :: ', id, '::', urls.get(file))
#                                         malicious_sites.append(id+','+urls.get(file))

#                                 if res2 > -1:
#                                         print('Notification Requested  :: ',id, '::', urls.get(file))
#         except Exception as e:
#                 print(e)



def fetch_urls_from_file():
        df_urls = pd.read_csv(csv_file_path, header=0)# names=['id','url','processed'])
        print(df_urls.head())
        # df_urls = df_urls.where(df_urls['processed']==1)
        urls ={}
        for _,row in df_urls.iterrows():
                urls[row[0]] = row[1]
        # print(urls)
        return urls
                

def filter_notification_requests():
        import tarfile

        urls = fetch_urls_from_file()
                
        dir_path = './sw_sec_containers_data/'  
        
        for id,url in urls.items():
                if 'Alexa' not in id:
                        continue
                try:
                        id = 'container_Ana_'+id
                        # print(url)
                        if os.path.exists(dir_path+id+'/'):
                                # print(id,url)
                                log_tar_dir = dir_path+id+'/chrome_log_0.tar'
                                t = tarfile.open(log_tar_dir,'r')
                                chrome_log_file = 'chrome_debug.log'
                                if chrome_log_file in t.getnames():
                                        f = t.extractfile(chrome_log_file)
                                        data = f.read()
                                        res = data.find('=registerServiceWorker')
                                        
                                        res2 = data.find('=requestNotification')
                                        if res >-1:
                                                print('Found SW  :: ', id)
                                        if res2 >-1:
                                                print('Found Notification Request :: ', id)
                except Exception as e:
                        continue

filter_notification_requests()


# with open('./data/malicious_sites_sw.csv','w') as f:
#     f.write('\n'.join(malicious_sites))