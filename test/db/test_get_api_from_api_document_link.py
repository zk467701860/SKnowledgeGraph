from unittest import TestCase

from db.util.code_text_process import get_api_qualifier_name_from_api_document_link


class TestGet_api_from_api_document_link(TestCase):
    def test_get_api_from_api_document_link(self):
        examples = [
            (u"../../java/applet/Applet.html", u"java.applet.Applet"),
            (u"../../java/lang/String.html", u"java.lang.String"),
            (u"../../java/lang/Character.UnicodeBlock.html", u"java.lang.Character.UnicodeBlock")
        ]

        for example in examples:
            result = get_api_qualifier_name_from_api_document_link(example[0])
            self.assertEqual(result, example[1])
