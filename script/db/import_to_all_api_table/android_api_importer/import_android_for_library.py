from db.engine_factory import EngineFactory
from db.cursor_factory import ConnectionFactory
from db.model import LibraryEntity, KnowledgeTableRowMapRecord
from db.model_factory import KnowledgeTableFactory

cur = ConnectionFactory.create_cursor_for_jdk_importer()
session = EngineFactory.create_session()


def create_library_node_list():
    library_list = [
        {"library_name": "Android Platform APIs (API 27)",
         "version": "API level 27",
         "description": "Android provides a rich application framework that enables you to develop innovative applications and games for mobile devices in the Java language environment. Android Oreo is the 8th major release of the Android operating system. It was first released as a developer preview on October 25, 2017, with factory images for current Nexus and Pixel devices. A second developer preview was made available on November 27, 2017 for Nexus and Pixel devices, before the stable version was released on December 5, 2017.Android provides a rich application framework that enables you to develop innovative applications and games for mobile devices in the Java language environment.",
         "doc_website": "https://developer.android.com/reference/packages"
         },
        {"library_name": "Android Support Library",
         "version": "API level 27",
         "description": "Provides a variety of Android feature and utility APIs that are compatible with a wide range of platform versions.",
         "doc_website": "https://developer.android.com/reference/android/support/packages"
         },
    ]
    library_entity_list=[]
    for library_data in library_list:
        library_entity = LibraryEntity(name=library_data["library_name"], version=library_data["version"],
                                       short_description=library_data["description"], url=library_data["doc_website"])
        library_entity_list.append(library_entity)

    return library_entity_list


def import_all_android_library_version():

    library_entity_list=create_library_node_list()
    for lib_node in library_entity_list:
        lib_node = lib_node.find_or_create(session, autocommit=False)
    session.commit()
    "reading from mysql completed!"


import_all_android_library_version()
cur.close()
