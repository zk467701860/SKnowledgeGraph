import threading
import time
from Queue import Queue

from py2neo import Node

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.accessor.graph_client_for_rwr import RandomWalkGraphAccessor
from skgraph.graph.operation.generateDataPpi import DataCreateUtil
from skgraph.graph.operation.random_walk_restart import Walker

log_file = open('log.txt', 'w')
input_file_name = 'data.ppi'
begin_id = 57645
client_1 = DefaultGraphAccessor(GraphClient(server_number=1))
client_2 = DefaultGraphAccessor(GraphClient(server_number=2))
data_util = DataCreateUtil(client_1)

max_id = client_1.get_max_id_for_node()
end_status = 0


class Producer(threading.Thread):
    def __init__(self, queue, queue_length):
        threading.Thread.__init__(self)
        self.data = queue
        self.queue_length = queue_length

    def run(self):
        print 'begin produce'
        print 'max id:  %d' % (max_id)
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
            while self.data.qsize() > self.queue_length:
                pass
            print 'qsize len:  ' + str(self.data.qsize())
        log_file.close()
        global end_status
        end_status = 1
        print 'end produce'


class Consumer(threading.Thread):
    def __init__(self, name, queue, transaction_number, cond):
        threading.Thread.__init__(self)
        self.name = name
        self.data = queue
        self.transaction_number = transaction_number
        self.cond = cond

    def run(self):
        print 'begin %s' % (self.name)
        global end_status
        random_walk_similarity_list = []
        if self.name == 'consumer_1':
            time.sleep(1)
        print '%s' % (self.name)
        self.cond.acquire()
        print '%s   acquire' % (self.name)
        if self.name != 'consumer_1':
            print "%s initial wait" % (self.name)
            self.cond.wait()
            print "%s initial wait end" % (self.name)
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
                    self.cond.notify()
                    print "%s begin insert" % (self.name)
                    self.cond.release()
                    print "%s  release" % (self.name)
                    try:
                        RandomWalkGraphAccessor(client_2).create_random_walk_similarity_by_transaction(random_walk_similarity_list)
                    except Exception, error:
                        print '%s  exception  between %d and %d' % (
                            self.name, random_walk_similarity_list[0]['start_link_id'],
                            random_walk_similarity_list[self.transaction_number - 1]['start_link_id'])
                        time.sleep(3)
                    random_walk_similarity_list = []
                    self.cond.acquire()
                    print '%s  acquire' % (self.name)
                    # if self.name == 'consumer_2':
                    # self.cond.wait()
                    # self.cond.wait()
                    # print "%s wait end" % (self.name)
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
                RandomWalkGraphAccessor(client_2).create_random_walk_similarity_by_transaction(
                    random_walk_similarity_list)
                random_walk_similarity_list = []
        if len(random_walk_similarity_list) > 0:
            RandomWalkGraphAccessor(client_2).create_random_walk_similarity_by_transaction(random_walk_similarity_list)
        self.cond.release()
        print 'end consume'


if __name__ == '__main__':
    queue = Queue()
    producer = Producer(queue, 60000)
    cond = threading.Condition()
    queue_process_length = 15000
    consumer_1 = Consumer('consumer_1', queue, queue_process_length, cond)
    consumer_2 = Consumer('consumer_2', queue, queue_process_length, cond)
    consumer_3 = Consumer('consumer_3', queue, queue_process_length, cond)
    producer.start()
    consumer_1.start()
    consumer_2.start()
    consumer_3.start()
    producer.join()
    consumer_1.join()
    consumer_2.join()
    consumer_3.join()

    print 'All threads terminate!'
