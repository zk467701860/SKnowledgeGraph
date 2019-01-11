from db.engine_factory import EngineFactory
from db.model import APIEntity

if __name__ == "__main__":

    type_list = [
        {
            "name": "byte",
            "description": "byte is a keyword which designates the 8 bit signed integer primitive type. The java.lang.Byte class is the nominal wrapper class when you need to store a byte value but an object reference is required."},
        {
            "name": "char",
            "description": "char is a keyword. It defines a character primitive type. char can be created from character literals and numeric representation. Character literals consist of a single quote character (') (ASCII 39, hex 0x27), a single character, and a close quote ('), such as 'w'. Instead of a character, you can also use unicode escape sequences, but there must be exactly one."},
        {
            "name": "short",
            "description": "short is a keyword. It defines a 16 bit signed integer primitive type."},
        {
            "name": "int",
            "description": "int is a keyword which designates the 32 bit signed integer primitive type. The java.lang.Integer class is the nominal wrapper class when you need to store an int value but an object reference is required."
        }, {
            "name": "long",
            "description": "long is a keyword which designates the 64 bit signed integer primitive type. The java.lang.Long class is the nominal wrapper class when you need to store a long value but an object reference is required."},
        {
            "name": "float",
            "description": "float is a keyword which designates the 32 bit float primitive type. The java.lang.Float class is the nominal wrapper class when you need to store a float value but an object reference is required."},
        {
            "name": "double",
            "description": "double is a keyword which designates the 64 bit float primitive type. The java.lang.Double class is the nominal wrapper class when you need to store a double value but an object reference is required."},
        {
            "name": "boolean",
            "description": "boolean is a keyword which designates the boolean primitive type. There are only two possible boolean values: true and false. The default value for boolean fields is false."},

        {
            "name": "void",
            "description": "void is a Java keyword. Used at method declaration and definition to specify that the method does not return any type, the method returns void. It is not a type and there is no void references/pointers as in C/C++."},

    ]
    session = EngineFactory.create_session()

    for item in type_list:
        api_entity = APIEntity(qualified_name=item["name"], api_type=APIEntity.API_TYPE_PRIMARY_TYPE,
                               short_description=item["description"])
        print(api_entity)
        api_entity.find_or_create(session=session)
        print(api_entity)