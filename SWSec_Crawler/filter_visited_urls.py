import os
import pandas as pd 

dir_path = './demo_code/demo_logs/'
url_ids = []

def fetch_urls_from_file():
	url_file = pd.read_csv('./data/malicious_sites.csv')
	links = url_file['link']
	urls = {'M'+str(i):u for i,u in enumerate(links)}
	return urls
        
malicious_sites = []
for file in os.listdir(dir_path):
        try:
            urls = fetch_urls_from_file()
            id = file.replace('M','')  
            if os.path.exists(dir_path+file+'/'):
                    #print('Processing folder '+dir_path+file+'/'+str(0))	
                    chrome_log_file = dir_path+file+'/chrome_log.log'
                    if os.path.exists(chrome_log_file):
                        with open(chrome_log_file,'r') as f:
                                data = f.read()
                                res = data.find('=registerServiceWorker')
                                res2 = data.find('=requestNotification')
                                if res >-1:
                                        print('Service Worker Found :: ', id, '::', urls.get(file))
                                        malicious_sites.append(id+','+urls.get(file))

                                if res2 > -1:
                                        print('Notification Requested  :: ',id, '::', urls.get(file))
        except Exception as e:
                print(e)

with open('./data/malicious_sites_sw.csv','w') as f:
    f.write('\n'.join(malicious_sites))