from unittest import TestCase

from fusion.cross_source_fusion import CrossDataSourceFusion


class TestCrossDataSourceFusion(TestCase):
    def test_get_fusion_result_for_one_domain_entity(self):
        fusion = CrossDataSourceFusion()
        fusion.init()
        result = fusion.get_fusion_result_for_one_domain_entity(507853, "apk file")
        print(result)
    def test_get_fusion_result_for_illgal_char(self):
        fusion = CrossDataSourceFusion()
        fusion.init()
        result = fusion.get_fusion_result_for_one_domain_entity(507853, "*.jar")
        print(result)