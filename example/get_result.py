from py2neo import Graph
from skgraph.graph.accessor.factory import GraphFactory
import xlrd

class AnnotationStatistics:

    def __init__(self, graph=None):
        if isinstance(graph, Graph):
            self._graph = graph

        else:
            self._graph, _config = GraphFactory.create_from_default_config(server_number=4)

    @staticmethod
    def read_data_from_sheet(f_path):
        index_list = []
        with xlrd.open_workbook(f_path) as f:
            table = f.sheet_by_index(0)
        index = 1
        print("################################")
        for item in table.col_values(6, 1):
            print(item)
            if int(item) == 0:
                index_list.append(index)
            index += 1
        return table, index_list

    @staticmethod
    def compare_between_two_file(table1, table2):
        diff_list = []
        same_list = []
        col_num = table1.nrows
        for i in range(1, col_num):
            if table1.cell(i, 6).value != table2.cell(i, 6).value:
                diff_list.append(i)
            else:
                same_list.append(i)
        return diff_list, same_list

    @staticmethod
    def find_false_in_same_list(same_list, fail_list):
        new_list = []
        for index in same_list:
            if index in fail_list:
                new_list.append(index)
        return new_list

    def get_new_lines_from_list(self,table, new_list):
        lines = []
        for index in new_list:
            line = [str(int(table.cell(index, 0).value)), table.cell(index, 1).value, table.cell(index, 2).value,
                    table.cell(index, 3).value, str(int(table.cell(index, 4).value)), str(table.cell(index, 5).value)]
            print(line)
            query = "MATCH (s:`wikidata`) WHERE ID(s)={param} RETURN s.`site:enwiki` as url".format(
                        param=table.cell(index, 4).value
                    )
            record_data = self._graph.run(query).data()
            line.append(record_data[0]["url"])
            lines.append("#".join(line))
        return lines


if __name__ == "__main__":
    annotation = AnnotationStatistics()
    table1, index_list_1 = annotation.read_data_from_sheet("./data/data1.xlsx")
    print(index_list_1)
    table2, index_list_2 = annotation.read_data_from_sheet("./data/data2.xlsx")
    print(index_list_2)
    diff_list, same_list = annotation.compare_between_two_file(table1, table2)
    same_fail_list = annotation.find_false_in_same_list(same_list, index_list_1)
    print(diff_list)
    print(same_list)
    new_list = diff_list + same_fail_list
    print(new_list)
    lines = annotation.get_new_lines_from_list(table1, new_list)
    with open("new_data.txt", "w") as f:
        for line in lines:
            f.write(line + "\n")
