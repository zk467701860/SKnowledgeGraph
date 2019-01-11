from db.engine_factory import EngineFactory
from db.model import APIEntity, APIHTMLText


class ValueInstanceAPIHTMLTextImport:
    def __init__(self):
        self.session = None

    def start_import(self):
        self.session = EngineFactory.create_session()
        html_type = APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION

        api_entity_list = APIEntity.get_all_value_instance_api(session=self.session)
        for api_entity in api_entity_list:
            description = api_entity.short_description
            if description is None or description == "":
                continue
            api_html_entity = APIHTMLText(api_id=api_entity.id, html=description, html_type=html_type)
            api_html_entity.find_or_create(session=self.session, autocommit=False)
        self.session.commit()


if __name__ == "__main__":
    value_html_importer = ValueInstanceAPIHTMLTextImport()
    value_html_importer.start_import()
