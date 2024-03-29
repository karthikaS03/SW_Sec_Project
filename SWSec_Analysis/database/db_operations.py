import psycopg2
from datetime import datetime
import sys
if sys.version_info > (2,8):
    from .config import *
else:
    from config import *

import sys
from datetime import datetime


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
        self.log_db = True

    def bye(self,):
        self.cursor.close()
        self.conn.close()

    def get_seed_urls(self,is_crawl, count=10):
        if not self.log_db:
            return
        if is_crawl:
            query = """
            SELECT rank, site_url FROM alexa_sites WHERE is_crawled is NULL  order by rank
            LIMIT %s
            """ %(count)
        else:
            query = """
            SELECT rank, site_url FROM alexa_sites WHERE is_crawled=True AND is_sw_found=True AND has_notification_request=True 
            AND is_analyzed is NULL order by rank LIMIT %s
            """ %(count)
            query = """
            SELECT rank, site_url FROM alexa_filtered_sites WHERE  is_analyzed = False and rank <5000 order by rank LIMIT %s
            """ %(count)
        self.cursor.execute(query)
        return [x for x in self.cursor.fetchall()]

    ### get sw_urls whose rank are unknown
    def get_sw_urls(self):
        if not self.log_db:
            return
        query = """
        SELECT distinct request_url FROM sw_events_info WHERE sw_url not in (select sw_url from sw_urls)
        """ 
        query = """select distinct request_url from sw_events_info where event_name LIKE 'openWindow%' """
        self.cursor.execute(query)
        return [x[0] for x in self.cursor.fetchall()]

    def update_sw_events_info_table(self, container_id, sw_event_info):
        if not self.log_db:
            return
        try:
            self.cursor.execute(
                """
                INSERT INTO sw_events_info (container_id, sw_url, ev_timestamp, event_name, request_url
                                    )
                VALUES (%s, %s, %s, %s, %s)""",
                (container_id, sw_event_info['sw_url'], sw_event_info['timestamp'], sw_event_info['event_name'], sw_event_info['request_url']))
        except Exception as e:
            print('ERROR :: Database ', e)

    def update_process_task_usage_table(self, container_id, task_usage_info):
        if not self.log_db:
            return
        try:
            self.cursor.execute(
            """
            INSERT INTO process_task_usage (container_id, process_title, cpu_usage, mem_usage,
                                            ev_timestamp)
            VALUES (%s, %s, %s, %s, %s)""",
            (container_id, task_usage_info['title'],task_usage_info['cpu'], task_usage_info['memory'], task_usage_info['timestamp']))
        except Exception as e:
            print('ERROR :: Database ', e)

    def insert_alexa_sites_table(self, site_url, site_rank):
        if not self.log_db:
            return
        try:
            self.cursor.execute(
            """
            INSERT INTO alexa_sites (site_url, rank)
            VALUES (%s, %s)""",
            (site_url, site_rank))
        except Exception as e:
            print('ERROR :: Database ', e)

    def update_alexa_sites_table(self, site_rank, site_url, column_name, column_val):
        if not self.log_db:
            return
        query= """ UPDATE alexa_filtered_sites SET """+ column_name +""" = """+ column_val
        try:
            if column_name == 'is_crawled':
                query = query + """, crawl_timestamp = '%s'""" % (datetime.now())
            elif column_name =='is_analyzed':
                query = query + """, analysis_timestamp = '%s'""" % (datetime.now())

            if site_rank == None:
                query = query + """ 
                        WHERE site_url LIKE '%"""+ site_url +"""%' """
            else:
                query = query + """ 
                        WHERE rank = %s """ % (site_rank)
            # print(query)
            self.cursor.execute(query)
            
        except Exception as e:
            print('ERROR :: Database ', e)

    def update_sw_event_duration_table(self, container_id, node_info):
        if not self.log_db:
            return
        try:
            if ('end_label' in node_info):
                self.cursor.execute("""
                        INSERT INTO sw_event_duration (container_id, process_id,
                                        node_id, st_time, end_time, st_label, end_label, sw_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s)""",
                        (container_id, node_info['process_id'], node_info['st_node_id'], node_info['st_timestamp'],node_info['end_timestamp'],
                        node_info['st_label'], node_info['end_label'], node_info['sw_url']))
            else:
                self.cursor.execute(
                    """
                    INSERT INTO sw_event_duration (container_id, process_id,
                                    node_id, st_time, st_label)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (container_id, node_info['process_id'], node_info['st_node_id'], node_info['timestamp'],
                    node_info['label']))

            # self.cursor.execute("""
            # SELECT * FROM sw_event_duration WHERE container_id = %s AND
            # node_id = %s AND process_id = %s
            # """, (container_id, node_info['st_node_id'], node_info['process_id']))
            # if self.cursor.rowcount == 0:
            #     self.cursor.execute(
            #         """
            #         INSERT INTO sw_event_duration (container_id, process_id,
            #                         node_id, st_time, st_label)
            #         VALUES (%s, %s, %s, %s, %s)""",
            #         (container_id, node_info['process_id'], node_info['st_node_id'], node_info['timestamp'],
            #         node_info['label']))
            # else:
            #     self.cursor.execute("""
            #         UPDATE sw_event_duration SET end_label = %s , end_time = %s
            #         WHERE container_id = %s AND node_id = %s AND process_id = %s
            #         """, (node_info['label'], node_info['timestamp'] ,container_id, node_info['st_node_id'], node_info['process_id']))
        except Exception as e:
            print('ERROR :: Database ', e)


    def insert_notification(self,container_id, notification_obj):
        if not self.log_db:
            return
        try:
            self.cursor.execute(
                    """
                    INSERT INTO notification_details (container_id, sw_url, notification_title, notification_body, 
                    notification_tag, image_url, icon_url, badge_url, timestamp, event)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (container_id,
                    notification_obj['sw_url'],
                    notification_obj['notification_title'] , 
                    notification_obj['notification_body'] , 
                    notification_obj['notification_tag'] , 
                    notification_obj['notification_image'] , 
                    notification_obj['notification_icon'] , 
                    notification_obj['notification_badge'] , 
                    notification_obj['timestamp'],
                    notification_obj['event'] ))
            if self.cursor.rowcount == 1:
                return True
        except Exception as e:
            print(e)
            return False
        return False

    def get_output_log_iteration(self, container_id):
        query = """SELECT MAX(iteration) FROM container_output_logs WHERE container_id ='%s'"""%(container_id)
        self.cursor.execute(query)
        res = self.cursor.fetchone()[0]
        if res is None:
            iteration = 0
        else:
            iteration = res + 1
        return iteration
        

    def insert_container_log(self, container_id, iteration,  ev_time, event):
        if not self.log_db:
            return
        try:
            
            self.cursor.execute(
                """
                INSERT INTO container_output_logs (container_id, iteration, event_time, event )
                VALUES (%s, %s, %s, %s)""",
                (container_id, iteration, ev_time, event))
        except Exception as e:
            print('ERROR :: Database ', e)

    def update_sw_url(self, sw_url, sw_sld_domain,  rank):
        if not self.log_db:
            return
        try:            
            self.cursor.execute(
                """
                INSERT INTO sw_urls(sw_url,sw_sld_domain,rank) VALUES(%s, %s, %s)""",
                ( sw_url,sw_sld_domain, rank))
        except Exception as e:
            print('ERROR :: Database ', e)

    def insert_request(self, req_obj):
        if not self.log_db:
            return
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
