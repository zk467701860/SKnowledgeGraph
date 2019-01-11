import threading
from Queue import Queue

from py2neo import Node

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.accessor.graph_client_for_rwr import RandomWalkGraphAccessor
from skgraph.graph.operation.generateDataPpi import DataCreateUtil
from skgraph.graph.operation.random_walk_restart import Walker

log_file = open('log_single.txt', 'w')
input_file_name = 'data.ppi'
node_id = 53157
client_1 = DefaultGraphAccessor(GraphClient(server_number=1))
client_2 = DefaultGraphAccessor(GraphClient(server_number=2))
data_util = DataCreateUtil(client_1)
end_status = 0


class Producer(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.data = queue

    def run(self):
        print 'begin produce'
        log_file.writelines('begin  %d\n' % (node_id))
        log_file.flush()
        if client_1.find_node_by_id(node_id) == None:
            return 0
        if data_util.createData(node_id) == 1:
            log_file.writelines('generate ppi end\n')
            log_file.flush()
            walker = Walker(input_file_name, client_2)
            walker.run_exp(node_id, 0.15, log_file, self.data)
            # print self.data.qsize()
        else:
            node_1 = Node('Entity', link_id=node_id)
            client_2.merge(node_1)
            log_file.writelines('add node end\n')
            log_file.flush()
        print 'qsize len:  ' + str(self.data.qsize())
        global end_status
        end_status = 1
        print 'end produce'


class Consumer(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.data = queue

    def run(self):
        print 'begin consume'
        global end_status
        random_walk_similarity_list = []
        while end_status == 0:
            while self.data.qsize() > 0:
                # print 'qsize len:  ' + str(self.data.qsize())
                line = self.data.get()
                # print line
                split_line = line.rstrip().split('\t')
                '''
                node_1_call_node_2 = Relationship(Node('Entity',link_id=int(split_line[0])), 'connect', Node('Entity',link_id=int(split_line[1])))
                node_1_call_node_2['count'] = float(split_line[2])
                client_2.merge(node_1_call_node_2)
                '''
                if len(random_walk_similarity_list) < 2000:
                    content = {}
                    content['start_link_id'] = int(split_line[0])
                    content['end_link_id'] = int(split_line[1])
                    print 'end 0 :     %s' % (split_line[1])
                    content['count'] = float(split_line[2])
                    random_walk_similarity_list.append(content)
                else:
                    RandomWalkGraphAccessor(client_2).create_random_walk_similarity_by_transaction(
                        random_walk_similarity_list)
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
            if len(random_walk_similarity_list) < 3000:
                content = {}
                content['start_link_id'] = int(split_line[0])
                content['end_link_id'] = int(split_line[1])
                content['count'] = float(split_line[2])
                print 'end 1 :     %s' % (split_line[1])
                random_walk_similarity_list.append(content)
            else:
                RandomWalkGraphAccessor(client_2).create_random_walk_similarity_by_transaction(
                    random_walk_similarity_list)
                random_walk_similarity_list = []
        print len(random_walk_similarity_list)
        print random_walk_similarity_list
        if len(random_walk_similarity_list) > 0:
            RandomWalkGraphAccessor(client_2).create_random_walk_similarity_by_transaction(random_walk_similarity_list)
        print 'end consume'


if __name__ == '__main__':
    queue = Queue()
    producer = Producer(queue)
    consumer = Consumer(queue)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()

    print 'All threads terminate!'
