## fast linkd的别名统计信息tsv生成

从html的纯文本统计别名在全文中出现的次数,生成tsv文件，
同时也会对alias_link.json统计出来的别名进行处理。目前做的处理有分词，全部变成小写，去掉开头结尾的空格。
运行脚本 start_count_alias.py

输入：
```
data/alias_link.json
data/html.json
```

输出：
```
data/normalize_alias_link.json
data/alias-entity-count.tsv
```

## java, android以及android guide网页爬取和(alias, link)计数
prepare_data_java.py 从[java官方文档](https://docs.oracle.com/javase/8/docs/api/)上爬取主要的html文本，清理后以{html, clean_text}的列表存在raw_data_java/html.json中;将HTML中的<a>标签所包含的文本作为alias，href属性作为link，并对所有文档的(alias, link)对进行计数，以{alias, link, count}的列表存在alias_link.json中，在根据url是否为文档内部链接分成inner_alias_link.json和outer_alias_link.json中。
prepare_data_android.py和android_guide.py功能类似，分别从android文档[reference](https://developer.android.com/reference/)和[guide](https://developer.android.com/guide/)爬取数据。分别存到raw_data_android以及raw_data_guide中


