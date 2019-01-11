import sys

from script.graph_operation.graph_data_clean.awesome_item_rename_ambiguous import awesome_item_rename_ambiguous
from script.graph_operation.graph_data_clean.awesome_item_rename_duplicate import awesome_item_rename_duplicate
from script.graph_operation.graph_data_clean.merge_awesome_nodes_from_database import merge_awesome_nodes_from_database
from script.graph_operation.graph_data_clean.merge_awesome_nodes_from_file import merge_awesome_nodes_from_file
from skgraph.graph.accessor.graph_accessor import GraphClient
from skgraph.graph.accessor.graph_client_for_awesome import AwesomeGraphAccessor
from skgraph.graph.node_collection import NodeCollection

reload(sys)
sys.setdefaultencoding('utf8')

graph_client = GraphClient(server_number=1)
awesome_graph_accessor = AwesomeGraphAccessor(graph_client)
node_collection = NodeCollection(graph_client)

# step1
print "----------------------------------------------------------"
print "step1 begin: rename duplicate awesome items"
awesome_item_rename_duplicate(awesome_graph_accessor, node_collection)
# step2
print "----------------------------------------------------------"
print "step2 begin: merge awesome nodes from file"
merge_awesome_nodes_from_file(awesome_graph_accessor)
# step3
print "----------------------------------------------------------"
print "step3 begin: merge awesome nodes from database"
merge_awesome_nodes_from_database(awesome_graph_accessor,node_collection)
# step4
print "----------------------------------------------------------"
print "step4 begin: rename ambiguous awesome items"
awesome_item_rename_ambiguous(awesome_graph_accessor, node_collection)