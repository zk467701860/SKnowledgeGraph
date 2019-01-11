## 建立全文索引
1. alias
```
CREATE FULLTEXT INDEX full_text_alias ON `java_api_alias` (`alias`);
```
2. so post title
```
CREATE FULLTEXT INDEX full_text_title ON `posts` (`title`);
```