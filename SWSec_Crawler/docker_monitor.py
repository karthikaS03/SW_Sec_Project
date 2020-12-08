import docker
import os
import time
import datetime
from docker_config import *


client = docker.from_env(timeout=(3600*24))
export_path = CONFIG_EXPORT_PATH



    # logging.basicConfig(name = name , filename=name +'.log', filemode='w', ,level=logging.INFO)


def get_time():
	currentDT = datetime.datetime.now()
	return '['+currentDT.strftime("%Y-%m-%d %H:%M:%S") +'] '

def initiate_container(url, id, script_name, iteration_count,  container_timeout):	
    try:
        ## create and setup container ##
        get_logger('container_'+id, 1).info(get_time() + 'container_'+id+' creating!!')
        container_id  = client.containers.create(image=docker_image,name='container_'+id,volumes = vols,
                                                shm_size='1G', user=docker_user, 
                                                publish_all_ports=True, detach=False)
        container = client.containers.get('container_'+str(id))
        container.start()
        get_logger('container_'+id).info(get_time() + 'container_'+id+' created successfully!!')    
        
        ## wait for display to be activated ##
        time.sleep(10)
        ## Exeecute the browser automation script
        execute_script(url, id, script_name,  iteration_count, container_timeout-100)
    except Exception as e:
        # print(e)
        get_logger('container_'+id).info(e) 

def execute_script(url, id, script_name,  iteration_count, container_timeout):
    try:	
        ## Execute javascript file
        get_logger('container_'+id).info(get_time() +'container_'+id+': Executing javascript')
        container = client.containers.get('container_'+str(id))               
        #logs = container.attach(stream=True,stdout=True,stderr=True)
        _,logs = container.exec_run(cmd=['node',script_name,url,id,str(iteration_count),str(container_timeout)], user=docker_user, detach=False, stream=True)
               
        for log in logs:
            # print('Container_'+id+' :: LOG :: '+log)
            get_logger('container_'+id).info('Container_'+id+' :: LOG :: '+log)
        # print('timeout started')
        # time.sleep(container_timeout) 
        get_logger('container_'+id).info(get_time() +'container_'+id+': Execution complete!!')	
        export_container_logs(id,iteration_count)
    except Exception as e:
        get_logger('container_'+id).info('Exception ')
        get_logger('container_'+id).info(e)
        export_container_logs(id,iteration_count)

def stop_container(id):
    try:
        container = client.containers.get('container_'+str(id))
        if container:
            get_logger('container_'+id).info(get_time() + 'container_'+id+' stopping!!')
            container.pause()
            time.sleep(2)
            container.stop()
    except Exception as e:
        get_logger('container_'+id).info(e)

def remove_containers():
    while client.containers.list():		
        try:
            for c in client.containers.list():
                c.stop()
                c.remove()
        except Exception as e:
            print(e)
        
def resume_container(url, id, script_name, iteration_count, container_timeout):
    container = client.containers.get('container_'+str(id))
    if container:
        get_logger('container_'+id).info(get_time() + 'container_'+id+'_'+str(iteration_count)+' resuming!!')
        container.start()
        ## wait for display to be activated ##
        time.sleep(10)
        ##   Open a blank page on the browser and wait for notifications 
        execute_script(url,id, script_name, iteration_count, container_timeout-100)

def export_container_logs(id,count):
    try:
        print(export_path)
        container = client.containers.get('container_'+str(id))
        get_logger('container_'+id).info(get_time() + 'container_'+id+'exporting files!!')
        dir_path = export_path+'container_'+id+'/'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
        # with open(dir_path+'logs_'+str(count)+'.tar', 'w') as f:
        #     bits, stat = container.get_archive('/home/pptruser/logs/')
        #     for chunk in bits:
        #         f.write(chunk)

        with open(dir_path+'chrome_log_'+str(count)+'.tar', 'w') as f:
            bits, stat = container.get_archive('/home/pptruser/chromium/chrome_debug.log')
            for chunk in bits:
                f.write(chunk)

    except Exception as e:
        get_logger('container_'+id).info('Export Container:: Exception!!')
    
def sw_found_pwa(id, count):
    try:
        import tarfile
        log_tar_dir = export_path+'container_'+id+'/chrome_log_'+str(count)+'.tar'        
        t = tarfile.open(log_tar_dir,'r')
        chrome_log_file = 'chrome_debug.log'
        print(t.getnames())
        if 'chrome_debug.log' in t.getnames():
            f = t.extractfile(chrome_log_file)
            data = f.read()
            res = data.find('=registerServiceWorker')
            
            # res2 = data.find('=requestNotification')
            if res >-1:
                print('Found sw :: ', id)
                return True
        return False
    except Exception as e:
        return False

def sw_found_vv8(id,count):
    try:
        import tarfile
        log_tar_dir = export_path+id+'/logs_'+str(count)+'.tar'
        t = tarfile.open(log_tar_dir,'r')
        for log_name in t.getnames():
            # print(log_name)
            if 'ServiceWorker' in log_name and '.log' in log_name:
                print('Found SW :: ', id)
                return True
        return False
    except Exception as e:
        return False

def docker_prune():
    ## Remove containers that are unused  ##
    try:
        client.containers.prune()		
    except Exception as e:
        get_logger('container_'+id).info(e)


def test():
    '''
    remove_containers()
    initiate_container('https://evangelistjoshuaforum.com/','tes_100', 'capture_notifications.js','0', 330 )    
    count=0
    while count<2:
        stop_container('tes_100')
        export_container('tes_100',str(count-1))
        time.sleep(300)
        resume_container('https://evangelistjoshuaforum.com/','tes_100','capture_notifications.js',count,330)
        count=count+1
    '''
    #export_container('833','9')
    #get_logger('container_'+id).info(check_if_success('1786','0'))
    stop_container('tes_1000')
    docker_prune()
    initiate_container('https://feedbackchoice.com/','tes_1000', 'run_chromium.js','0', 1000 )   
    export_container_logs('tes0','0')
   
    
if __name__== "__main__":
    test()
