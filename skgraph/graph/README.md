# 全文索引建立
```

apoc.index.addAllNodes('name',{label1:['prop1',...],...}, {options}) YIELD type, name, config

Call apoc.index.addAllNodes('entity',{`entity`:["name",'api_qualifier_name']})

Call apoc.index.addAllNodes('entity',{`entity`:["name",'api_qualifier_name'],`wikidata`:['name',"labels_en"]})

Call apoc.index.addAllNodes('library_function',{`awesome category`:["name"]})

Call apoc.index.addAllNodes('library_description',{`awesome item`:["name","description","descriptions_en"],`library`:["name","description","descriptions_en"]})
```
