from unittest import TestCase

from db.alias_util import APIAliasGeneratorFactory
from db.model import APIAlias, APIEntity


class TestAPIAliasGenerate(TestCase):
    def test_get_method_qualifier_parameter_type(self):
        generator = APIAliasGeneratorFactory.create_generator(
            APIAlias.ALIAS_TYPE_SIMPLE_METHOD_WITH_QUALIFIER_PARAMETER_TYPE)
        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.addAttribute(java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String)",
                      "addAttribute(java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String)",
                      APIAlias.ALIAS_TYPE_SIMPLE_METHOD_WITH_QUALIFIER_PARAMETER_TYPE)

    def test_get_alias_name(self):
        generator = APIAliasGeneratorFactory.create_generator(
            APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_QUALIFIER_PARAMETER_TYPE)

        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.addAttribute(java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String)",
                      "Attributes2Impl.addAttribute(java.lang.String,java.lang.String,java.lang.String,java.lang.String,java.lang.String)",
                      APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_QUALIFIER_PARAMETER_TYPE)

    def test_get_simple_type_method_alias_name(self):
        alias_type = APIAlias.ALIAS_TYPE_SIMPLE_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE
        generator = APIAliasGeneratorFactory.create_generator(
            alias_type)
        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.addAttribute.drainTo(java.shared.Collection<? super java.shared.concurrent.PriorityBlockingQueue>)",
                      "drainTo(Collection<? super PriorityBlockingQueue>)",
                      alias_type)
        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.sort(T[],java.shared.Comparator<? super T>)",
                      "sort(T[],Comparator<? super T>)",
                      alias_type)
        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.compute(java.lang.Object,java.shared.function.BiFunction<? super,? super,? extends java.lang.Object>)",
                      "compute(Object,BiFunction<? super,? super,? extends Object>)",
                      alias_type)

        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.getBoolean(java.lang.String)",
                      "getBoolean(String)",
                      alias_type)
        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.createXMLStreamWriter(OutputStream,java.lang.String)",
                      "createXMLStreamWriter(OutputStream,String)",
                      alias_type)

    def test_get_simple_type_class_method_alias_name(self):
        alias_type = APIAlias.ALIAS_TYPE_SIMPLE_CLASS_NAME_METHOD_WITH_SIMPLE_PARAMETER_TYPE
        generator = APIAliasGeneratorFactory.create_generator(
            alias_type)
        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.drainTo(java.shared.Collection<? super java.shared.concurrent.PriorityBlockingQueue>)",
                      "Attributes2Impl.drainTo(Collection<? super PriorityBlockingQueue>)",
                      alias_type)
        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.sort(T[],java.shared.Comparator<? super T>)",
                      "Attributes2Impl.sort(T[],Comparator<? super T>)",
                      alias_type)
        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.compute(java.lang.Object,java.shared.function.BiFunction<? super,? super,? extends java.lang.Object>)",
                      "Attributes2Impl.compute(Object,BiFunction<? super,? super,? extends Object>)",
                      alias_type)

        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.getBoolean(java.lang.String)",
                      "Attributes2Impl.getBoolean(String)",
                      alias_type)
        self.one_name(generator,
                      "org.xml.sax.ext.Attributes2Impl.createXMLStreamWriter(OutputStream,java.lang.String)",
                      "Attributes2Impl.createXMLStreamWriter(OutputStream,String)",
                      alias_type)

    def test_get_camel_case_alias_name(self):
        alias_type = APIAlias.ALIAS_TYPE_CAMEL_CASE_TO_SPACE
        generator = APIAliasGeneratorFactory.create_generator(
            alias_type)

        examples = [
            (
                "org.xml.sax.ext.Attributes2Impl.drainTo(java.shared.Collection<? super java.shared.concurrent.PriorityBlockingQueue>)",
                "drain To"),
            ("org.xml.sax.ext.Attributes2Impl",
             "Attributes2 Impl"),
            ("Attributes2Impl.createXMLStreamWriter(OutputStream,String)",
             "create XML Stream Writer",),
            ("sort", None),
            ("java.lang.Object", None)]
        for example in examples:
            self.one_name(generator, example[0], example[1], alias_type)

    def one_name(self, generator, qualifier_name, right_answer, right_type):
        aliases = generator.generate_aliases(
            APIEntity(qualified_name=qualifier_name, api_type=APIEntity.API_TYPE_METHOD))
        print aliases
        if right_answer is not None:
            self.assertEqual(aliases[0].alias,
                             right_answer)
            self.assertEqual(aliases[0].type, right_type)
        else:
            self.assertEqual(aliases, [])
