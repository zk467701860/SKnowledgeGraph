1. index on entity, name
2. index on wikidata, wd_item_id
3. index on entity `Stack Exchange tag`
CREATE INDEX ON :entity(`Stack Exchange tag`)
CREATE INDEX ON :wikidata(`Stack Exchange tag`)
CREATE INDEX ON :entity(`Stack Overflow tag url`)
CREATE INDEX ON :`so tag`(`Stack Overflow tag url`)
CREATE INDEX ON :entity(name)
CREATE INDEX ON :entity(`site:enwiki`)