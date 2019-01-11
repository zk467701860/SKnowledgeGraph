from db.importer import APIHTMLTextImport
from db.model import APIHTMLText

if __name__ == "__main__":
    # importer = APIHTMLTextImport(table="jdk_package", primary_key_name="package_id", html_column="description",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_SHORT_DESCRIPTION)
    # importer.start_import()
    #
    # importer = APIHTMLTextImport(table="jdk_package", primary_key_name="package_id", html_column="detail_description",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
    # importer.start_import()

    # importer = APIHTMLTextImport(table="jdk_class", primary_key_name="class_id", html_column="description",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_SHORT_DESCRIPTION)
    # importer.start_import()

    # importer = APIHTMLTextImport(table="jdk_class", primary_key_name="class_id", html_column="detail_description",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
    # importer.start_import()

    # importer = APIHTMLTextImport(table="jdk_method", primary_key_name="method_id", html_column="full_declaration",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_DECLARATION)
    # importer.start_import()
    #
    # importer = APIHTMLTextImport(table="jdk_method", primary_key_name="method_id", html_column="description",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
    # importer.start_import()
    #
    # importer = APIHTMLTextImport(table="jdk_method", primary_key_name="method_id", html_column="return_string",
    #                              html_text_type=APIHTMLText.HTML_TYPE_METHOD_RETURN_VALUE_DESCRIPTION)
    # importer.start_import()
    # importer = APIHTMLTextImport(table="androidAPI_package", primary_key_name="id",
    #                              html_column="short_description_label",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_SHORT_DESCRIPTION)
    # importer.start_import()
    # importer = APIHTMLTextImport(table="androidAPI_package", primary_key_name="id",
    #                              html_column="long_description_label",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
    # importer.start_import()

    # importer = APIHTMLTextImport(table="androidAPI_class", primary_key_name="id", html_column="short_description_label",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_SHORT_DESCRIPTION)
    # importer.start_import()
    # importer = APIHTMLTextImport(table="androidAPI_class", primary_key_name="id", html_column="long_description_label",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
    # importer.start_import()

    importer = APIHTMLTextImport(table="androidAPI_method", primary_key_name="id",
                                 html_column="short_description_label",
                                 html_text_type=APIHTMLText.HTML_TYPE_API_SHORT_DESCRIPTION)
    importer.start_import()
    importer = APIHTMLTextImport(table="androidAPI_method", primary_key_name="id", html_column="long_description_label",
                                 html_text_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
    importer.start_import()

    # importer = APIHTMLTextImport(table="androidAPI_support_package", primary_key_name="id",
    #                              html_column="short_description_label",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_SHORT_DESCRIPTION)
    # importer.start_import()
    # importer = APIHTMLTextImport(table="androidAPI_support_package", primary_key_name="id",
    #                              html_column="long_description_label",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
    # importer.start_import()
    #
    # importer = APIHTMLTextImport(table="androidAPI_support_class", primary_key_name="id",
    #                              html_column="short_description_label",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_SHORT_DESCRIPTION)
    # importer.start_import()
    # importer = APIHTMLTextImport(table="androidAPI_support_class", primary_key_name="id",
    #                              html_column="long_description_label",
    #                              html_text_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
    # importer.start_import()

    '''
    #todo android method api haven been import into API ALL ENTITY TABLE
    importer = APIHTMLTextImport(table="androidAPI_support_method", primary_key_name="id",
                                 html_column="short_description_label",
                                 html_text_type=APIHTMLText.HTML_TYPE_API_SHORT_DESCRIPTION)
    importer.start_import()
    importer = APIHTMLTextImport(table="androidAPI_support_method", primary_key_name="id", html_column="long_description_label",
                                 html_text_type=APIHTMLText.HTML_TYPE_API_DETAIL_DESCRIPTION)
    importer.start_import()

    '''
