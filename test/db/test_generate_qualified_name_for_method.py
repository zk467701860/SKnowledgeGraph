#!/usr/bin/python
# -*- coding: UTF-8 -*-
from unittest import TestCase

from script.db.jdk_importer.import_jdk_for_method import generate_qualified_name_for_method


class Test_generate_qualified_name_for_method(TestCase):
    def test_generate_qualified_name_for_method(self):
        simple_method_name = "BasicStroke"
        api_full_declaration_html = '<pre><a href="../../java/beans/ConstructorProperties.html" title="annotation in java.beans">@ConstructorProperties</a>public BasicStroke(float width,int cap,int join,float miterlimit,float[] dash,float dash_phase)</pre>'
        parent_class_id = 27
        expected = "java.awt.BasicStroke.BasicStroke(float,int,int,float,float[],float)"
        result = generate_qualified_name_for_method(simple_method_name=simple_method_name, api_full_declaration_html=api_full_declaration_html, parent_class_id=parent_class_id)
        self.assertEqual(result, expected)


    def test_generate_qualified_name_for_method_2(self):
        simple_method_name = "removeLayoutComponent"
        api_full_declaration_html = '<pre>void removeLayoutComponent(<a href="../../java/awt/Component.html" title="class in java.awt">Component</a> comp)</pre>'
        parent_class_id = 12
        expected = "java.awt.LayoutManager.removeLayoutComponent(java.awt.Component)"
        result = generate_qualified_name_for_method(simple_method_name=simple_method_name, api_full_declaration_html=api_full_declaration_html, parent_class_id=parent_class_id)
        self.assertEqual(result, expected)

    def test_get_simple_method_name_qualifier_type(self):
        simple_method_name = "removeLayoutComponent"
        api_full_declaration_html = '<pre>void removeLayoutComponent(<a href="../../java/awt/Component.html" title="class in java.awt">Component</a> comp)</pre>'
