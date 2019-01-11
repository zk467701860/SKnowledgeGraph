
CREATE INDEX ON :entity(`source code repository`)
CREATE INDEX ON :entity(`official website`)
CREATE INDEX ON :entity(`url`)
CREATE INDEX ON :wikidata(`source code repository`)
CREATE INDEX ON :wikidata(`official website`)
CREATE INDEX ON :wikidata(`url`)
CREATE INDEX ON :`awesome item`(`url`)
CREATE INDEX ON :`awesome item`(`name`)

CREATE INDEX ON :`awesome list`(`url`)
CREATE INDEX ON :`awesome list`(`name`)

CREATE INDEX ON :`awesome category`(`name`)
CREATE INDEX ON :`awesome list topic`(`name`)
CREATE INDEX ON :entity(wd_item_id)
## add library concept label
MATCH (n:wikidata{`wd_item_id`:"Q188860"}) set n:`library concept` RETURN count(n)
MATCH (m:wikidata)-[r:`subclass of`]->(n:wikidata{`wd_item_id`:"Q188860"}) set m:`library concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`library concept`) set m:`library concept` RETURN count(m)

## add library label
MATCH (m:entity)-[r:`instance of`]->(n:`library concept`) set m:`library`  RETURN count(m)

## add software concept label
MATCH (n:wikidata{`wd_item_id`:"Q7397"}) set n:`software concept` RETURN count(n)

MATCH (m:wikidata)-[r:`subclass of`]->(n:wikidata{`wd_item_id`:"Q7397"}) set m:`software concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`software concept`) set m:`software concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`software concept`) set m:`software concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`software concept`) set m:`software concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`software concept`) set m:`software concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`software concept`) set m:`software concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`software concept`) set m:`software concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`software concept`) set m:`software concept` RETURN count(m)

## add software label
MATCH (m:entity)-[r:`instance of`]->(n:`software concept`) set m:`software`  RETURN count(m)

## add platform concept label
MATCH (n:wikidata{`wd_item_id`:"Q241317"}) set n:`platform concept` RETURN count(n)
MATCH (n:wikidata{`wd_item_id`:"Q9135"}) set n:`platform concept` RETURN count(n)

MATCH (m:wikidata)-[r:`subclass of`]->(n:`platform concept`) set m:`platform concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`platform concept`) set m:`platform concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`platform concept`) set m:`platform concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`platform concept`) set m:`platform concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`platform concept`) set m:`platform concept` RETURN count(m)

## add platform label
MATCH (m:entity)-[r:`instance of`]->(n:`platform concept`) set m:`platform`  RETURN count(m)


## add programming language concept label
MATCH (n:wikidata{`wd_item_id`:"Q9143"}) set n:`programming language concept` RETURN count(n)
MATCH (n:wikidata{`wd_item_id`:"Q629206"}) set n:`programming language concept` RETURN count(n)

MATCH (m:wikidata)-[r:`subclass of`]->(n:`programming language concept`) set m:`programming language concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`programming language concept`) set m:`programming language concept` RETURN count(m)
MATCH (m:wikidata)-[r:`subclass of`]->(n:`programming language concept`) set m:`programming language concept` RETURN count(m)

## add programming language label
MATCH (m:entity)-[r:`instance of`]->(n:`programming language concept`) set m:`programming language`  RETURN count(m)

# add background knowledge extraction label
MATCH (n:wikidata) set n:`background knowledge` RETURN count(n)
MATCH (n:`so tag`) set n:`background knowledge` RETURN count(n)
MATCH (n:`awesome list`) set n:`background knowledge` RETURN count(n)
MATCH (n:`awesome item`) set n:`background knowledge` RETURN count(n)
MATCH (n:`awesome category`) set n:`background knowledge` RETURN count(n)
