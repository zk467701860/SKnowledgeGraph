"""
Implementation of tissue-specific graph walk with RWR

"""
import sys
import numpy as np
import networkx as nx
from sklearn.preprocessing import normalize

# from py2neo import Node,Relationship

# convergence criterion - when vector L1 norm drops below 10^(-6)
# (this is the same as the original RWR paper)
CONV_THRESHOLD = 0.000001


# possibility_file = open('possibility.txt', 'w')

class Walker:
    """ Class for multi-graph walk to convergence, using matrix computation
    Attributes:
    -----------
        og_matrix (np.array) : The column-normalized adjacency matrix
                               representing the original graph LCC, with no
                               nodes removed
        restart_prob (float) : The probability of restarting from the source
                               node for each step in run_path (i.e. r in the
                               original Kohler paper RWR formulation)
    """

    def __init__(self, original_ppi):
        self._build_matrices(original_ppi)

    def run_exp(self, source_id, restart_prob, log_file, queue):
        """ Run a multi-graph random walk experiment, and print results.

        Parameters:
        -----------
            source (list):        The source node indices (i.e. a list of Entrez
                                  gene IDs)
            restart_prob (float): As above
        """
        self.restart_prob = restart_prob

        # set up the starting probability vector
        p_0 = self._set_up_p0(source_id)
        diff_norm = 1
        # this needs to be a deep copy, since we're reusing p_0 later
        p_t = np.copy(p_0)
        log_file.writelines('begin calculate connect count\n')
        log_file.flush()
        while (diff_norm > CONV_THRESHOLD):
            # first, calculate p^(t + 1) from p^(t)
            p_t_1 = self._calculate_next_p(p_t, p_0)

            # calculate L1 norm of difference between p^(t + 1) and p^(t),
            # for checking the convergence condition
            diff_norm = np.linalg.norm(np.subtract(p_t_1, p_t), 1)

            # then, set p^(t) = p^(t + 1), and loop again if necessary
            # no deep copy necessary here, we're just renaming p
            p_t = p_t_1

        # now, generate and print a rank list from the final prob vector
        node_list = []
        possibility_list = []
        sum_possibility = 0
        log_file.writelines('push neo4j edge into queue\n')
        log_file.flush()
        """
        for node, prob in self._generate_rank_list(p_t):
            if int(node) != source_id:
                node_list.append(node)
                possibility_list.append(prob)
                sum_possibility += prob
        for i in range(0, len(node_list)):
            file.writelines('{}\t{}\t{:.10f}\n'.format(source_id, node_list[i], possibility_list[i] / sum_possibility))
            file.flush()
        """
        count = 0
        for node, prob in self._generate_rank_list(p_t):
            # possibility_file.writelines('{}\t{}\t{:.10f}\n'.format(source_id, node, prob))
            # possibility_file.flush()
            # file.writelines('{}\t{}\t{:.10f}\n'.format(source_id, node, prob))
            # file.flush()
            if int(node) != source_id:
                if prob == 0:
                    break
                temp_str = str(source_id) + '\t' + node + '\t' + str(prob)
                # print temp_str
                queue.put(temp_str)
                count += 1
                # node_1_call_node_2 = Relationship(Node(link_id=source_id), 'connect', Node(link_id=int(node)))
                # node_1_call_node_2['count'] = prob
                # self.client.merge(node_1_call_node_2)
        return count

    def _generate_rank_list(self, p_t):
        """ Return a rank list, generated from the final probability vector.
        Gene rank list is ordered from highest to lowest probability.
        """
        gene_probs = zip(self.OG.nodes(), p_t.tolist())
        # sort by probability (from largest to smallest), and generate a
        # sorted list of Entrez IDs
        for s in sorted(gene_probs, key=lambda x: x[1], reverse=True):
            yield s[0], s[1]

    def _calculate_next_p(self, p_t, p_0):
        """ Calculate the next probability vector. """
        # epsilon = np.squeeze(np.asarray(np.dot(self.og_matrix, p_t)))
        epsilon = np.squeeze(np.asarray(np.dot(p_t, self.og_matrix)))
        no_restart = epsilon * (1 - self.restart_prob)
        restart = p_0 * self.restart_prob
        return np.add(no_restart, restart)

    def _set_up_p0(self, source_id):
        """ Set up and return the 0th probability vector. """
        p_0 = [0] * self.OG.number_of_nodes()
        try:
            # matrix columns are in the same order as nodes in original nx
            # graph, so we can get the index of the source node from the OG
            source_index = list(self.OG.nodes()).index(str(source_id))
            p_0[source_index] = 1
        except ValueError:
            sys.exit("Source node %d is not in original graph.. Exiting." % (source_id))
        return np.array(p_0)

    def _build_matrices(self, original_ppi):
        """ Build column-normalized adjacency matrix for each graph.

        NOTE: these are column-normalized adjacency matrices (not nx
              graphs), used to compute each p-vector
        """
        original_graph = self._build_og(original_ppi)

        self.OG = original_graph
        og_not_normalized = nx.to_numpy_matrix(original_graph)
        self.og_matrix = self._normalize_cols(og_not_normalized)
        # print self.OG.nodes
        # print self.og_matrix

    def _build_og(self, original_ppi):
        """ Build the original graph, without any nodes removed. """

        try:
            graph_fp = open(original_ppi, 'r')
        except IOError:
            sys.exit("Could not open file: {}".format(original_ppi))

        G = nx.DiGraph()
        edge_list = []

        # parse network input
        for line in graph_fp.readlines():
            split_line = line.rstrip().split('\t')
            if len(split_line) > 3:
                # assume input graph is in the form of HIPPIE network
                edge_list.append((split_line[1], split_line[3],
                                  float(split_line[4])))
            elif len(split_line) < 3:
                # assume input graph is a simple edgelist without weights
                edge_list.append((split_line[0], split_line[1], float(1)))
            else:
                # assume input graph is a simple edgelist with weights
                edge_list.append((split_line[0], split_line[1],
                                  float(split_line[2])))

        G.add_weighted_edges_from(edge_list)
        graph_fp.close()

        return G

    def _normalize_cols(self, matrix):
        """ Normalize the columns of the adjacency matrix """
        return normalize(matrix, norm='l1', axis=0)
