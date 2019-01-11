## stopwards 的清理

```
match(n:entity)-[r]-(m:api) where ID(m)=107717 return n,r,m limit 50
```
有些节点名字是停用词，某些节点错误地连接到了这上面，需要删除


## fix bug
logger.exception()->logger.exception("------").
必须进行修复，否则项目会出现Bug