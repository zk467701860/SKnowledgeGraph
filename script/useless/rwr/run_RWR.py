from py2neo import Node

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.operation.generateDataPpi import DataCreateUtil
from skgraph.graph.operation.random_walk_restart import Walker

log_file = open('log.txt', 'w')
input_file_name = 'data.ppi'
max_id = 1665370
client_1 = DefaultGraphAccessor(GraphClient(server_number=1))
client_2 = DefaultGraphAccessor(GraphClient(server_number=2))
data_util = DataCreateUtil(client_1)
for id in range(23, max_id + 1):
    log_file.writelines('begin  %d\n' % (id))
    if data_util.createData(id) == 1:
        log_file.writelines('generate ppi end\n')
        walker = Walker(input_file_name, client_2)
        walker.run_exp(id, 0.15, log_file)
        log_file.flush()
    else:
        node_1 = Node(link_id=id)
        client_2.merge(node_1)
        log_file.writelines('add node end\n')
        log_file.flush()
log_file.close()
