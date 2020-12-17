import psycopg2
from datetime import datetime

from .config import *

import sys


class DBOperator:
    def __init__(self,):
        # Connect to database
        try:
            self.conn = psycopg2.connect("dbname=%s host=%s user=%s password=%s"
                                         % (db_name, db_host, db_user, db_password))
        except Exception as e:
            print ("Unable to connect to database: " + db_name)
            print(e)
            sys.exit()
        self.cursor = self.conn.cursor()
        self.conn.set_session(autocommit=True)

    def bye(self,):
        self.cursor.close()
        self.conn.close()

    def update_sw_events_info_table(self, container_id, sw_event_info):
        try:
            self.cursor.execute(
                """
                INSERT INTO sw_events_info (container_id, sw_url, ev_timestamp, event_name
                                    )
                VALUES (%s, %s, %s, %s)""",
                (container_id, sw_event_info['sw_url'], sw_event_info['timestamp'], sw_event_info['event_name']))
        except Exception as e:
            print('ERROR :: Database ', e)

    def update_process_task_usage_table(self, container_id, task_usage_info):
       
        try:
            self.cursor.execute(
            """
            INSERT INTO process_task_usage (container_id, process_title, cpu_usage, mem_usage,
                                            ev_timestamp)
            VALUES (%s, %s, %s, %s, %s)""",
            (container_id, task_usage_info['title'],task_usage_info['cpu'], task_usage_info['memory'], task_usage_info['timestamp']))
        except Exception as e:
            print('ERROR :: Database ', e)


    def update_sw_event_duration_table(self, container_id, node_info):
        try:
            self.cursor.execute("""
            SELECT * FROM sw_event_duration WHERE container_id = %s AND
            node_id = %s AND process_id = %s
            """, (container_id, node_info['st_node_id'], node_info['process_id']))
            if self.cursor.rowcount == 0:
                self.cursor.execute(
                    """
                    INSERT INTO sw_event_duration (container_id, process_id,
                                    node_id, st_time, st_label)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (container_id, node_info['process_id'], node_info['st_node_id'], node_info['timestamp'],
                    node_info['label']))
            else:
                self.cursor.execute("""
                    UPDATE sw_event_duration SET end_label = %s , end_time = %s
                    WHERE container_id = %s AND node_id = %s AND process_id = %s
                    """, (node_info['label'], node_info['timestamp'] ,container_id, node_info['st_node_id'], node_info['process_id']))
        except Exception as e:
            print('ERROR :: Database ', e)


    def insert_notification(self, notification_obj):
        try:
            self.cursor.execute(
                    """
                    INSERT INTO notification_details_latest (sw_url_id,notification_title, notification_body,notification_count, target_url, image_url, sw_url, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (notification_obj['log_id'],
                    notification_obj['push_notification_title'] , 
                    notification_obj['push_notification_body'] , 
                    notification_obj['notification_count'] , 
                    notification_obj['push_notification_target_url'] , 
                    notification_obj['push_notification_image'] , 
                    notification_obj['frame_url'],
                    notification_obj['timestamp'] ))
            if self.cursor.rowcount == 1:
                return True
        except Exception as e:
            print(e)
            return False
        return False


    def insert_request(self, req_obj):
        try:
            self.cursor.execute(
                    """
                    INSERT INTO page_requests(sw_url_id,frame_url,local_url,request_url,timestamp)
                    VALUES (%s, %s, %s, %s,%s)""",
                    (req_obj['log_id'],
                    req_obj['frame_url'], 
                    req_obj['local_frame_root_url'], 
                    req_obj['url'],                     
                    req_obj['timestamp'] ))
            if self.cursor.rowcount == 1:
                return True
        except Exception as e:
            print(e)
            return False
        return False



def test():
    dbo = DBOperator()
   

if __name__ == "__main__":
    test()