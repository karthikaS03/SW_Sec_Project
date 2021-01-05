import psycopg2
import sys

from config import *

# Connect to database
try:
    conn = psycopg2.connect("dbname=%s host=%s user=%s password=%s"
                            % (db_name, db_host, db_user, db_password))
    
except Exception as e:
    print ("Unable to connect to database: " + db_name)
    print(e)
    sys.exit()


print ("Successfully connected!")
cursor = conn.cursor()

def create_tables():
   
    '''
    Table :: sw_events_info

    sw_event_id
    container_id
    ev_timetsamp
    sw_url
    event_name      

    '''
    cursor.execute("""
            CREATE TABLE sw_events_info
                    (
                        sw_event_id SERIAL, PRIMARY KEY(sw_event_id),
                        container_id TEXT, sw_url TEXT,
                        ev_timetsamp TIMESTAMP, event_name VARCHAR(512)
                    )
                """)

    '''
    Table :: process_task_usage 

    process_id
    container_id
    process_title
    cpu_usage
    mem_usage
    ev_timestamp
    '''

    cursor.execute("""
            CREATE TABLE process_task_usage
                    (
                        process_id SERIAL, PRIMARY KEY(process_id),
                        container_id TEXT, process_title TEXT,
                        ev_timetsamp TIMESTAMP, cpu_usage DECIMAL, mem_usage DECIMAL
                    )
            """)
    '''
    Table :: sw_event_duration

    id
    container_id
    process_id
    node_id
    st_time
    end_time
    st_label
    end_label
                        
    '''
    cursor.execute("""
            CREATE TABLE sw_event_duration
                    (
                        id SERIAL, PRIMARY KEY(id),
                        container_id TEXT, process_id INT,  node_id TEXT,
                        st_time TIMESTAMP, end_time TIMESTAMP,
                        st_label TEXT, end_label TEXT
                    )
            """)

    '''
    Table :: alexa_sites

    site_id
    site_url
    domain
    rank
    is_crawled
    is_sw_found
    is_analyzed
    has_notification_request
                        
    '''
    cursor.execute("""
            CREATE TABLE alexa_sites
                    (
                        site_id SERIAL, PRIMARY KEY(site_id),
                        site_url TEXT UNIQUE ,domain TEXT UNIQUE , rank INT,  is_crawled BOOLEAN ,
                        is_sw_found BOOLEAN , ia_analyzed BOOLEAN ,
                        has_notification_request BOOLEAN 
                    )
            """)
'''
Table :: container_output_logs

log_id
container_id
iteration
event_time
event        
'''
cursor.execute("""
        CREATE TABLE container_output_logs
                (
                    log_id SERIAL, PRIMARY KEY(log_id),
                    container_id TEXT ,
                    iteration INT,
                    event_time TIMESTAMP , 
                    event TEXT 
                )
        """)

conn.commit()

cursor.close()
conn.close()
