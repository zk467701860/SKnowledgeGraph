# entity
#### 引入的节点的label
- awesome category, awesome list中的子标题，表示了一些功能类型的概念
- awesome item，代表了一个一个库
- awesome list，代表了一个一个awesome list
- awesome list topic,代表了awesome list的主题，比如awesome python，python是awesome Python的主题。
#### 原始的json数据

1. awesome_item_entity_list.json
    - awesome列表中的条目,有name,url,description等属性。
    - 导入图数据库，节点具有标签"awesome item","entity"。
    - 已经导入
1. awesome_item_category_entity_list.json
    - awesome_item_category表示在awesome list中的子标题，代表了接下来库具有的共同的功能，"Json Processing"就是一个awesome category。这个json是个list。
    - 导入图数据库，节点具有标签"awesome category","entity"。
    - 已经导入
1. awesome_list_cate_entity_list.json
    - awesome_item_category表示在"list of awesome list"中的子标题，代表了awesome list的划分的种类，比如"Networking".这个json是个list。
    - 导入图数据库，节点具有标签"awesome category","entity"。
    - 已经导入
1. new_complete_list_of_awesome_list.json
    - 表示在"awesome list" of 这个json是个list。
    - 导入图数据库，节点具有标签"awesome list","entity"。
    - 已经导入

# relation
1. collect_relation.json
    - 表示了某个awesome列表收集了某些库
    - 表示在("awesome list","collect","awesome item")关系，
    - 已经导入
1. subtopic_list_relation.json
    - 表示了某个awesome列表还包含了更加细的awesome列表
    - 表示在("awesome list","has subtopic list","awesome list")关系，
    - 已经导入    
1. complete_list_of_awesome_list_collect_relation.json
    - 表示了总的awesome list收集了其他人的awesome list
    - 表示在("awesome list","has subtopic list","awesome list")关系，
    - 已经导入  

1. awesome_list_relation.json
    - 加入defined for,contain topic,main category,related to.表示了awesome_list 的关系，包括(awesome list,related to,wikipedia)
    - 已经导入  
1. awesome_item_category_related_to_wikipedia_relation_list.json
    - 加入awesome category与对应地维基百科概念地关系，包括(awesome category,related to,wikipedia)
    - 已经导入      




