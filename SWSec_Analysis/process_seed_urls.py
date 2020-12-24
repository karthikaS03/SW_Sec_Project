import json
import csv
import os
from database import db_operations





dbo = db_operations.DBOperator()

def insert_top_urls():
    urls_path = '../SWSec_Data/top_sites2.json'
    with open(urls_path,'r') as o:
        sites = json.loads(o.read())			
        for item in sites:
            rank = int(item['Country']['Rank'])
            url = 'https://' + item['DataUrl']	        
            dbo.insert_alexa_sites_table(url, rank )

def update_pwa_sites():
    urls_path = '../SWSec_Crawler/data/crawl_sites_sw.csv'
    with open(urls_path) as cf:
        csvreader = csv.DictReader(cf, delimiter=',' )			
        for row in csvreader:		
            if 'Alexa' in row['id']:
                rank = row['id'].split('_')[2] 
                url = row['url']
                print(url)
                dbo.update_alexa_sites_table(None, url, 'is_sw_found', 'True')
				
def update_crawled_sites():
    dir_path = '../SWSec_Crawler/output_logs/'
    for f in os.listdir(dir_path):
        if 'container_Seed_Alexa_' in f:
            rank = int(f.split('.')[0].split('_')[3])
            dbo.update_alexa_sites_table(rank, None, 'is_crawled', 'True')				

if __name__ == "__main__":
    # insert_top_urls()
    # update_pwa_sites()
    update_crawled_sites()