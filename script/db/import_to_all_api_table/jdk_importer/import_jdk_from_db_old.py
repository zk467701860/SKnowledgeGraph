import traceback

import MySQLdb

from db.cursor_factory import ConnectionFactory

cur = ConnectionFactory.create_cursor_for_jdk_importer()


# neo4j connect


# read from mysql
def mySQLReader(start, end):


    # get all-version library
    cur.execute("select * from jdk_library where library_id >= %s and library_id < %s", (start, end))
    lib_sql_data_list = cur.fetchall()

    for lib_node_mysql_data_index in range(0, len(lib_sql_data_list)):
        lib_node, library_id = create_library_node_from_mysql(lib_node_mysql_data_index, node1lib, lib_sql_data_list)

        # get package
        cur.execute("select * from jdk_package where library_id = %s", (library_id,))
        package_sql_data_list = cur.fetchall()

        for package_node_sql_data_index in range(0, len(package_sql_data_list)):
            api_package_id, package_node = create_package_node_from_mysql(package_node_sql_data_index, lib_node,
                                                                          package_sql_data_list)

            # get class
            cur.execute("select * from jdk_class where package_id = %s", (api_package_id,))
            class_node_sql_data_list = cur.fetchall()
            for class_node_sql_data_index in range(0, len(class_node_sql_data_list)):
                api_class_id, class_node = create_class_node_from_mysql(class_node_sql_data_index, package_node,
                                                                        class_node_sql_data_list)

                # get method
                cur.execute("select * from jdk_method where class_id = %s", (api_class_id,))
                method_node_sql_data_list = cur.fetchall()
                for method_node_sql_data_index in range(0, len(method_node_sql_data_list)):
                    api_method_id, method_node, api_method_retStr, api_method_retType = create_method_node_from_mysql(
                        class_node,
                        method_node_sql_data_index,
                        method_node_sql_data_list)  # get method parameter
                    create_return_value_node_from_mysql(api_method_retStr, api_method_retType, method_node)

                    cur.execute("select * from jdk_parameter where method_id = %s", (api_method_id,))
                    parameter_node_sql_data_list = cur.fetchall()
                    for parameter_node_sql_data_index in range(0, len(parameter_node_sql_data_list)):
                        create_parameter_node_from_mysql(parameter_node_sql_data_index, method_node,
                                                         parameter_node_sql_data_list)

                    cur.execute("select * from jdk_exception where method_id = %s", (api_method_id,))
                    exception_node_sql_data_list = cur.fetchall()
                    for exception_node_sql_data_index in range(0, len(exception_node_sql_data_list)):
                        create_throw_exception_node_from_mysql(exception_node_sql_data_index, method_node,
                                                               exception_node_sql_data_list)

    print "reading from mysql completed!"


def create_return_value_node_from_mysql(api_method_retStr, api_method_retType, method_node):
    if api_method_retStr is not None and api_method_retStr != "":
        api_return_value_node = NodeBuilder(). \
            add_label("api"). \
            add_label("java method return value"). \
            add_label("entity"). \
            add_one_property("name", api_method_retStr). \
            add_one_property("value description", api_method_retStr). \
            add_one_property("value type", api_method_retType). \
            build()
        connect_graph.merge(api_return_value_node)
        connect_graph.merge(Relationship(method_node, 'return', api_return_value_node))


def create_parameter_node_from_mysql(l, method_node, result4):
    api_parameter_id = result4[l][0]
    api_parameter_name = result4[l][1]
    api_parameter_type_class_id = result4[l][4]
    api_parameter_type_string = result4[l][5]
    api_parameter_description = result4[l][6]
    api_parameter_description = clean_html_text(api_parameter_description)
    try:
        sql = "select name,doc_website from jdk_class where class_id = " + str(
            api_parameter_type_class_id)
        cur.execute(sql)
        class_query = cur.fetchone()
        class_name = class_query[0]
        class_doc_website = class_query[1]
    except Exception:
        traceback.print_exc()
        class_name = None
        class_doc_website = None
    parameter_node = NodeBuilder(). \
        add_label("api"). \
        add_label("java method parameter"). \
        add_one_property("name", api_parameter_type_string + " " + api_parameter_name). \
        add_one_property("formal parameter name", api_parameter_name). \
        add_one_property("formal parameter type", api_parameter_type_string). \
        add_one_property("description", api_parameter_description). \
        add_one_property("formal parameter type document website", class_doc_website). \
        add_one_property("formal parameter type full name", class_name). \
        build()
    connect_graph.merge(parameter_node)
    # connect_graph.merge(Relationship(parameter_node, 'instance of', node6para))
    connect_graph.merge(Relationship(parameter_node, 'belong to', method_node))


def create_throw_exception_node_from_mysql(l, method_node, result4):
    exception_id = result4[l][0]
    exception_name = result4[l][1]
    throw_exception_description = result4[l][4]
    throw_exception_description = clean_html_text(throw_exception_description)
    throw_exception_node = NodeBuilder(). \
        add_label("api"). \
        add_label("entity"). \
        add_label("java throw exception description"). \
        add_one_property("name", throw_exception_description). \
        add_one_property("exception type", exception_name). \
        add_one_property("description", throw_exception_description). \
        build()
    connect_graph.merge(throw_exception_node)
    connect_graph.merge(Relationship(method_node, 'throw exception description', throw_exception_node))
    if method_node["throw exception"] is not None:
        method_node["throw exception"] = method_node["throw exception"].append(exception_name)
    else:
        exception_list = [exception_name]
        method_node["throw exception"] = exception_list
    connect_graph.push(method_node)


def create_method_node_from_mysql(class_node, n, result3):
    api_method_id = result3[n][0]
    api_method_type = result3[n][1]
    api_method_name = result3[n][2]
    api_method_declaration = result3[n][3]
    api_method_retType = result3[n][4]
    api_method_retStr = result3[n][5]
    api_method_des = result3[n][6]
    api_method_first_version = result3[n][7]
    api_method_is_static = result3[n][8]
    api_method_override = result3[n][9]
    api_method_specify = result3[n][10]
    api_method_declaration = clean_html_text(api_method_declaration)
    api_method_retStr = clean_html_text(api_method_retStr)
    api_method_des = clean_html_text(api_method_des)
    if "Field" == api_method_type:
        method_node = NodeBuilder(). \
            add_label("api"). \
            add_label("java field"). \
            add_one_property("name", api_method_name). \
            add_one_property("field name", api_method_name). \
            add_one_property("api type", api_method_type). \
            add_one_property("declaration", api_method_declaration). \
            add_one_property("return value type", api_method_retType). \
            add_one_property("return value description", api_method_retStr). \
            add_one_property("first version", api_method_first_version). \
            add_one_property("override", api_method_override). \
            add_one_property("description", api_method_des). \
            build()

        connect_graph.merge(method_node)
        # connect_graph.merge(Relationship(method_node, 'instance of', node5field))
        connect_graph.merge(Relationship(method_node, 'belong to', class_node))

    else:
        if "Nested" == api_method_type:
            method_node = NodeBuilder(). \
                add_label("api"). \
                add_label("java nested class"). \
                add_one_property("name", api_method_name). \
                add_one_property("class name", api_method_name). \
                add_one_property("api type", "nested class"). \
                add_one_property("declaration", api_method_declaration). \
                add_one_property("return value type", api_method_retType). \
                add_one_property("class description", api_method_retStr). \
                add_one_property("first version", api_method_first_version). \
                add_one_property("override", api_method_override). \
                add_one_property("description", api_method_des). \
                build()
        else:
            if api_method_type.lower() == "optional" or api_method_type.lower() == "required":
                method_node = NodeBuilder(). \
                    add_label("api"). \
                    add_label("java abstract property"). \
                    add_one_property("name", api_method_name). \
                    add_one_property("method name", api_method_name). \
                    add_one_property("api type", api_method_type). \
                    add_one_property("declaration", api_method_declaration). \
                    add_one_property("return value type", api_method_retType). \
                    add_one_property("return value description", api_method_retStr). \
                    add_one_property("first version", api_method_first_version). \
                    add_one_property("override", api_method_override). \
                    add_one_property("description", api_method_des). \
                    build()
            else:
                method_node = NodeBuilder(). \
                    add_label("api"). \
                    add_label("java " + api_method_type.lower()). \
                    add_one_property("name", api_method_name). \
                    add_one_property("method name", api_method_name). \
                    add_one_property("api type", api_method_type). \
                    add_one_property("declaration", api_method_declaration). \
                    add_one_property("return value type", api_method_retType). \
                    add_one_property("return value description", api_method_retStr). \
                    add_one_property("first version", api_method_first_version). \
                    add_one_property("override", api_method_override). \
                    add_one_property("description", api_method_des). \
                    build()

        connect_graph.merge(method_node)
        # connect_graph.merge(Relationship(method_node, 'instance of', node4method))
        connect_graph.merge(Relationship(method_node, 'belong to', class_node))

    return api_method_id, method_node, api_method_retStr, api_method_retType


def create_class_node_from_mysql(m, package_node, result2):
    api_class_id = result2[m][0]
    api_class_name = result2[m][1]
    api_class_first_version = result2[m][6]
    api_class_type = result2[m][8]
    api_class_doc_website = result2[m][9]
    api_class_description = result2[m][3]
    api_class_description = clean_html_text(api_class_description)
    class_node = NodeBuilder(). \
        add_label("api"). \
        add_label("java class"). \
        add_one_property("name", api_class_name). \
        add_one_property("class name", api_class_name). \
        add_one_property("first version", api_class_first_version). \
        add_one_property("api document website", api_class_doc_website). \
        add_one_property("description", api_class_description). \
        add_one_property("api type", api_class_type). \
        build()
    connect_graph.merge(class_node)
    # connect_graph.merge(Relationship(class_node, 'instance of', node3class))
    connect_graph.merge(Relationship(class_node, 'belong to', package_node))
    return api_class_id, class_node


def create_package_node_from_mysql(j, lib_node, result1):
    api_package_id = result1[j][0]
    api_package_name = result1[j][1]
    api_package_first_version = result1[j][2]
    api_package_doc_website = result1[j][4]
    api_package_description = result1[j][8]
    print api_package_id, "     ", api_package_name
    api_package_description = clean_html_text(api_package_description)
    package_node = NodeBuilder(). \
        add_label("api"). \
        add_label("java package"). \
        add_one_property("name", api_package_name). \
        add_one_property("package name", api_package_name). \
        add_one_property("first version", api_package_first_version). \
        add_one_property("api document website", api_package_doc_website). \
        add_one_property("description", api_package_description). \
        build()
    # insert package to neo4j
    connect_graph.merge(package_node)
    ## connect_graph.merge(Relationship(package_node, 'instance of', node2package))
    connect_graph.merge(Relationship(package_node, 'belong to', lib_node))
    return api_package_id, package_node


def create_library_node_from_mysql(i, node1lib, result):
    library_id = result[i][0]
    library_name = result[i][1]
    library_orgnization = result[i][2]
    library_version = result[i][3]
    library_doc_website = result[i][4]
    print library_id
    lib_node = NodeBuilder(). \
        add_label("api"). \
        add_label("java library"). \
        add_one_property("name", library_name). \
        add_one_property("library name", library_name). \
        add_one_property("version", library_version). \
        add_one_property("api document website", library_doc_website). \
        add_one_property("organization", library_orgnization). \
        build()
    # insert lib to neo4j
    connect_graph.merge(lib_node)
    connect_graph.merge(Relationship(lib_node, 'instance of', node1lib))
    connect_graph.merge(Relationship(lib_node, 'version', node1lib))
    return lib_node, library_id


# write into neo4j
def schema_builder():
    node1 = Node("schema", "entity", name="Java software library", wd_item_id='Q21127166')
    connect_graph.merge(node1)
    node2 = Node("schema", "entity", name="java package")
    connect_graph.merge(node2)
    class_node = Node("schema", "entity", name="java class")
    connect_graph.merge(class_node)
    node4 = Node("schema", "entity", name="java method")
    connect_graph.merge(node4)
    node5 = Node("schema", "entity", name="java field")
    connect_graph.merge(node5)
    method_parameter_node = Node("schema", "entity", name="java method parameter")
    connect_graph.merge(method_parameter_node)

    exception_node = Node("schema", "entity", name="java exception")
    connect_graph.merge(exception_node)
    throw_exception_description_node = Node("schema", "entity", name="java throw exception description")
    connect_graph.merge(throw_exception_description_node)

    connect_graph.merge(Relationship(node2, 'belong to', node1))
    connect_graph.merge(Relationship(class_node, 'belong to', node2))
    connect_graph.merge(Relationship(node4, 'belong to', class_node))
    connect_graph.merge(Relationship(node5, 'belong to', class_node))
    connect_graph.merge(Relationship(method_parameter_node, 'belong to', node4))

    connect_graph.merge(Relationship(method_parameter_node, 'parameter type', class_node))
    connect_graph.merge(Relationship(class_node, 'return value type', class_node))
    connect_graph.merge(Relationship(method_parameter_node, 'throw', exception_node))
    connect_graph.merge(
        Relationship(method_parameter_node, 'throw exception description', throw_exception_description_node))

    node7 = Node("schema", "entity", name="package")
    connect_graph.merge(node7)
    connect_graph.merge(Relationship(node2, 'subclass of', node7))
    node8 = Node("schema", "entity", name="class")
    connect_graph.merge(node8)
    connect_graph.merge(Relationship(class_node, 'subclass of', node8))
    node9 = Node("schema", "entity", name="method")
    connect_graph.merge(node9)
    connect_graph.merge(Relationship(node4, 'subclass of', node9))
    node10 = Node("schema", "entity", name="field")
    connect_graph.merge(node10)
    connect_graph.merge(Relationship(node5, 'subclass of', node10))
    node11 = Node("schema", "entity", name="method parameter")
    connect_graph.merge(node11)
    connect_graph.merge(Relationship(method_parameter_node, 'subclass of', node11))

    print "writing concept to neo4j completed!"


schema_builder()
mySQLReader(1, 2)
cur.close()
conn.close()
