from unittest import TestCase

from skgraph.graph.label_util import LabelUtil


class TestLabelUtil(TestCase):
    def setUp(self):
        self.labelUtil = LabelUtil()

    def test_get_all_public_label_json_list(self):
        labels = self.labelUtil.get_all_public_label_json_list()

        self.assertEqual(len(labels), 15)
        print(labels)

        labels = self.labelUtil.get_all_public_label_name_list()

        self.assertEqual(len(labels), 15)
        print(labels)

    def test_get_public_label_object_by_name(self):
        label = self.labelUtil.get_public_label_object_by_name("API Class")
        self.assertIsNotNone(label)
        print(label)
        label = self.labelUtil.get_public_label_object_by_name("api")
        self.assertIsNone(label)
        print(label)

    def test_get_private_label_object_by_name(self):
        label = self.labelUtil.get_private_label_object_by_name("API Class")
        self.assertIsNone(label)
        print(label)
        label = self.labelUtil.get_private_label_object_by_name("api")
        self.assertIsNotNone(label)
        print(label)

    def test_filter_labels_set_to_public_label_string_list(self):
        labels = self.labelUtil.filter_labels_set_to_public_label_string_list(
            ["wikidata", "background knowledge", "entity"])
        self.assertEqual(labels, ["Background Knowledge"])
        print(labels)

        labels = self.labelUtil.filter_labels_set_to_public_label_string_list(["entity", ])
        self.assertEqual(labels, ['Descriptive Knowledge'])
        print(labels)

        labels = self.labelUtil.filter_labels_set_to_public_label_string_list(["awesome item","background knowledge", "entity","wikidata","software" ])
        self.assertEqual(labels, [u'Library', u'Background Knowledge'])
        print(labels)

        labels = self.labelUtil.filter_labels_set_to_public_label_string_list(
            ["java constructor", "java method", "entity", "entity","api"])
        self.assertEqual(labels, [u'API Method'])
        print(labels)

        labels = self.labelUtil.filter_labels_set_to_public_label_string_list(
            ["background knowledge", "programming language", "software", "entity", "wikidata"])
        self.assertEqual(labels, [u'Programming Language','Background Knowledge'])
        print(labels)