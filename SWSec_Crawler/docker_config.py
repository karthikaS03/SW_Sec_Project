import os

project_dir = os.getcwd()

#Docker
docker_image = 'dockerammu/sw_sec_chromium:pwa'
docker_user = 'pptruser'
docker_container_home = '/home/pptruser/'
docker_shared_dir_root = project_dir
vols = {}# docker_shared_dir_root + '/app' :{'bind':docker_container_home + 'app','mode':'rw'}}
''', 
	docker_shared_dir_root + '/logs'          :{'bind':docker_container_home + 'logs','mode':'rw'},
	        docker_shared_dir_root + '/screenshots'   :{'bind':docker_container_home + 'screenshots','mode':'rw'},
            docker_shared_dir_root + '/resources'     :{'bind':docker_container_home + 'resources','mode':'rw'},
	       
	      }
'''
collection_script   = 'run_chromium.js'


CRAWL_MAX_CONTAINERS = 20
CRAWL_TIMEOUT = 300
ANALYSIS_MAX_CONTAINERS = 50
ANALYSIS_TIMEOUT = 3600 * 72  # 900 ->15 mins


# CONFIG_EXPORT_PATH = './containers_data/'

CRAWL_URL_PATH = '../SWSec_Data/top_sites2.json' #'../SWSec_Data/navigatorserviceworkerregister.csv'
ANALYSIS_URL_PATH = './data/filtered_sw_urls.csv'

###
# To be changed as needed
###
CRAWL_SW = True
IS_MALICIOUS = False

if CRAWL_SW ==True:
	CONFIG_EXPORT_PATH = './crawl_containers_data/'
else:
	CONFIG_EXPORT_PATH = './sw_sec_containers_data/'

def get_logger(name, init=0):    
	import logging

	format='%(name)s - %(funcName)20s() - %(message)s'

	logger = logging.getLogger(name = name)
	# print(name,init,logger)
	if init == 0:
		return logger
	else:
		handler = logging.FileHandler('./output_logs/'+name+'.log')
		handler.setFormatter(logging.Formatter(format))
		logger.setLevel(logging.INFO)
		logger.addHandler(handler)
		return logger