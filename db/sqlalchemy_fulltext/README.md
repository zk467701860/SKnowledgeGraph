## 说明
这个项目是github上找的对于全文索引的支持
https://github.com/mengzhuo/sqlalchemy-fulltext-search

## 

SQLAlchemy-FullText-Search
==========================


Fulltext search support with MySQL & SQLAlchemy

Examples:

Default

```

    from sqlalchemy_fulltext import FullText, FullTextSearch
    class Foo(FullText, Base):
        __fulltext_columns__ = ('spam', 'ham')

    session.query(Foo).filter(FullTextSearch('Spam', Foo))
```
Using "IN BOOLEAN MODE":

```

    from sqlalchemy_fulltext import FullText, FullTextSearch
    import sqlalchemy_fulltext.modes as FullTextMode
    class Foo(FullText, Base):
        __fulltext_columns__ = ('spam', 'ham')

    session.query(Foo).filter(FullTextSearch('Spam', Foo, FullTextMode.BOOLEAN))
```
Using "IN NATURAL LANGUAGE MODE":

```

    from sqlalchemy_fulltext import FullText, FullTextSearch
    import sqlalchemy_fulltext.modes as FullTextMode
    class Foo(FullText, Base):
        __fulltext_columns__ = ('spam', 'ham')

    session.query(Foo).filter(FullTextSearch('Spam', Foo, FullTextMode.NATURAL))
```
Using "WITH QUERY EXPANSION"

```
    from sqlalchemy_fulltext import FullText, FullTextSearch
    import sqlalchemy_fulltext.modes as FullTextMode
    class Foo(FullText, Base):
        __fulltext_columns__ = ('spam', 'ham')

    session.query(Foo).filter(FullTextSearch('Spam', Foo, FullTextMode.QUERY_EXPANSION))
```

