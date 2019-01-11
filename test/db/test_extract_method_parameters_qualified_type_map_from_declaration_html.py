#!/usr/bin/python
# -*- coding: UTF-8 -*-
from unittest import TestCase

from db.util.code_text_process import extract_method_parameters_qualified_type_map_from_declaration_html, \
    parse_declaration_html_with_full_qualified_type


class TestExtract_method_parameters_qualified_type_map_from_declaration_html(TestCase):
    def test_extract_method_parameters_qualified_type_map_from_declaration_html(self):
        examples = [
            (
                u'''<pre><a href="../../java/applet/Applet.html" title="class in java.applet">Applet</a> getApplet(<a href="../../java/lang/String.html" title="class in java.lang">String</a> name)</pre>''',
                {"Applet": "java.applet.Applet",
                 "String": "java.lang.String"}),
        ]

        for example in examples:
            result = extract_method_parameters_qualified_type_map_from_declaration_html(example[0])
            self.assertEqual(result, example[1])

    def test_parse_declaration_html_with_full_qualified_type(self):
        examples = [
            (
                u'''<pre><a href="../../java/applet/Applet.html" title="class in java.applet">Applet</a> getApplet(<a href="../../java/lang/String.html" title="class in java.lang">String</a> name)</pre>''',
                u'''java.applet.Applet getApplet(java.lang.String name)'''),
            (
                u'''<pre>public <a href="../../java/awt/Point.html" title="class in java.awt">Point</a> getLocation()</pre>''',
                u'''public java.awt.Point getLocation()'''),

            (
                u'''<pre>public\xa0<a href="../../java/awt/event/ActionListener.html" title="interface in java.awt.event">ActionListener</a>[]\xa0getActionListeners()</pre>''',
                u'''public java.awt.event.ActionListener[] getActionListeners()''')
        ]

        for example in examples:
            result = parse_declaration_html_with_full_qualified_type(example[0])
            self.assertEqual(result, example[1])
