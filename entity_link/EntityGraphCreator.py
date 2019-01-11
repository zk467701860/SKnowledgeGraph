import MySQLdb
if __name__ == "__main__":
    try:
        conn = MySQLdb.connect(host='10.141.221.73', user='root', passwd='root', port=3306, db='codehub',
                               charset='utf8')
        cur = conn.cursor()
    except MySQLdb.Error, e:
        print "Mysql connection Error %d: %s" % (e.args[0], e.args[1])
    try:
        sql = 'select start_api_id,end_api_id from java_api_relation'
        cur.execute(sql)
        data = cur.fetchall()
        print len(data)
        if data != ():
            with open("data/graph_input.edgelist", 'w') as write_f:
                for content in data:
                    write_f.writelines('%s %s\n'% (content[0], content[1]))
    except MySQLdb.Error, e:
        print "Mysql connection Error %d: %s" % (e.args[0], e.args[1])
        print "sql:  %s" % (sql)