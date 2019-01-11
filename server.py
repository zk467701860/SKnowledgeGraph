# -*- coding: utf-8 -*-
import inspect
import logging
import sys

from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS

from db.engine_factory import EngineFactory
from db.heat_handler import SQLHeatHandler
from db.model import PostsRecord, APIEntity, DocumentSentenceText, \
    DocumentSentenceTextAnnotation, DocumentText
from db.search import SOPostSearcher, APISearcher, SentenceSearcher, SentenceSearcher
from qa.new_qa.qa_system import QuestionAnswerSystem
from semantic_search.semantic_search_util_for_api import APISentenceLevelSemanticSearch
from server_util.search import SearchUtil
from shared.logger_util import Logger
from shared.logger_util import SQLAlchemyHandler
from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient
from skgraph.graph.accessor.graph_client_for_api import APIGraphAccessor
from skgraph.graph.accessor.graph_client_for_sementic_search import SemanticSearchAccessor
from skgraph.graph.label_util import LabelUtil
from skgraph.graph.node_cleaner import GraphJsonParser

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
CORS(app)
db_handler = SQLAlchemyHandler()
db_handler.setLevel(logging.WARN)  # Only serious messages
app.logger.addHandler(db_handler)

logger = Logger("neo4jServer").get_log()
logger.info("create logger")

client = GraphClient(server_number=4)
graphClient = DefaultGraphAccessor(client)
logger.info("create graphClient")

apiGraphClient = APIGraphAccessor(client)
semanticSearchAccessor = SemanticSearchAccessor(client)

# api_entity_linker = APIEntityLinking()
# logger.info("create api_entity_linker object")

questionAnswerSystem = QuestionAnswerSystem()
logger.info("create questionAnswerSystem")

dbSOPostSearcher = SOPostSearcher(EngineFactory.create_so_session(), logger=app.logger)
logger.info("create SO POST Searcher")

api_entity_session = EngineFactory.create_session(autocommit=True)
apiSearcher = APISearcher(session=api_entity_session, logger=app.logger)
logger.info("create API Searcher")

dbSentenceSearcher = SentenceSearcher(EngineFactory.create_so_session(), logger=app.logger)
logger.info("create QA sentence Searcher")

sql_heat_handler = SQLHeatHandler(session=EngineFactory.create_heat_session(), logger=app.logger)
logger.info("create SQL HeatHandler")

graphJsonParser = GraphJsonParser(graph_accessor=graphClient)
logger.info("create graphJsonParser Json Parser")

NEWEST_NODE = graphClient.get_newest_nodes(10)
logger.info("init newest node")

labelUtil = LabelUtil()

ALL_LABELS_LIST = labelUtil.get_all_public_label_name_list
logger.info("init all labels")

# semantic_searcher = SentenceLevelSemanticSearch()
# semantic_searcher.init()

api_semantic_searcher = APISentenceLevelSemanticSearch()
api_semantic_searcher.init()

search_util = SearchUtil(graphClient, apiSearcher, api_semantic_searcher)

logger.info("semantic_searcher init complete")

METADATA = {"Entity": graphClient.count_nodes(),
            "Relation": graphClient.count_relations(),
            "Relation Type": graphClient.count_relation_type(),
            "API Package": graphClient.count_package_nodes(),
            "API Class": graphClient.count_class_nodes(),
            "API Method": graphClient.count_method_nodes()}

logger.info("init all metadata")

## todo: 1. add logger to all interface record all api calling and fail. the time of calling.

API_SUMMARY_CACHE = {}


@app.route('/')
def hello():
    return "Hello World!\n This is SKnowledgeGraph"


if __name__ == '__main__':
    from werkzeug.contrib.fixers import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run()
    logger.info("app.run()")


@app.route('/getStartNode/', methods=['POST', 'GET'])
def getStartNode():
    node = graphClient.find_node_by_id(7686)
    logger.info("start node %r" % node)
    r = graphJsonParser.parse_node_to_public_json(node)
    logger.info("start node dict %r" % r)
    jsonify1 = jsonify(r)
    logger.info("start node jsonify1 %r" % jsonify1)
    return jsonify1


@app.route('/getNodeByID/', methods=['POST', 'GET'])
def getNodeByID():
    if not request.json:
        app.logger.warn("getNodeByID fail empty json")
        return "fail"
    if not 'id' in request.json:
        logger.warn("getNodeByID fail" + str(request.json))
        app.logger.warn("getNodeByID fail" + str(request.json))
        return "fail"
    apit_id = request.json['id']
    sql_heat_handler.like(apit_id)
    node = graphClient.find_node_by_id(apit_id)
    r = graphJsonParser.parse_node_to_public_json(node)
    print("call get node by ID for %r" % apit_id)
    return jsonify(r)


@app.route('/getRelationsBetweenTwoNodes/', methods=['POST', 'GET'])
def getRelationsBwtweenTwoNodes():
    if not request.json:
        app.logger.warn("getRelationsBwtweenTwoNodes fail empty json")
        return "fail"
    sid = request.json['start_id']
    eid = request.json['end_id']
    subgraph = graphClient.get_relations_between_two_nodes_in_subgraph(sid, eid)
    relations_json = graphJsonParser.parse_relations_in_subgraph_to_public_json(subgraph)
    return jsonify({'relations': relations_json})


@app.route('/expandNode/', methods=['POST', 'GET'])
def expandNode():
    if not request.json:
        app.logger.warn("expandNode fail empty json")
        return "fail"
    if not 'id' in request.json:
        app.logger.warn("expandNode fail" + str(request.json))
        return "fail"
    limit = 50
    if 'limit' in request.json:
        limit = request.json["limit"]

    apit_id = request.json['id']
    sql_heat_handler.like(apit_id)
    subgraph = graphClient.expand_node_for_adjacent_nodes_to_subgraph(apit_id, limit=limit)

    subgraph_json = graphJsonParser.parse_subgraph_to_public_json(subgraph)
    print("call expandNode %r" % apit_id)

    return jsonify(subgraph_json)


@app.route('/searchNodesByKeyWords/', methods=['POST', 'GET'])
def searchNodesByKeyWords():
    if not request.json:
        app.logger.warn("searchNodesByKeyWords fail empty json")
        return "fail"
    if not 'keywords' in request.json:
        app.logger.warn("searchNodesByKeyWords fail" + str(request.json))
        return "fail"

    top_number = 10
    if 'top_number' in request.json:
        top_number = request.json['top_number']

    node_list = search_util.search(request.json['keywords'], top_number)

    nodes = graphJsonParser.parse_node_list_to_json(node_list)

    return jsonify({'nodes': nodes})


@app.route('/answer/', methods=['POST', 'GET'])
def answer():
    if not request.json or not 'question' in request.json:
        return "fail"
    returns = []
    top_number = 10
    if 'top_number' in request.json:
        top_number = request.json['top_number']

    answer_collection = questionAnswerSystem.full_answer(request.json['question'], top_number)
    if answer_collection is None:
        return 'fail'
    return jsonify(answer_collection.parse_json())


@app.route('/shortestPathToID/', methods=['POST', 'GET'])
def shortestPathToID():
    if not request.json or not 'id' in request.json or not 'end_id' in request.json:
        return "fail"
    DEFAULT_PATH_DEGREE = 6
    DEFAULT_TOP_NUM = 3
    top_number = DEFAULT_TOP_NUM
    max_len = DEFAULT_PATH_DEGREE

    if 'top_number' in request.json:
        top_number = request.json['top_number']
    if 'max_len' in request.json:
        max_len = request.json['max_len']
        if request.json['max_len'] < 1 or request.json['max_len'] > DEFAULT_PATH_DEGREE:
            max_len = DEFAULT_PATH_DEGREE

    subgraph = graphClient.get_shortest_path_in_subgraph(start_id=request.json['id'],
                                                         end_id=request.json['end_id'],
                                                         max_degree=max_len,
                                                         limit=top_number)
    subgraph_json = graphJsonParser.parse_subgraph_to_public_json(subgraph)

    return jsonify(subgraph_json)


@app.route('/shortestPathToName/', methods=['POST', 'GET'])
def shortestPathToName():
    if not request.json or not 'id' in request.json or not 'name' in request.json:
        return "fail"
    DEFAULT_PATH_DEGREE = 6
    top_number = 3
    if 'top_number' in request.json:
        top_number = request.json['top_number']
    max_len = DEFAULT_PATH_DEGREE
    if 'max_len' in request.json:
        max_len = request.json['max_len']
        if request.json['max_len'] < 1 or request.json['max_len'] > DEFAULT_PATH_DEGREE:
            max_len = DEFAULT_PATH_DEGREE

    subgraph = graphClient.get_shortest_path_to_name_in_subgraph(request.json['id'],
                                                                 request.json['name'],
                                                                 max_len, top_number)
    subgraph_json = graphJsonParser.parse_subgraph_to_public_json(subgraph)

    return jsonify(subgraph_json)


@app.route('/GetKnowledgeGraphMetaData/', methods=['POST', 'GET'])
def GetKnowledgeGraphMetaData():
    return jsonify(METADATA)


# @app.route('/EntityLink/', methods=['POST', 'GET'])
# def entity_link():
#     if not request.json:
#         return "fail"
#     returns = []
#     j = request.json
#     if 'str' in j:
#         returns = api_entity_linker.get_link(j['str'])
#
#     return jsonify(returns)


@app.route('/GetOutRelation/', methods=['POST', 'GET'])
def get_out_relation():
    # todo change the to "page_index" and define it value start from 0
    if not request.json:
        return "fail"
    j = request.json
    if 'id' in j and 'page_number' in j:
        returns = graphJsonParser.parse_relation_list_to_json(
            graphClient.find_out_relation_list(j['id'], j['page_number']))
        return jsonify({'relations': returns})

    return 'fail'


@app.route('/GetInRelation/', methods=['POST', 'GET'])
def get_in_relation():
    # todo change the to "page_index" and define it value start from 0

    if not request.json:
        return "fail"
    j = request.json
    if 'id' in j and 'page_number' in j:
        returns = graphJsonParser.parse_relation_list_to_json(
            graphClient.find_in_relation_list(j['id'], j['page_number']))
        return jsonify({'relations': returns})

    return 'fail'


@app.route('/GetNewNodes/', methods=['POST', 'GET'])
def get_new_nodes():
    top_number = 5
    if request.json:
        j = request.json
        if 'top_number' in j:
            top_number = int(j['top_number'])
    nodes = NEWEST_NODE[:top_number]

    returns = graphJsonParser.parse_node_list_to_json(nodes)
    return jsonify({'nodes': returns})


@app.route('/GetIntroduction/', methods=['POST', 'GET'])
def get_introduction():
    returns = []
    returns.append({'text': '''Our API-centric knowledge graph propose to bridge the knowledge gap between software documents. The knowledge graph is built by extracting entities and relations from multiple heterogeneous information sources and fusing the knowledge through entity resolution.
It is buit by Fudan Software Engineering Laboratory. We have constructed a knowledge graph for JDK and Android APIs and we will develop an integrated platform that provides API-centric knowledge services such as question answering and knowledge recommendation for the public.'''})
    return jsonify(returns)


@app.route('/GetPopularNodes/', methods=['POST', 'GET'])
def get_popular_nodes():
    top_number = 3
    if request.json:
        j = request.json
        if 'top_number' in j:
            top_number = int(j['top_number'])
    entity_heat_list = sql_heat_handler.get_most_popular_entity_id_list(top_number=top_number)
    nodes = []

    for heat in entity_heat_list:
        entity_id = heat["api_id"]
        node = graphClient.find_node_by_id(entity_id)
        nodes.append(node)

    returns = graphJsonParser.parse_node_list_to_json(nodes)
    return jsonify({'nodes': returns})


@app.route('/GetAllLabels/', methods=['POST', 'GET'])
def get_all_labels():
    """
    get all labels name
    :return:
    """
    returns = ALL_LABELS_LIST
    return jsonify({'labels': returns})


@app.route('/SearchAPI/', methods=['POST', 'GET'])
def search_api():
    if not request.json:
        return "fail"
    j = request.json

    if not 'keyword' in j:
        return "fail"

    keyword = j['keyword']
    label = 'api'
    top_number = 10
    if 'label' in j:
        label = j['label']
    if 'top_number' in j:
        top_number = j['top_number']

    returns = graphJsonParser.parse_nodes_in_subgraph_to_public_json(
        graphClient.search_nodes_by_keyword(keyword, label, top_number))
    return jsonify({'nodes': returns})


@app.route('/SearchAPIID/', methods=['POST', 'GET'])
def search_api_id():
    request_json = request.json

    if not check_completeness_api_with_parameters(inspect.stack()[0][3], request_json, 'keyword'):
        return "fail"

    keyword = request_json['keyword']
    api_type = APIEntity.API_TYPE_ALL_API_ENTITY
    top_number = 10
    if 'api_type' in request_json:
        api_type = request_json['api_type']
    if 'top_number' in request_json:
        top_number = request_json['top_number']

    api_entity_list = apiSearcher.search_api_entity(query=keyword, result_limit=top_number, api_type=api_type)
    api_id_list = []
    for api_entity in api_entity_list:
        api_id_list.append(api_entity.id)
    returns = graphClient.get_api_entity_map_to_node_id(api_id_list)
    return jsonify(returns)


@app.route('/SearchAPINode/', methods=['POST', 'GET'])
def search_api_node():
    request_json = request.json

    if not check_completeness_api_with_parameters(inspect.stack()[0][3], request_json, 'keyword'):
        return "fail"

    keyword = request_json['keyword']
    api_type = APIEntity.API_TYPE_ALL_API_ENTITY
    top_number = 10
    if 'api_type' in request_json:
        api_type = request_json['api_type']
    if 'top_number' in request_json:
        top_number = request_json['top_number']

    api_entity_list = apiSearcher.search_api_entity_with_order(query=keyword, result_limit=top_number,
                                                               api_type=api_type)
    api_id_list = []
    for api_entity in api_entity_list:
        api_id_list.append(api_entity.id)
    nodes = graphClient.get_api_entity_map_to_node(api_id_list)
    returns = graphJsonParser.parse_node_list_to_json(nodes)
    return jsonify(returns)


@app.route('/APILinking/', methods=['POST', 'GET'])
def api_linking():
    if not request.json:
        return "fail"
    j = request.json

    if not 'api_string' in j:
        return "fail"

    api_string = j['api_string']
    api_type = 1
    top_number = 5
    declaration = ''
    parent_api = ''
    if 'top_number' in j:
        top_number = j['top_number']
    if 'api_type' in j:
        api_type = j['api_type']
    if 'declaration' in j:
        declaration = j['declaration']
    if 'parent_api' in j:
        parent_api = j['parent_api']
    returns = graphClient.api_linking(api_string, top_number, api_type, declaration, parent_api)
    return jsonify(returns)


# KGIDToMySQLID
@app.route('/KGIDToMySQLID/', methods=['POST', 'GET'])
def kg_id2mysql_id():
    if not request.json:
        return "fail"
    j = request.json

    if not 'kg_id' in j:
        return "fail"

    kg_id = j['kg_id']
    returns = graphClient.kg_id2mysql_id(kg_id)
    return jsonify(returns)


# MySQLIDToKGID
@app.route('/MySQLIDToKGID/', methods=['POST', 'GET'])
def mysql_id2kg_id():
    if not request.json:
        return "fail"
    j = request.json

    if not 'mysql_id' in j:
        return "fail"

    mysql_id = j['mysql_id']
    returns = graphClient.mysql_id2kg_id(mysql_id)
    return jsonify(returns)


@app.route('/PostID/', methods=['POST', 'GET'])
def post_get_by_id():
    if not request.json:
        return "fail"
    j = request.json
    if not 'id' in j:
        return "fail"
    id = j['id']
    posts_record = PostsRecord()
    returns = posts_record.get_post_by_id(id)
    return jsonify(returns)


@app.route('/RelatedPosts/', methods=['POST', 'GET'])
def query_related_posts_by_string():
    request_json = request.json
    if not check_completeness_api_with_parameters(inspect.stack()[0][3], request_json, "str"):
        return "fail"
    str = request_json['str']
    if not str or not str.strip():
        return "fail"

    returns = dbSOPostSearcher.search_post_in_simple_format(str, 10)
    return jsonify(returns)


@app.route('/GetRelationDescription/', methods=['POST', 'GET'])
def get_relation_description():
    request_json = request.json
    if not check_completeness_api_with_parameters(inspect.stack()[0][3], request_json, "name"):
        return "fail"

    name = request_json['name']
    if not name or not name.strip():
        return "fail"

    returns = graphJsonParser.relationUtil.get_description_by_relation_type(name)
    return jsonify(returns)


def getType(number=0):
    if number == 0:
        return 'api'
    elif number == 1:
        return 'java package'
    elif number == 2:
        return 'java class'
    elif number == 3:
        return 'java class'
    elif number == 4:
        return 'java class'
    elif number == 5:
        return 'java class'
    elif number == 6:
        return 'java field'
    elif number == 7:
        return 'java constructor'
    elif number == 11:
        return 'java method'


def check_parameters_completeness(request_json, *parameters):
    for p in parameters:
        if p not in request_json:
            return False, p

    return True, ""


def check_is_empty_json(request_json):
    if request_json is None:
        return True
    else:
        return False


def check_completeness_api_with_parameters(method_name, request_json, *parameters):
    if check_is_empty_json(request_json):
        app.logger.warn("empty json in %s", method_name)
        return False
    completeness, error_string = check_parameters_completeness(request_json, *parameters)
    if not completeness:
        app.logger.warn("parameter %s is missing in %s", error_string, method_name)
        return False

    return True


@app.route('/Log/', methods=['POST', 'GET'])
def test_log():
    # app.logger.exception("Failed !")
    app.logger.warn("Failed !")
    return ""


@app.route('/GetPublicLabels/', methods=['POST', 'GET'])
def getPublicLabels():
    """
    get public labels detail info
    :return:
    """
    returns = labelUtil.get_all_public_label_json_list()
    return jsonify(returns)


@app.route('/like/', methods=['POST', 'GET'])
def like():
    if not request.json:
        return "fail"
    j = request.json
    if not 'id' in j:
        return "fail"
    api_id = j['id']
    returns = sql_heat_handler.like(api_id)
    return jsonify(returns)


@app.route('/getHeat/', methods=['POST', 'GET'])
def get_api_heat_by_apiID():
    if not request.json:
        return "fail"
    j = request.json
    if not 'id' in j:
        return "fail"

    api_id = j['id']
    returns = sql_heat_handler.get_api_heat_by_apiID(api_id)
    return jsonify(returns)


@app.route('/getDocById/', methods=['POST', 'GET'])
def get_doc_by_id():
    if not request.json:
        return "fail"
    j = request.json
    if not 'doc_id' in j:
        return "fail"
    doc_id = j['doc_id']
    sentence_list = DocumentSentenceText.get_sentence_list_by_doc_id(api_entity_session, doc_id)
    sentence_list_json = []
    for each in sentence_list:
        temp = {
            "id": each.id,
            "doc_id": each.doc_id,
            "sentence_index": each.sentence_index,
            "text": each.text
        }
        sentence_list_json.append(temp)
    return jsonify(sentence_list_json)


@app.route('/getAnnotationCountByIndex/', methods=['POST', 'GET'])
def get_annotation_count_by_index():
    if not request.json:
        return "fail"
    j = request.json
    if 'doc_id' not in j and "sentence_id" not in j:
        return "fail"
    doc_id = j["doc_id"]
    sentence_id = j["sentence_id"]
    sentence_annotation = DocumentSentenceTextAnnotation.get_annotation_count_by_index(api_entity_session, doc_id,
                                                                                       sentence_id)
    if sentence_annotation:
        return jsonify({"annotation_count": sentence_annotation})
    else:
        return jsonify({"annotation_count": -1})


@app.route('/saveSentenceAnnotation/', methods=['POST', 'GET'])
def save_sentence_annotation():
    session = EngineFactory.create_session()
    if not request.json:
        return "fail"
    j = request.json
    for each in j:
        if 'doc_id' not in each and "sentence_index" not in each and "type" not in each and "username" not in each:
            return "fail"
        doc_id = each["doc_id"]
        sentence_index = each["sentence_index"]
        type = each["type"]
        username = each["username"]
        sentence_text_annotation = DocumentSentenceTextAnnotation(doc_id, sentence_index, type, username)
        sentence_text_annotation.find_or_create(session, autocommit=False)
        if sentence_text_annotation.type != type:
            sentence_text_annotation.type = type
    session.commit()
    return "save successful"


@app.route('/getDocIdList/', methods=['POST', 'GET'])
def get_doc_id_list():
    doc_list_data = DocumentText.get_doc_list(api_entity_session)
    doc_id_list = []
    if doc_list_data:
        for each in doc_list_data:
            doc_id = each.id
            text = each.text
            if text is not None and text != "":
                doc_id_list.append(doc_id)
    result = {"doc_id_list": doc_id_list}
    return jsonify(result)


@app.route('/sentenceSearch/', methods=['POST', 'GET'])
def get_sentence_list():
    if not request.json:
        return "fail"
    j = request.json
    if "os_question" not in j:
        return "fail"
    os = j["os_question"]
    session = EngineFactory.create_session()
    searcher = SentenceSearcher(session)
    sentence_data = searcher.search_sentence_answer(os, 10)
    sentence_list = []
    if len(sentence_data) > 0:
        for each in sentence_data:
            text = each[1]
            doc_id = each[0]
            if text is not None and text != "":
                sentence_list.append({"doc_id": doc_id, "text": text})
    result = {"sentence_list": sentence_list}
    return jsonify(result)


@app.route('/sentenceGoogleSearch/', methods=['POST', 'GET'])
def sentence_google_search():
    return "fail"
    # todo fix
    # if not request.json:
    #     return "fail"
    # parameter_json = request.json
    # logger.info("sentence_google_search parameters")
    # logger.info(str(parameter_json))
    #
    # if 'query_text' not in parameter_json:
    #     return "fail"
    # else:
    #     query_text = parameter_json["query_text"]
    #
    # if 'page_limit' not in parameter_json:
    #     page_limit = 10
    # else:
    #     page_limit = parameter_json["page_limit"]
    #
    # if 'api_type' not in parameter_json:
    #     api_type = "general"
    # else:
    #     api_type = parameter_json["api_type"]
    #
    # logger.info("query_text %r" % query_text)
    # logger.info("page_limit %r" % page_limit)
    # logger.info("api_type %r" % api_type)
    # se = SummaryExtraction()
    # page_list = se.summary_extraction(query_text=query_text, api_type=api_type, page_limit=page_limit)
    #
    # logger.info("sentence_google_search successful")
    # logger.info("page_list len=%d" % (len(page_list)))
    #
    # return jsonify(page_list)


@app.route('/sentenceSemanticSearch/', methods=['POST', 'GET'])
def sentence_semantic_search():
    return "fail"
    # todo fix this
    # if not request.json:
    #     return "fail"
    #
    # parameter_json = request.json
    # logger.info("sentence_semantic_search parameters")
    #
    # logger.info(str(parameter_json))
    #
    # if not 'query_text' in parameter_json:
    #     return "fail"
    # else:
    #     query_text = parameter_json["query_text"]
    #
    # if not 'sentence_limit' in parameter_json:
    #     sentence_limit = 100
    # else:
    #     sentence_limit = parameter_json["sentence_limit"]
    #
    # if not 'each_np_candidate_entity_num' in parameter_json:
    #     each_np_candidate_entity_num = 20
    # else:
    #     each_np_candidate_entity_num = parameter_json["each_np_candidate_entity_num"]
    #
    # if not 'sort_function' in parameter_json:
    #     sort_function = semantic_searcher.SORT_FUNCTION_SELECT_PART_ENTITY_LINK
    # else:
    #     sort_function = parameter_json["sort_function"]
    #
    # if not 'weight_context_sim' in parameter_json:
    #     weight_context_sim = 0.5
    # else:
    #     weight_context_sim = parameter_json["weight_context_sim"]
    #
    # if not 'weight_graph_sim' in parameter_json:
    #     weight_graph_sim = 0.5
    # else:
    #     weight_graph_sim = parameter_json["weight_graph_sim"]
    #
    # logger.info("query_text %r" % query_text)
    # logger.info("each_np_candidate_entity_num %r" % each_np_candidate_entity_num)
    # logger.info("sort_function %r" % sort_function)
    # logger.info("sentence_limit %r" % sentence_limit)
    # logger.info("weight_context_sim %r" % weight_context_sim)
    # logger.info("weight_graph_sim %r" % weight_graph_sim)
    #
    # sentence_list = semantic_searcher.semantic_search(query_text=query_text,
    #                                                   each_np_candidate_entity_num=each_np_candidate_entity_num,
    #                                                   sort_function=sort_function,
    #                                                   sentence_limit=sentence_limit,
    #                                                   weight_context_sim=weight_context_sim,
    #                                                   weight_graph_sim=weight_graph_sim
    #                                                   )
    # logger.info("sentence_semantic_search successful")
    # logger.info("sentence_list len=%d" % (len(sentence_list)))
    #
    # return jsonify(sentence_list)


@app.route('/sentenceSemanticSearchTreeView/', methods=['POST', 'GET'])
def sentence_semantic_search_tree_view():
    return "fail"
    # todo fix this
    # if not request.json:
    #     return "fail"
    #
    # parameter_json = request.json
    # logger.info("sentence_semantic_search parameters")
    #
    # logger.info(str(parameter_json))
    #
    # if not 'query_text' in parameter_json:
    #     return "fail"
    # else:
    #     query_text = parameter_json["query_text"]
    #
    # if not 'sentence_limit' in parameter_json:
    #     sentence_limit = 100
    # else:
    #     sentence_limit = parameter_json["sentence_limit"]
    #
    # if not 'each_np_candidate_entity_num' in parameter_json:
    #     each_np_candidate_entity_num = 20
    # else:
    #     each_np_candidate_entity_num = parameter_json["each_np_candidate_entity_num"]
    #
    # if not 'sort_function' in parameter_json:
    #     sort_function = semantic_searcher.SORT_FUNCTION_SELECT_PART_ENTITY_LINK
    # else:
    #     sort_function = parameter_json["sort_function"]
    #
    # if not 'weight_context_sim' in parameter_json:
    #     weight_context_sim = 0.5
    # else:
    #     weight_context_sim = parameter_json["weight_context_sim"]
    #
    # if not 'weight_graph_sim' in parameter_json:
    #     weight_graph_sim = 0.5
    # else:
    #     weight_graph_sim = parameter_json["weight_graph_sim"]
    #
    # logger.info("query_text %r" % query_text)
    # logger.info("each_np_candidate_entity_num %r" % each_np_candidate_entity_num)
    # logger.info("sort_function %r" % sort_function)
    # logger.info("sentence_limit %r" % sentence_limit)
    # logger.info("weight_context_sim %r" % weight_context_sim)
    # logger.info("weight_graph_sim %r" % weight_graph_sim)
    #
    # sentence_list = semantic_searcher.semantic_search(query_text=query_text,
    #                                                   each_np_candidate_entity_num=each_np_candidate_entity_num,
    #                                                   sort_function=sort_function,
    #                                                   sentence_limit=sentence_limit,
    #                                                   weight_context_sim=weight_context_sim,
    #                                                   weight_graph_sim=weight_graph_sim
    #                                                   )
    # api_tree = APITree(sentence_list).tree
    # logger.info("sentence_semantic_search successful")
    # logger.info("sentence_list len=%d" % (len(sentence_list)))

    # return jsonify(api_tree)


@app.route('/sentenceSemanticSearchGraphSummary/', methods=['POST', 'GET'])
def sentence_semantic_search_graph_summary():
    return "fail"
    # todo fix
    # if not request.json:
    #     return "fail"
    #
    # parameter_json = request.json
    # logger.info("sentence_semantic_search parameters")
    #
    # logger.info(str(parameter_json))
    #
    # if not 'query_text' in parameter_json:
    #     return "fail"
    # else:
    #     query_text = parameter_json["query_text"]
    #
    # if not 'sentence_limit' in parameter_json:
    #     sentence_limit = 20
    # else:
    #     sentence_limit = parameter_json["sentence_limit"]
    #
    # logger.info("query_text %r" % query_text)
    # logger.info("sentence_limit %r" % sentence_limit)
    #
    # sentence_list = semantic_searcher.semantic_search(query_text=query_text,
    #                                                   each_np_candidate_entity_num=50,
    #                                                   sort_function=semantic_searcher.SORT_FUNCTION_SELECT_PART_ENTITY_LINK,
    #                                                   sentence_limit=sentence_limit,
    #                                                   weight_context_sim=0.4,
    #                                                   weight_graph_sim=0.6
    #                                                   )
    # logger.info("sentence_semantic_search successful")
    # logger.info("sentence_list len=%d" % (len(sentence_list)))
    # node_list = []
    # relation_list = []
    # summary = []
    # for sentence_dic in sentence_list:
    #     node = {}
    #     sentences = []
    #     flag = 0
    #     node["id"] = sentence_dic["api_kg_id"]
    #     node["name"] = sentence_dic["api_qualified_name"]
    #     if not 'api_document_website#1' in sentence_dic:
    #         node["url"] = "null"
    #     else:
    #         node["url"] = sentence_dic["api_document_website#1"]
    #     if node_list:
    #         for item in node_list:
    #             if item["id"] == node["id"]:
    #                 item["sentences"].append({"text": sentence_dic["text"], "type": sentence_dic["sentence_type"]})
    #                 flag = 1
    #                 break
    #         if flag == 1:
    #             pass
    #         else:
    #             sentences.append({"text": sentence_dic["text"], "type": sentence_dic["sentence_type"]})
    #             node["sentences"] = sentences
    #             node_list.append(node)
    #     else:
    #         sentences.append({"text": sentence_dic["text"], "type": sentence_dic["sentence_type"]})
    #         node["sentences"] = sentences
    #         node_list.append(node)
    # _graph, _config = GraphFactory.create_from_default_config(server_number=4)
    # accessor = SemanticSearchAccessor(_graph)
    # relation_list = accessor.get_nodes_relation(node_list)
    # summary = Connected_subgraph.Get_sub_maps(relation_list, node_list)
    # logger.info("sentenceSemanticSearchGraphSummary  finished")
    # return jsonify(summary)


@app.route('/sentenceSemanticSearchGraphSummaryTwoStep/', methods=['POST', 'GET'])
def sentence_semantic_search_graph_summary_two_step():
    return "fail"
    # todo fix
    # if not request.json:
    #     return "fail"
    #
    # parameter_json = request.json
    # logger.info("sentence_semantic_search parameters")
    # logger.info(str(parameter_json))
    #
    # if not 'query_text' in parameter_json:
    #     return "fail"
    # else:
    #     query_text = parameter_json["query_text"]
    #
    # if not 'sentence_limit' in parameter_json:
    #     sentence_limit = 20
    # else:
    #     sentence_limit = parameter_json["sentence_limit"]
    #
    # logger.info("query_text %r" % query_text)
    # logger.info("sentence_limit %r" % sentence_limit)
    #
    # sentence_list = semantic_searcher.semantic_search(query_text=query_text,
    #                                                   each_np_candidate_entity_num=50,
    #                                                   sort_function=semantic_searcher.SORT_FUNCTION_SELECT_PART_ENTITY_LINK,
    #                                                   sentence_limit=sentence_limit,
    #                                                   weight_context_sim=0.4,
    #                                                   weight_graph_sim=0.6
    #                                                   )
    # logger.info("sentence_semantic_search successful")
    # logger.info("sentence_list len=%d" % (len(sentence_list)))
    # node_list = []
    # for sentence_dic in sentence_list:
    #     node = {}
    #     sentences = []
    #     flag = 0
    #     node["id"] = sentence_dic["api_kg_id"]
    #     node["name"] = sentence_dic["api_qualified_name"]
    #     if not 'api_document_website#1' in sentence_dic:
    #         node["url"] = "null"
    #     else:
    #         node["url"] = sentence_dic["api_document_website#1"]
    #     for item in node_list:
    #         if item["id"] == node["id"]:
    #             item["sentences"].append({"text": sentence_dic["text"], "type": sentence_dic["sentence_type"]})
    #             flag = 1
    #             break
    #     if flag == 1:
    #         pass
    #     else:
    #         sentences.append({"text": sentence_dic["text"], "type": sentence_dic["sentence_type"]})
    #         node["sentences"] = sentences
    #         node_list.append(node)
    # _graph, _config = GraphFactory.create_from_default_config(server_number=4)
    # accessor = SemanticSearchAccessor(_graph)
    # relation_list, node_list = accessor.get_nodes_relation_by_two_steps(node_list)
    # summary = Connected_subgraph.Get_sub_maps(relation_list, node_list)
    # logger.info("sentenceSemanticSearchGraphSummaryTwoStep  finished")
    # return jsonify(summary)


@app.route('/sentenceSemanticSearchTableFinal/', methods=['POST', 'GET'])
def sentence_semantic_search_graph_table_final():
    if not request.json:
        return "fail"

    parameter_json = request.json
    logger.info("sentence_semantic_search parameters")
    logger.info(str(parameter_json))

    if not 'query_text' in parameter_json:
        return "fail"
    else:
        query_text = parameter_json["query_text"]

    if not 'sentence_limit' in parameter_json:
        sentence_limit = 20
    else:
        sentence_limit = parameter_json["sentence_limit"]

    logger.info("query_text %r" % query_text)
    logger.info("sentence_limit %r" % sentence_limit)
    print("query text type ", type(query_text))

    if query_text in API_SUMMARY_CACHE.keys():
        return API_SUMMARY_CACHE[query_text]
    result_list = api_semantic_searcher.semantic_search_summary_by_api_with_class(query_text=query_text,
                                                                                  weight_graph_sim=0.4,
                                                                                  weight_context_sim=0.6,
                                                                                  )
    logger.info("api_sentence_semantic_search successful")
    logger.info("sentence_list len=%d" % (len(result_list)))
    accessor = semanticSearchAccessor
    final_result_list = []
    for rank, sentence_collection in enumerate(result_list):
        all_sentence_infos = sentence_collection.get_all_sentence_infos()
        first_sentence = all_sentence_infos[0].parse_to_json()
        first = SentenceSearcher.search_first_sentence_by_api_id(first_sentence["api_id"])
        if first_sentence["api_type"] == 2 or first_sentence["api_type"] == 3:
            first_class_name = first_sentence["api_qualified_name"]
            first_method = first_sentence["api_qualified_name"]
        else:
            first_class_name = accessor.get_api_class_by_api_id(first_sentence["api_kg_id"])
            first_method = first_sentence["api_qualified_name"]
        final_result_list.append(
            {
                "class_name": first_class_name,
                "sim": sentence_collection.get_sum_qs_sim(),
                "sentences": [{"method": first_method, "text": first_sentence["text"], "first": first}]
            }
        )
        for index in range(1, len(all_sentence_infos)):
            sentence = all_sentence_infos[index].parse_to_json()
            first = SentenceSearcher.search_first_sentence_by_api_id(sentence["api_id"])
            # print "api_name: ", sentence["api_qualified_name"]," ",sentence["api_kg_id"]
            if first_class_name == None:
                first_class_name = accessor.get_api_class_by_api_id(sentence["api_kg_id"])
                final_result_list[len(final_result_list) - 1]["class_name"] = first_class_name
            method = sentence["api_qualified_name"]
            final_result_list[len(final_result_list) - 1]["sentences"].append(
                {"method": method, "text": sentence["text"], "first": first})
        if final_result_list[len(final_result_list) - 1]["class_name"] == None:
            final_result_list[len(final_result_list) - 1]["class_name"]=first_method
    logger.info("sentenceSemanticSearchTableFinal finished")
    json_return_value = jsonify(final_result_list)
    logger.info("start node jsonify1 %r" % json_return_value)
    
    API_SUMMARY_CACHE[query_text] = json_return_value
    return json_return_value
