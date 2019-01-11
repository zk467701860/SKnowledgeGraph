from db.engine_factory import EngineFactory
from db.model import DomainEntity, DomainEntityExtractFromSentenceRelation


def delete_domain_entity_and_relation_to_sentence(session, domain_entity):
    relation_list = DomainEntityExtractFromSentenceRelation.get_all_relation_by_domain_entity_id(session=session,
                                                                                                 domain_entity_id=domain_entity.id)
    print("delete relation num=%d" % len(relation_list))

    for r in relation_list:
        session.delete(r)
        print("delete relation id=%d" % r.id)
    session.commit()
    session.delete(domain_entity)
    session.commit()

def get_same_domain_entity_list(domain_entity_list):
    id_set = set([])
    result = []

    for index, domain_entity in enumerate(domain_entity_list):
        if index == len(domain_entity_list) - 1:
            break
        current_same_list = []
        if domain_entity.id in id_set:
            continue
        id_set.add(domain_entity.id)

        next_start_index = index + 1

        for other_domain_entity in domain_entity_list[next_start_index:]:
            if other_domain_entity.description == domain_entity.description:
                current_same_list.append(other_domain_entity)
                id_set.add(other_domain_entity.id)
        if current_same_list is not []:
            current_same_list.append(domain_entity)
            result.append(current_same_list)
    return result


def merge_domain_entity_and_relation(session, same_list):
    start_domain_entity = same_list[0]
    other_domain_entity_list = same_list[1:]

    print("merge name=%s id=%d" % (start_domain_entity.name, start_domain_entity.id))

    for other_domain_entity in other_domain_entity_list:
        relation_list = DomainEntityExtractFromSentenceRelation.get_all_relation_by_domain_entity_id(session=session,
                                                                                                     domain_entity_id=other_domain_entity.id)
        for r in relation_list:
            r.domain_entity_id = start_domain_entity.id
        session.commit()
        session.delete(other_domain_entity)
        session.commit()


def start_fix_duplicate_domain_entity():
    session = EngineFactory.create_session()
    domain_entity_name_list = DomainEntity.get_all_domain_entity_name_distinct(session)
    print("distinct name=%d" % len(domain_entity_name_list))
    for team_domain_entity in domain_entity_name_list:
        name = team_domain_entity.name
        print("current name=%s" % name)
        if len(name) <= 2:
            print("delete name=%s" % name)
            all_same_name_domain_entity_list = DomainEntity.get_all_domain_entity_with_same_name(session, name)
            for domain_entity in all_same_name_domain_entity_list:
                delete_domain_entity_and_relation_to_sentence(session=session, domain_entity=domain_entity)

            continue

        all_same_name_domain_entity_list = DomainEntity.get_all_domain_entity_with_same_name(session, name)
        same_list_of_list = get_same_domain_entity_list(all_same_name_domain_entity_list)
        for same_list in same_list_of_list:
            merge_domain_entity_and_relation(session=session, same_list=same_list)
        session.commit()
    session.commit()


if __name__ == "__main__":
    start_fix_duplicate_domain_entity()
