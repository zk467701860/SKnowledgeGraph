import threading
import time
from Queue import Queue

import MySQLdb

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.operation.generateDataPpi import DataCreateUtil
from skgraph.graph.operation.random_walk_restart import Walker

log_file = open('log.txt', 'w')
exception_file = open('exception.txt', 'w')
input_file_name = 'data.ppi'
begin_id = 60103
client_1 = DefaultGraphAccessor(GraphClient(server_number=1))
data_util = DataCreateUtil(client_1)
max_id = client_1.get_max_id_for_node()
end_status = 0


class Producer(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.data = queue

    def run(self):
        print 'begin produce'
        print 'max id:  %d' % (max_id)
        total_count = 0
        for id in range(begin_id, max_id + 1):
            if id <= 92354 or id > 243569:
                log_file.writelines('begin  %d\n' % (id))
                log_file.flush()
                if client_1.find_node_by_id(id) == None:
                    continue
                if data_util.createData(id) == 1:
                    log_file.writelines('generate ppi end\n')
                    log_file.flush()
                    try:
                        walker = Walker(input_file_name)
                    except Exception, error:
                        exception_text = str(id) + ' construct edge graph fail\n'
                        exception_file.writelines(exception_text)
                        exception_file.flush()
                        continue
                    total_count += walker.run_exp(id, 0.15, log_file, self.data)
                    print 'total count:   %d' % (total_count)
                    print 'qsize len:  ' + str(self.data.qsize())
        log_file.close()
        global end_status
        end_status = 1
        print 'end produce'


class Consumer(threading.Thread):
    def __init__(self, queue, transaction_number):
        threading.Thread.__init__(self)
        self.data = queue
        self.transaction_number = transaction_number

    def run(self):
        global end_status
        random_walk_similarity_list = []
        try:
            # conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', port=3306, db='graphApplication', charset='utf8')
            conn = MySQLdb.connect(host='10.141.221.75', user='root', passwd='root', port=3306, db='graphApplication',
                                   charset='utf8')
            cur = conn.cursor()
        except MySQLdb.Error, e:
            print "Mysql connection Error %d: %s" % (e.args[0], e.args[1])
        while end_status == 0:
            while self.data.qsize() > 0:
                line = self.data.get()
                split_line = line.rstrip().split('\t')
                content = (int(split_line[0]), int(split_line[1]), float(split_line[2]))
                random_walk_similarity_list.append(content)
                if len(random_walk_similarity_list) >= self.transaction_number:
                    try:
                        print 'begin process   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        self.insert_list_to_mysql(conn, cur, random_walk_similarity_list)
                        print 'end process   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        print 'between ' + str(random_walk_similarity_list[0][0]) + ' and ' + str(
                            random_walk_similarity_list[self.transaction_number - 1][0]) + '\n'
                    except Exception, error:
                        exception_text = 'between ' + str(random_walk_similarity_list[0][0]) + ' and ' + str(
                            random_walk_similarity_list[self.transaction_number - 1][0]) + '\n'
                        exception_file.writelines(exception_text)
                        exception_file.flush()
                        time.sleep(2)
                    random_walk_similarity_list = []
        print 'out produce loop'
        while self.data.qsize() > 0:
            line = self.data.get()
            split_line = line.rstrip().split('\t')
            content = (int(split_line[0]), int(split_line[1]), float(split_line[2]))
            random_walk_similarity_list.append(content)
            if len(random_walk_similarity_list) >= self.transaction_number:
                try:
                    print 'begin process   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    self.insert_list_to_mysql(conn, cur, random_walk_similarity_list)
                    print 'end process   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    print 'between ' + str(random_walk_similarity_list[0][0]) + ' and ' + str(
                        random_walk_similarity_list[self.transaction_number - 1][0]) + '\n'
                except Exception, error:
                    exception_text = 'between ' + str(random_walk_similarity_list[0][0]) + ' and ' + str(
                        random_walk_similarity_list[self.transaction_number - 1][0]) + '\n'
                    exception_file.writelines(exception_text)
                    exception_file.flush()
                    time.sleep(2)
                random_walk_similarity_list = []
        if len(random_walk_similarity_list) > 0:
            try:
                print 'begin process   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                self.insert_list_to_mysql(conn, cur, random_walk_similarity_list)
                print 'end process   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                print 'between ' + str(random_walk_similarity_list[0][0]) + ' and ' + str(
                    random_walk_similarity_list[len(random_walk_similarity_list) - 1][0]) + '\n'
            except Exception, error:
                exception_text = 'between ' + str(random_walk_similarity_list[0][0]) + ' and ' + str(
                    random_walk_similarity_list[len(random_walk_similarity_list) - 1][0]) + '\n'
                exception_file.writelines(exception_text)
                exception_file.flush()
                time.sleep(2)
        cur.close()
        conn.close()
        print 'end consume'

    def insert_list_to_mysql(self, conn, cursor, list):
        sql = 'insert into randomWalkCount(startID,endID,count) values(%s,%s,%s)'
        try:
            cursor.executemany(sql, list)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print('MySQL: %s   error:%s' % (sql, e))


if __name__ == '__main__':
    queue = Queue()
    producer = Producer(queue)
    consumer = Consumer(queue, 30000)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()

    print 'All threads terminate!'
