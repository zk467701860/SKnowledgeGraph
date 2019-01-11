import traceback

from graph_accessor import GraphAccessor
from shared.logger_util import Logger

_logger = Logger("SentenceAccessor").get_log()


class SemanticSearchAccessor(GraphAccessor):
    def get_all_entity(self, entity_id_string_list):
        try:
            query = "MATCH (n:`entity`) WHERE id(n) in [{kg_id_list}] return DISTINCT n".format(
                kg_id_list=",".join(entity_id_string_list))
            record_list = self.graph.run(query)

            entity_list = []
            for record in record_list:
                entity_list.append(record["n"])

            return entity_list
        except Exception, error:
            traceback.print_exc()
        return []

    def search_sentence_by_entity_list(self, entity_id_string_list):
        try:
            query = "MATCH (n:`entity`)-[r*1..2]-(relateNode:`sentence`) WHERE id(n) in [{kg_id_list}] return DISTINCT relateNode".format(
                kg_id_list=",".join(entity_id_string_list))
            record_list = self.graph.run(query)

            sentence_list = []
            for record in record_list:
                sentence_list.append(record["relateNode"])
                # print record["relateNode"]["sentence_type_code"]

            return sentence_list
        except Exception, error:
            traceback.print_exc()
        return []

    def search_sentence_by_directly_to_api(self, entity_id_string_list):
        try:
            query = "MATCH (n:`api`)<-[r:`source from`]-(relateNode:`sentence`) WHERE id(n) in [{kg_id_list}] return DISTINCT relateNode".format(
                kg_id_list=",".join(entity_id_string_list))
            record_list = self.graph.run(query)
            # todo: add the sentence from parameter and return value
            sentence_list = []
            for record in record_list:
                sentence_list.append(record["relateNode"])
                # print record["relateNode"]["sentence_type_code"]

            return sentence_list
        except Exception, error:
            traceback.print_exc()
        return []

    def search_api_by_entity_list(self, entity_id_string_list):
        try:
            # query = "MATCH (n:`entity`)-[r*1..2]-(relateNode:`api`) WHERE id(n) in [{kg_id_list}] return DISTINCT relateNode".format(
            #     kg_id_list=",".join(entity_id_string_list))
            query = "MATCH (n:`entity`)-[r*1..2]-(relateNode:`api`) WHERE id(n) in [{kg_id_list}] return DISTINCT relateNode".format(
                kg_id_list=",".join(entity_id_string_list))
            record_list = self.graph.run(query)

            sentence_list = []
            for record in record_list:
                sentence_list.append(record["relateNode"])
            return sentence_list
        except Exception, error:
            traceback.print_exc()
        return []

    def get_api_id_for_sentence(self, kg_id):
        try:
            query = "MATCH (n:`sentence`)-[r:`source from`]->(m:`api`) WHERE id(n) = {kg_id} return id(m) limit 1".format(
                kg_id=kg_id)
            api_id = self.graph.evaluate(query)

            return api_id
        except Exception, error:
            traceback.print_exc()
        return None

    def get_api_entity_for_sentence(self, kg_id):
        try:
            query = "MATCH (n:`sentence`)-[r:`source from`]->(m:`api`) WHERE id(n) = {kg_id} return m limit 1".format(
                kg_id=kg_id)
            api_entity = self.graph.evaluate(query)

            return api_entity
        except Exception, error:
            traceback.print_exc()
        return None

    def get_nodes_relation(self, node_list):
        relation_list = []
        for startnode in node_list:
            for endnode in node_list:
                if startnode != endnode:
                    try:
                        query = "MATCH (n:`api`)-[r]->(m:`api`) WHERE id(n) = {kg_id} and id(m)={mkg_id} return id(r),type(r)".format(
                            kg_id=int(startnode["id"]), mkg_id=int(endnode["id"]))
                        record_list = self.graph.run(query).data()
                        if len(record_list):
                            for record in record_list:
                                relation_list.append(
                                    {
                                        "id": record["id(r)"],
                                        "name": record["type(r)"],
                                        "start_id": startnode["id"],
                                        "end_id": endnode["id"]
                                    }
                                )
                        else:
                            pass
                    except Exception, error:
                        traceback.print_exc()
        return relation_list

    def get_nodes_relation_by_two_steps(self, node_list):
        relation_list = []
        virtual_id = 400000
        add_node_list = []
        for start in range(0, len(node_list) - 1):
            for end in range(start + 1, len(node_list)):
                startnode = node_list[start]
                endnode = node_list[end]
                tem_relation_list = self.get_two_api_node_relation_by_id(startnode["id"], endnode["id"])
                # if the two nodes don't have relationship ,find their relationship in two steps
                if len(tem_relation_list):
                    relation_list += tem_relation_list
                else:
                    query = "match(n:api)-[r1]-(q:api)-[r2]-(m:api) WHERE id(n) = {kg_id} and id(m)={mkg_id} return id(q),q,labels(q),type(r1),type(r2)".format(
                        kg_id=int(startnode["id"]), mkg_id=int(endnode["id"]))
                    record_list3 = self.graph.run(query).data()
                    if len(record_list3):
                        # if the middle node is labeled "api class", add the middle node to node_list
                        # otherwise add a relation between startnode and endnode
                        flag = 0
                        for item in record_list3:
                            if "api class" in item["labels(q)"]:
                                flag = 1
                                add_new_node = {
                                    "id": item["id(q)"],
                                    "name": item["q"]["qualified_name"],
                                    "url": "null",
                                    "sentences": []
                                }
                                if add_new_node not in add_node_list:
                                    add_node_list.append(add_new_node)
                        if flag == 0:
                            relation_list.append(
                                {
                                    "id": virtual_id,
                                    "name": "related to",
                                    "start_id": startnode["id"],
                                    "end_id": endnode["id"]
                                }
                            )
                            virtual_id += 1
        # print(add_node_list)
        # judge new add node wether is in node_list
        new_add_node_list = []
        for item1 in add_node_list:
            flag = 0
            for item2 in node_list:
                if item1["id"] == item2["id"]:
                    flag = 1
            if flag == 0:
                new_add_node_list.append(item1)
        if len(new_add_node_list):
            for startnode in new_add_node_list:
                for endnode in node_list:
                    add_relation_list = self.get_two_api_node_relation_by_id(startnode["id"], endnode["id"])
                    if len(add_relation_list):
                        relation_list += add_relation_list
            node_list += new_add_node_list
        return relation_list, node_list

    def get_two_api_node_relation_by_id(self, start_id, end_id):
        try:
            relation_list = []
            query = "MATCH (n:`api`)-[r]->(m:`api`) WHERE id(n) = {kg_id} and id(m)={mkg_id} return id(r),type(r)".format(
                kg_id=int(start_id), mkg_id=int(end_id))
            record_list1 = self.graph.run(query).data()
            query = "MATCH (n:`api`)<-[r]-(m:`api`) WHERE id(n) = {kg_id} and id(m)={mkg_id} return id(r),type(r)".format(
                kg_id=int(start_id), mkg_id=int(end_id))
            record_list2 = self.graph.run(query).data()
            for record in record_list1:
                relation_list.append(
                    {
                        "id": record["id(r)"],
                        "name": record["type(r)"],
                        "start_id": start_id,
                        "end_id": end_id
                    }
                )
            for record in record_list2:
                relation_list.append(
                    {
                        "id": record["id(r)"],
                        "name": record["type(r)"],
                        "start_id": end_id,
                        "end_id": start_id
                    }
                )
            return relation_list
        except Exception, error:
            traceback.print_exc()


    def judge_api_class_by_api_id(self, api_id):
        try:
            query = "MATCH (n:`api`) WHERE id(n) = {kg_id}  return labels(n)".format(
                kg_id=api_id)
            record_list1 = self.graph.run(query).data()
            for record in record_list1:
                if "api class" in record["labels(n)"]:
                    return 1
                # elif "api method" in record["labels(n)"]:
                #     return 2
                else:
                    return 2
        except Exception, error:
            traceback.print_exc()


    def get_api_class_by_api_id(self, api_id):
        try:
            query = "match(m:`api class`)-[r]->(n) where id(n) = {kg_id}  return m.qualified_name".format(
                kg_id=api_id)
            record_list = self.graph.run(query).data()
            if len(record_list):
                for record in record_list:
                    return record["m.qualified_name"]
            else:
                query2 = "match(m:`api interface`)-[r]->(n) where id(n) = {kg_id}  return m.qualified_name".format(
                    kg_id=api_id)
                record_list2 = self.graph.run(query2).data()
                for record in record_list2:
                    return record["m.qualified_name"]
            query3 = "match(m:`api package`)-[r]->(n) where id(n) = {kg_id}  return m.qualified_name".format(
                kg_id=api_id)
            record_list3 = self.graph.run(query3).data()
            for record in record_list3:
                return record["m.qualified_name"]
            return None
        except Exception, error:
            traceback.print_exc()
