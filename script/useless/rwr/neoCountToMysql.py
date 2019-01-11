import MySQLdb

from skgraph.graph.accessor.graph_accessor import DefaultGraphAccessor, GraphClient

conn= MySQLdb.connect(
        host='10.141.221.75',
        port = 3306,
        user='root',
        passwd='root',
        db ='graphApplication',
        charset='utf8'
        )

class CountImporter:
    def __init__(self, client, max_id):
        self.client = client
        self.max_id = max_id

    def insert_to_mysql(self):
        cur = conn.cursor()
        index = 0
        count_list = []
        for i in range(40374, self.max_id + 1):
            #print 'begin get %d  connect edge' %(i)
            result = self.client.get_all_connection_edge_by_id(i)
            for n in result:
                if n[0] != None:
                    content = (i, n[1]['link_id'], n[0])
                    count_list.append(content)
            #print 'end get %d  connect edge, edge number : %d' %(i, len(count_list))
            index += 1
            if index == 100:
                if count_list != []:
                    sql = 'insert into randomWalkCount(startID,endID,count) values(%s,%s,%s)'
                    try:
                        print 'begin insert %d, number: %d' % (i,len(count_list))
                        cur.executemany(sql, count_list)
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        print('MySQL: %s   error:%s' % (sql, e))
                index = 0
                count_list = []
        if count_list != []:
            sql = 'insert into randomWalkCount(startID,endID,count) values(%s,%s,%s)'
            try:
                print 'begin insert %d, number: %d' % (i, len(count_list))
                cur.executemany(sql, count_list)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print('MySQL: %s   error:%s' % (sql, e))
            cur.close()
            conn.close()

if __name__ == '__main__':
    client = DefaultGraphAccessor(GraphClient(server_number=1))
    importer = CountImporter(client, 92354)
    importer.insert_to_mysql()