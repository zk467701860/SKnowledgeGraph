# -*- coding:utf8 -*-

import random
import time

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor


class RandomWalk:
    max_id = 1665370

    def __init__(self, generationNumber, stepNumber):
        self.generationNumber = generationNumber
        self.stepNumber = stepNumber

    def walk(self):
        '''
        '''
        file = open('log1.txt', 'w')
        client = DefaultGraphAccessor()
        iterator = 0
        possibility_list = [0] * RandomWalk.max_id
        adjacent_node_list = [0] * RandomWalk.max_id
        file.writelines("begin:  " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\n')
        file.flush()
        while iterator < self.generationNumber:
            file.writelines("iteration:   " + str(iterator) + "   " + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                    time.localtime(time.time())) + '\n')
            file.flush()
            # print str(iterator) + "   " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            current_node_index = 1
            step_length_list = [0] * RandomWalk.max_id
            for i in range(0, self.stepNumber):
                if (current_node_index > 0 and current_node_index < 7520) or current_node_index > 7524:
                    if adjacent_node_list[current_node_index - 1] == 0:
                        adjacent_node = client.get_adjacent_node_id_list(current_node_index)
                        adjacent_node_list[current_node_index - 1] = adjacent_node
                    else:
                        adjacent_node = adjacent_node_list[current_node_index - 1]
                    next_node_index = adjacent_node[random.randint(0, len(adjacent_node) - 1)]
                    # print str(iterator) + "   " + str(i) + "   " + str(len(adjacent_node)) + "    " + str(
                    # next_node_index)
                    if (next_node_index > 1 and next_node_index < 7520) or next_node_index > 7524:
                        current_node_index = next_node_index
                    if step_length_list[next_node_index - 1] == 0 and next_node_index != 1:
                        step_length_list[next_node_index - 1] = i + 1
                        possibility_list[next_node_index - 1] += 1 - (
                        step_length_list[next_node_index - 1] / float(self.stepNumber))
            iterator += 1
        file.writelines("end:  " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '\n')
        file.flush()
        file.close()
        for i in range(0, RandomWalk.max_id):
            possibility_list[i] /= self.generationNumber
            if possibility_list[i] > 0:
                print str(i) + "  " + str(possibility_list[i])


if __name__ == '__main__':
    system = RandomWalk(100, 10000)
    system.walk()
