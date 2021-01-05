import os
import re
from datetime import datetime
from database import db_operations

log_path = '../SWSec_Crawler/output_logs/'

log_events = set(['creating!!', 'Execution complete!!', 'exporting files'])

dbo = db_operations.DBOperator()

for file in os.listdir(log_path):
    if 'Alexa' not in file:
        continue
    print(file)
    iter = 0
    with open(log_path+file, 'r') as f:
        line = f.readline()
        while line:
            
            if any([x in line for x in log_events]):
                if 'creating!!' in line:
                    iter +=1
                m = re.search('([\w]+)\s-\s+[\w]+\(\)\s+-\s+\[([\w-]+\s[\w:]+)\]\s([\w\s!:]+)', line)
                if m :                    
                    # print(m.groups())
                    dbo.insert_container_log(m.groups()[0], iter,  m.groups()[1], m.groups()[2])
            line = f.readline()
    
    