import pygraphviz as pgv
from datetime import datetime, timedelta
from parse_logs.parse_utils import *
import pandas as pd 
import matplotlib.pyplot as plt


from database import db_operations

dbo = db_operations.DBOperator()

# dbo.log_db =False

LOG_FILE = None

NODE_LOG_CALLS = set(['LogSWInfo', 'LogSWEvent', 'LogSWContextInfo', 'LogNotificationData', 'DidCallFunction' ,                        ])

START_END_EVENT_MAPS = {'InitializeOnWorkerThread':'PrepareForShutdownOnWorkerThread',
                        'StartEvent':'EndEvent', 
                        'StartFetchEvent':'DidHandleFetchEvent', 
                        'StartFunctionCall':'EndFunctionCall',
                        'DispatchPushEvent': 'DidHandlePushEvent',
                        'DispatchNotificationClickEvent':'DidHandleNotificationClickEvent',
                        'DispatchNotificationCloseEvent':'DidHandleNotificationCloseEvent',
                        'Fetch':'DidReceiveResponse',
                        # 'InstallNewDocument':'DocumentWasClosed'
                        # 'DispatchFetchEventForMainResource':
                        }
FOCUSSED_LOG_NAMES = set(['registerServiceWorker', 'InitializeOnWorkerThread',
'PrepareForShutdownOnWorkerThread', 
# 'InstallNewDocument','DocumentWasClosed',
                        'StartEvent','EndEvent', 
                        'StartFetchEvent','DidHandleFetchEvent', 
                        'StartFunctionCall','EndFunctionCall',
                        'DispatchPushEvent', 'DidHandlePushEvent',
                        'DispatchNotificationClickEvent','DidHandleNotificationClickEvent',
                        'DispatchNotificationCloseEvent','DidHandleNotificationCloseEvent',
                        'Fetch','FetchAndRunClassicScript', 'importScripts','showNotification',
                        'CreateNotificationData', 'DidReceiveResponse',
                        'ResetIdleTimeout','requestPermission','PermissionDecided','openWindow'
                        ])

# FOCUSSED_LOG_NAMES =set(['openWindow'])

PROCESS_TASK_USAGE_METHOD = 'FillProcessData'

FOCUSSED_PROCESS_TAGS = [
                # 'Tab', 
                'Service Worker'
                # ,'Browser'
                ]

NODE_ID = 0

_TIME_STR_FORMAT = "%Y-%m-%d-%H:%M:%S"



def get_node_id():
    global NODE_ID

    NODE_ID +=1
    return NODE_ID

def get_next_node_info():
    line = 'blah'
    if not line:
        return None
    timestamp = None
    proc_id = None
    node_id = -1
    try:
        while(line):
            
            line = LOG_FILE.readline().decode('utf-8')

            if 'LOG::Forensics' in line and line.count(':')>1 and 'DebugInfo' not in line and 'LogTaskUsageInfo' not in line:
                
                proc_id = line.split(':')[0]
                proc_id = int(proc_id.split('[')[1])
                
                time = line.split(':')[2] 
                try:
                    if int(time[:2])>5:
                        year = 2020
                    else:
                        year = 2021
                    timestamp = datetime(year, int(time[:2]), int(time[2:4]), int(time[5:7]),int(time[7:9]), int(time[9:11]), int(time[12:]))
                    ## container ahead of time by 5 hours
                    timestamp = timestamp - timedelta(hours=5)
                except Exception as e:
                    print(e)
                    timestamp = None
                entries = parse_log_entry(LOG_FILE)
                    
                if 'func_name' in entries:
                    
                    if entries['func_name'] in FOCUSSED_LOG_NAMES:                        
                        node_id = get_node_id()
                        G.add_node(node_id, label=entries['func_name'])
                        if entries['func_name'] == 'DispatchPushEvent':
                            print('\tPUSH ::', entries['script_url'], entries['registration_id'])
                        
                    elif entries['func_name']  == PROCESS_TASK_USAGE_METHOD:                        
                        parse_task_usage(timestamp, entries)

                return node_id,timestamp, proc_id, entries
            
    except Exception as ex:
            print(ex)

def parse_task_usage(timestamp,log_entries):
    global process_task_usage
    
    if 'process_title' in log_entries:
        task_usage_info = {'title': log_entries['process_title'], 'cpu': float(log_entries['process_cpu']),
                            'memory': float(log_entries['process_memory']), 'timestamp': timestamp}

        process_task_usage['title'].append(task_usage_info['title'])
        process_task_usage['cpu'].append(task_usage_info['cpu'])
        process_task_usage['memory'].append(task_usage_info['memory'])
        process_task_usage['timestamp'].append(timestamp)
        
        # print(task_usage_info)
        # print(process_task_usage)
        # dbo.update_process_task_usage_table(CONTAINER_ID, task_usage_info)


def _truncate_time_to_sec(t):
        
    t_str = t.strftime(_TIME_STR_FORMAT)
    return datetime.strptime(t_str, _TIME_STR_FORMAT)


def _truncate_time_to_min(t):
    TIME_STR_FORMAT ="%Y-%m-%d-%H:%M"
    
    t_str = t.strftime(TIME_STR_FORMAT+":00")
    return datetime.strptime(t_str, TIME_STR_FORMAT+":00")
    
def plot_task_usage(id):
    global process_task_usage
    
    df = pd.DataFrame(process_task_usage)
    print(df.head())
    if not df.empty :
        try:
            # print(min(df['timestamp']),max(df['timestamp']))
            min_time = _truncate_time_to_sec(min(df['timestamp']))
            max_time = _truncate_time_to_sec(max(df['timestamp']))
            
            _, axes = plt.subplots(nrows=2, ncols=1, figsize=(8,10))
            df_proc_cpu = pd.DataFrame()
            df_proc_mem = pd.DataFrame()
            process_titles = df['title'].unique()
            # print(process_titles)
            for proc in process_titles:
                
                if not any(p in proc for p in FOCUSSED_PROCESS_TAGS) or any(p in proc for p in ['about: blank','chrome', 'New Tab']):
                    continue
                
                try:                                               
                    df_proc_filtered = df[df['title']==proc]            
                    df_proc_filtered = df_proc_filtered.drop(columns=['title'])
                    df_proc_filtered['timestamp'] = [_truncate_time_to_sec(t) for t in df_proc_filtered['timestamp']]
                    df_proc_filtered = df_proc_filtered.groupby('timestamp').max()
                    df_proc_filtered = df_proc_filtered.reset_index()
                    df_proc_filtered = df_proc_filtered.drop_duplicates()     
                    
                    att = df_proc_filtered.set_index('timestamp')                
                    att = att.astype('float')            
                    idx = pd.date_range(min_time, max_time, freq='S')
                    date_reidx = att.reindex(idx)
                    if 'http' in proc and ':' in proc:
                        proc = proc.split(':')[0] + ' : ' + (proc.split(':')[2]).split('/')[2]
                    cpu_name = 'CPU :: '+ proc
                    mem_name = 'Mem :: '+ proc
                    date_reidx[cpu_name] = date_reidx['cpu']
                    date_reidx[mem_name] = date_reidx['memory']
                    if len(df_proc_cpu)==0:
                        df_proc_cpu = pd.DataFrame(date_reidx[cpu_name].copy())   
                        df_proc_mem = pd.DataFrame(date_reidx[mem_name].copy()) 
                    else:
                        df_proc_cpu[cpu_name] = pd.DataFrame(date_reidx[cpu_name].copy())   
                        df_proc_mem[mem_name] = pd.DataFrame(date_reidx[mem_name].copy()) 
                except Exception as e:
                    print(e)
                    continue
            # df_proc_cpu.to_csv('proc_cpu.csv')
            # df_proc_mem.to_csv('proc_mem_csv')
            
            
            
            box = axes[0].get_position()
            print(box)
            # axes[0].set_position([box.x0,0.45,box.width,box.height*0.90])
            df_proc_cpu.plot(ax=axes[0], kind='line', title = 'CPU Usage', 
                        legend=True).legend(loc='upper center',
                        #  bbox_to_anchor=(0.02,1.5),
                        ncol=2,prop={'size':6})
            
            box = axes[1].get_position()
            print(box)
            # axes[1].set_position([box.x0,box.y0,box.width,box.height*0.80])
            df_proc_mem.plot(ax=axes[1], kind='line', title = 'Memory Usage', 
                            legend=True).legend(loc= 'upper center', 
                            # bbox_to_anchor=(0.02,1.5),
                            ncol=2,prop={'size':6})
            
            # plt.legend( bbox_to_anchor=(0,2,1,100),mode='expand')
            
            # plt.show()   
            plt.tight_layout() 
            plt.savefig('./plots/'+id+'_proc_usage.pdf')          
            return  min_time,max_time
        except Exception as e:
            return None
    return None                     
        
def draw_sw_graph(id):
    global G
    global sw_events_info

    G.add_node(0, label='SessionStart')
    node_info = {}
    start_nodes = [(0,datetime.now(),0)]

    def find_proc_nodes(curr_proc_id):
        proc_start_nodes_idx= []
        for i, st_node in enumerate(start_nodes):
            prev_proc_id = st_node[2] 
            if curr_proc_id == prev_proc_id:
                proc_start_nodes_idx.append(i)
        
        if len(proc_start_nodes_idx)>0:
            return proc_start_nodes_idx
        return [0]

    def find_st_node(curr_proc_id, label):
        proc_start_nodes_idx= find_proc_nodes(curr_proc_id)
        for ind in proc_start_nodes_idx[::-1]:
            st_node_id = start_nodes[ind][0]
            prev_node = G.get_node(st_node_id)
            if label == START_END_EVENT_MAPS.get(prev_node.attr['label']) : 
                return ind, True         
        return proc_start_nodes_idx[-1],False  
            
    def log_sw_events( entries,timestamp):
        if 'service_worker_url' in entries or ('func_name' in entries and entries['func_name'] in ['registerServiceWorker', 'InitializeOnWorkerThread','Fetch' ] ):
            sw_info = {
                        'timestamp'  : timestamp,
                        'sw_url'     : entries['service_worker_url'] if 'service_worker_url' in entries else entries['request_url'], 
                        'request_url': entries['request_url'] if 'request_url' in entries else '',
                        'event_name' : entries['func_name']                                     
            }            
            sw_events_info.append(sw_info)                    
            dbo.update_sw_events_info_table(CONTAINER_ID, sw_info)

        if 'func_name' in entries and entries['func_name'] in ['showNotification','DispatchNotificationCloseEvent']:
            notification_obj = {
                'notification_title': entries['notification_title'],
                'notification_body': entries['notification_body'],
                'notification_tag': entries['notification_tag'],
                'notification_image': entries['notification_image'],
                'notification_icon': entries['notification_icon'],
                'notification_badge': entries['notification_badge'],
                'sw_url' : entries['context_url'],
                'timestamp' : timestamp,
                'event' : entries['func_name']
            }
            dbo.insert_notification(CONTAINER_ID, notification_obj)


    try:
        
        while( node_info !=None):
            try:
                node_info = get_next_node_info()
                
                if node_info == None:
                    break
                node_id,timestamp, proc_id, entries = node_info
                
                if node_id == -1:
                    continue
                node = G.get_node(node_id)
                label = node.attr['label']
                
                is_edge =True
                prev_node_idx,is_end_node = find_st_node(proc_id,label)
                prev_node_id = start_nodes[prev_node_idx][0] 

                log_sw_events(entries,timestamp)

                if  label in START_END_EVENT_MAPS:
                    start_nodes.append((node_id,timestamp,proc_id))  
                                
                elif is_end_node:       
                    st_node_id, st_timestamp, st_proc_id = start_nodes.pop(prev_node_idx)
                    st_node = G.get_node(st_node_id) 
                    
                    ### this eliminates recording null event
                    if (timestamp-st_timestamp).total_seconds() >2:
                        node_info = {'st_label': st_node.attr['label'], 'end_label': label, 'st_node_id': str(st_node_id), 'st_timestamp': st_timestamp, 'end_timestamp': timestamp, 'process_id': proc_id }
                        dbo.update_sw_event_duration_table(CONTAINER_ID, node_info)

                    st_node.attr['label'] = st_node.attr['label'] + ' (' +str((timestamp-st_timestamp).total_seconds()) + ')'
                    G.remove_node(node_id)
                    is_edge=False
                
                if is_edge:
                    G.add_edge(prev_node_id, node_id)
                    
            except Exception as e:
                print(e)
                continue
        

        for item in start_nodes:
            st_node_id, st_timestamp, st_proc_id = item
            st_node = G.get_node(st_node_id) 
            node_info = {'label': st_node.attr['label'], 'st_node_id': str(st_node_id), 'timestamp': st_timestamp, 'process_id': st_proc_id }
            dbo.update_sw_event_duration_table(CONTAINER_ID, node_info)

        

        s = G.to_string()
        with open('./dot_graphs/'+id+'.txt', 'w') as f:
            f.write(s) 

        # G.layout("dot")  # layout with dot
        # G.draw('./plots/'+id+"_sw_flow_graph.png")
        
    except Exception as e:
        print(e) 
    
    
def plot_sw_events(plt_det, id):
    global sw_events_info
    print(sw_events_info)
    print(plt_det)
    if plt_det==None:
        return
    min_time,max_time = plt_det
    plt.clf()
    _, axes = plt.subplots(nrows=2, ncols=1, figsize=(8,10))
    
    df_events = pd.DataFrame(sw_events_info)    

    
    if df_events.empty:
        return
    sw_urls = df_events['sw_url'].unique()
    
    y_point = 10
    colors = ['b', 'g','r','c','y']
    for sw_url in sw_urls:        
        try:                                               
            df_events_filtered = df_events[df_events['sw_url']==sw_url]
            df_events_filtered = df_events_filtered.drop(columns=['sw_url'])
            df_events_filtered['timestamp'] = [_truncate_time_to_min(t) for t in df_events_filtered['timestamp']]
            df_events_filtered = df_events_filtered.groupby('timestamp')['event_name'].apply(lambda ev : '\n'.join(set(ev)))
            df_events_filtered = df_events_filtered.reset_index()
            df_events_filtered = df_events_filtered.drop_duplicates()     
            print(df_events_filtered.head())
            min_time = _truncate_time_to_min(min_time)
            max_time = _truncate_time_to_min(max_time)
              
            att = df_events_filtered.set_index('timestamp')      
            print(att.head(n=20))     
            idx = pd.date_range(min_time, max_time, freq='min')
            date_reidx = att.reindex(idx)            
            date_reidx = date_reidx.reset_index()            
            date_reidx['y'] = date_reidx['event_name'].apply(lambda x: y_point if len(str(x))>3 else -1) 
            y_point += 10
            print(date_reidx)
            # date_reidx.to_csv('plot.csv')

            fig = date_reidx.plot('index','y' , ax=axes[0], kind='line', style='.', color = colors.pop(0),
                legend=True).legend(loc= 'upper center', 
                # bbox_to_anchor=(0.02,1.5),
                prop={'size':4})
            

            for i,row in date_reidx.iterrows():
                # break
                if row['y']>0:
                    axes[0].annotate(xy=(row['index'], row['y']), s=row['event_name'], ha='left', rotation=0, position=(row['index'],row['y']))


        
        except Exception as e:
            print(e)
            continue
            
    axes[0].set_ylim(0, y_point)
    # plt.tight_layout() 
    plt.savefig('./plots/'+id+'_sw_events.pdf')
    # plt.show()
            
    

if __name__ == "__main__":
    import tarfile
    import os
    test = False
    
    sw_events_info = []
    CONTAINER_ID = ''
    if test:
        process_task_usage = {
                        'title':[],
                        'cpu':[],
                        'memory':[],
                        'timestamp':[]
                }
        id = 'miner_demo2'
        log_tar_dir = '../../attack_demo2_miner2.tar'
        t = tarfile.open(log_tar_dir,'r')
        LOG_FILE = t.extractfile('attack_demo2_miner2.log') 
        G = pgv.AGraph(directed=True, strict=True, ranksep='1',node_sep='2')
        draw_sw_graph(id)
        plt_det = plot_task_usage(id)
        plot_sw_events(plt_det)
        plt.tight_layout() 
        plt.savefig('./plots/'+id+'_proc_usage.pdf')
        exit()

    
    log_dir_path = '../SWSec_Crawler/sw_sec_containers_data/' 
    # dbo.log_db =False
    for dir in os.listdir(log_dir_path):
        log_path = os.path.join(log_dir_path,dir)  
        if 'Ana_' not in dir:# or '3102' not in dir:
            continue      
        for tar_file in os.listdir(log_path):
            try:
                if 'chrome_log' in tar_file :
                    print(dir)
                    process_task_usage = {
                            'title':[],
                            'cpu':[],
                            'memory':[],
                            'timestamp':[]
                    }
                    id = "{}_{}".format(dir.replace('container_',''),tar_file.replace('chrome_log_','')) 
                    id = id.replace('.tar','')
                    CONTAINER_ID = id

                    if os.path.exists('./dot_graphs/'+id+'.txt'):
                        continue

                    print(dir)
                    log_tar_dir = os.path.join(log_path,tar_file)
                    t = tarfile.open(log_tar_dir,'r')
                    LOG_FILE = t.extractfile('chrome_debug.log') 
                                  
                     
                    G = pgv.AGraph(directed=True, strict=True, ranksep='1',node_sep='2')

                    ### records sw events details in db and draws dot graph
                    draw_sw_graph(id)
                    
                    ### uncomment if plots needs to be drawn
                    
                    #plt_det = plot_task_usage(id)                   
                    #plot_sw_events(plt_det, id)
                    
                    # exit()
            except Exception as e:
                continue
                    
    
