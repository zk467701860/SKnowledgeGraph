import threading
import time
from Queue import Queue

from py2neo import Node

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.accessor.graph_client_for_rwr import RandomWalkGraphAccessor
from skgraph.graph.operation.generateDataPpi import DataCreateUtil
from skgraph.graph.operation.random_walk_restart import Walker

log_file = open('log.txt', 'w')
exception_file = open('exception.txt', 'a+')
input_file_name = 'data.ppi'
begin_id = 92354
client_1 = DefaultGraphAccessor(GraphClient(server_number=1))
client_2 = DefaultGraphAccessor(GraphClient(server_number=2))
data_util = DataCreateUtil(client_1)
max_id = client_1.get_max_id_for_node()
end_status = 0
print_status = 0


class Producer(threading.Thread):
    def __init__(self, queue, queue_length):
        threading.Thread.__init__(self)
        self.data = queue
        self.queue_length = queue_length

    def run(self):
        print 'begin produce'
        print 'max id:  %d' % (max_id)
        global print_status
        total_count = 0
        for id in range(begin_id, max_id + 1):
            log_file.writelines('begin  %d\n' % (id))
            log_file.flush()
            if client_1.find_node_by_id(id) == None:
                continue
            if data_util.createData(id) == 1:
                log_file.writelines('generate ppi end\n')
                log_file.flush()
                walker = Walker(input_file_name, client_2)
                total_count += walker.run_exp(id, 0.15, log_file, self.data)
                print 'total count:   %d' % (total_count)
            else:
                node_1 = Node('Entity', link_id=id)
                client_2.merge(node_1)
                log_file.writelines('add node end\n')
                log_file.flush()
            if self.data.qsize() >= self.queue_length and print_status == 1:
                print 'produce full   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            while self.data.qsize() >= self.queue_length:
                pass
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
        global print_status
        random_walk_similarity_list = []
        while end_status == 0:
            while self.data.qsize() > 0:
                line = self.data.get()
                split_line = line.rstrip().split('\t')
                content = {}
                content['start_link_id'] = int(split_line[0])
                content['end_link_id'] = int(split_line[1])
                content['count'] = float(split_line[2])
                random_walk_similarity_list.append(content)
                if len(random_walk_similarity_list) >= self.transaction_number:
                    try:
                        print_status = 1
                        print 'begin process   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        RandomWalkGraphAccessor(client_2).create_random_walk_similarity_by_transaction(random_walk_similarity_list)
                        print 'end process   ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        print 'between ' + str(
                            random_walk_similarity_list[0]['start_link_id']) + ' and ' + str(
                            random_walk_similarity_list[self.transaction_number - 1]['start_link_id']) + '\n'
                        print_status = 0
                    except Exception, error:
                        exception_text = 'between ' + str(
                            random_walk_similarity_list[0]['start_link_id']) + ' and ' + str(
                            random_walk_similarity_list[self.transaction_number - 1]['start_link_id']) + '\n'
                        log_file.writelines(exception_text)
                        time.sleep(3)
                    random_walk_similarity_list = []
        print 'out produce loop'
        while self.data.qsize() > 0:
            line = self.data.get()
            # print line
            split_line = line.rstrip().split('\t')
            '''
            node_1_call_node_2 = Relationship(Node('Entity',link_id=int(split_line[0])), 'connect', Node('Entity',link_id=int(split_line[1])))
            node_1_call_node_2['count'] = float(split_line[2])
            client_2.merge(node_1_call_node_2)
            '''
            content = {}
            content['start_link_id'] = int(split_line[0])
            content['end_link_id'] = int(split_line[1])
            content['count'] = float(split_line[2])
            random_walk_similarity_list.append(content)
            if len(random_walk_similarity_list) >= self.transaction_number:
                try:
                    print 'begin process'
                    RandomWalkGraphAccessor(client_2).create_random_walk_similarity_by_transaction(
                        random_walk_similarity_list)
                    print 'end process'
                except Exception, error:
                    exception_text = 'between ' + str(random_walk_similarity_list[0]['start_link_id']) + ' and ' + str(
                        random_walk_similarity_list[self.transaction_number - 1]['start_link_id']) + '\n'
                    log_file.writelines(exception_text)
                    time.sleep(3)
                random_walk_similarity_list = []
        if len(random_walk_similarity_list) > 0:
            try:
                print 'begin process'
                RandomWalkGraphAccessor(client_2).create_random_walk_similarity_by_transaction(
                    random_walk_similarity_list)
                print 'end process'
            except Exception, error:
                exception_text = 'between ' + str(random_walk_similarity_list[0]['start_link_id']) + ' and ' + str(
                    random_walk_similarity_list[self.transaction_number - 1]['start_link_id']) + '\n'
                log_file.writelines(exception_text)
                time.sleep(3)
        print 'end consume'


if __name__ == '__main__':
    queue = Queue()
    producer = Producer(queue, 80000)
    consumer = Consumer(queue, 70000)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()

    print 'All threads terminate!'
