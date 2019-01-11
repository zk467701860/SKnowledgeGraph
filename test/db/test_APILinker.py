from unittest import TestCase

from db.api_linker import APILinker


class TestAPILinker(TestCase):
    def __try_test_for_test_case(self, linker, test_datas):
        for test_case in test_datas:
            print "api_name=", test_case[0]
            link_result = linker.link(api_name=test_case[0], context=test_case[1])
            print "link_result", link_result
            self.assertEqual(test_case[2], link_result)

    def test_link(self):
        linker = APILinker()

        test_datas = [
            ("androidXxx", None, []),
            ("java.lang", None, [{'api_id': 17, 'api_qualifier_name': u'java.lang', 'probability': 1.0}]),
            ("ContainerListener", None, [{'api_id': 638,
                                          'api_qualifier_name': u'java.awt.event.ContainerListener',
                                          'probability': 1.0}]),
            ("ContainerListener()", None, [{'api_id': 638,
                                            'api_qualifier_name': u'java.awt.event.ContainerListener',
                                            'probability': 1.0}]),
            ("NUMERIC", None, [{'api_id': 23273,
                                'api_qualifier_name': u'java.sql.JDBCType.NUMERIC',
                                'probability': 0.5},
                               {'api_id': 23228,
                                'api_qualifier_name': u'java.sql.Types.NUMERIC',
                                'probability': 0.5}]),

        ]

        self.__try_test_for_test_case(linker, test_datas)

    def test_link_for_other_scorer(self):
        linker = APILinker()

        test_datas = [
            ("Button", {"api_type": "class"},
             [{'api_id': 489, 'api_qualifier_name': u'java.awt.Button', 'probability': 0.5},
              {'api_id': 7470,
               'api_qualifier_name': u'android.widget.Button',
               'probability': 0.5},
              ]),
            ("Button", {"api_type": "classes"},
             [{'api_id': 489,
               'api_qualifier_name': u'java.awt.Button',
               'probability': 0.4076949740823466},
              {'api_id': 7470,
               'api_qualifier_name': u'android.widget.Button',
               'probability': 0.4076949740823466},
              {'api_id': 9540,
               'api_qualifier_name': u'java.awt.Button.Button()',
               'probability': 0.09230502591765338},
              {'api_id': 9541,
               'api_qualifier_name': u'java.awt.Button.Button(java.lang.String)',
               'probability': 0.09230502591765338}]),

            ("java.lang", None, [{'api_id': 17, 'api_qualifier_name': u'java.lang', 'probability': 1.0}]),
            ("ContainerListener", None, [{'api_id': 638,
                                          'api_qualifier_name': u'java.awt.event.ContainerListener',
                                          'probability': 1.0}]),
        ]

        self.__try_test_for_test_case(linker, test_datas)

    def test_link_for_parameter_scorer(self):
        linker = APILinker()

        test_datas = [
            ("writeCharacters(String a)", None,
             [
                 {'api_qualifier_name': u'javax.xml.stream.XMLStreamWriter.writeCharacters(java.lang.String)',
                  'probability': 1.0, 'api_id': 50201},
             ]),
            ("writeCharacters(String a)", {"api_type": "Method"},
             [
                 {'api_qualifier_name': u'javax.xml.stream.XMLStreamWriter.writeCharacters(java.lang.String)',
                  'probability': 0.7083333333333334, 'api_id': 50201},
                 {'api_id': 50202,
                  'api_qualifier_name': u'javax.xml.stream.XMLStreamWriter.writeCharacters(char[],int,int)',
                  'probability': 0.2916666666666667}
             ]),

            ("writeCharacters(a, 5 ,7)", {"api_type": "Method"},
             [
                 {'api_id': 50202,
                  'api_qualifier_name': u'javax.xml.stream.XMLStreamWriter.writeCharacters(char[],int,int)',
                  'probability': 0.7083333333333334},
                 {'api_qualifier_name': u'javax.xml.stream.XMLStreamWriter.writeCharacters(java.lang.String)',
                  'probability': 0.2916666666666667, 'api_id': 50201},

             ])
        ]

        for test_case in test_datas:
            print "api_name=", test_case[0]
            link_result = linker.link(api_name=test_case[0], context=test_case[1])
            self.assertEqual(test_case[2], link_result)

    def test_link_for_parent_api_scorer(self):
        linker = APILinker()

        test_datas = [
            ("next()", {"parent_api": "XMLStreamReader"},
             [
                 {'api_qualifier_name': u'javax.xml.stream.XMLStreamReader.next()',
                  'probability': 1.0, 'api_id': 50185},
             ]),
            ("PipedReader(int)", {"parent_api": "java.io.PipedReader", "api_type": "method"},
             [
                 {'api_qualifier_name': u'java.io.PipedReader.PipedReader(int)', 'probability': 1.0, 'api_id': 16216}
                 ,
             ]),
            ("PipedReader(1)", {"parent_api": "java.io.PipedReader", "api_type": "method"},
             [{'api_id': 16216,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(int)',
               'probability': 0.28993610223642174},
              {'api_id': 16213,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter)',
               'probability': 0.28993610223642174},
              {'api_id': 16214,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter,int)',
               'probability': 0.21006389776357828},
              {'api_id': 16215,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader()',
               'probability': 0.21006389776357828}]),

        ]
        self.__try_test_for_test_case(linker, test_datas)

    def test_link_for_declaration_api_scorer(self):
        linker = APILinker()

        test_datas = [
            ("PipedReader(1)",
             {"declaration": "public PipedReader(int)"},
             [{'api_id': 16216,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(int)',
               'probability': 0.34666803103016086},
              {'api_id': 16213,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter)',
               'probability': 0.3036596690475811},
              {'api_qualifier_name': u'java.io.PipedReader', 'probability': 0.13791974539077737, 'api_id': 916},
              {'api_qualifier_name': u'java.io.PipedReader.PipedReader()', 'probability': 0.11946893444019631,
               'api_id': 16215},
              {'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter,int)',
               'probability': 0.0922836200912844, 'api_id': 16214}

              ]),
            ("PipedReader(1)",
             {"parent_api": "java.io.PipedReader", "api_type": "method", "declaration": "public PipedReader(int)"},
             [{'api_id': 16216,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(int)',
               'probability': 0.29250007826490276},
              {'api_id': 16213,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter)',
               'probability': 0.2785627006078126},
              {'api_id': 16215,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader()',
               'probability': 0.21887347481958588},
              {'api_id': 16214,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter,int)',
               'probability': 0.21006374630769872},
              ]),
            ("PipedReader",
             {"parent_api": "java.io.PipedReader", "api_type": "method", "declaration": "public PipedReader(int)"},
             [{'api_id': 16216,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(int)',
               'probability': 0.29250007826490276},
              {'api_id': 16213,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter)',
               'probability': 0.2785627006078126},
              {'api_id': 16215,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader()',
               'probability': 0.21887347481958588},
              {'api_id': 16214,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter,int)',
               'probability': 0.21006374630769872},
              ]),
            ("PipedReader",
             {"parent_api": "java.io.PipedReader", "declaration": "public PipedReader(int)"},
             [{'api_id': 16216,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(int)',
               'probability': 0.2859218683094209},
              {'api_id': 16213,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter)',
               'probability': 0.2699399485487908},
              {'api_id': 16215,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader()',
               'probability': 0.20149461825839096},
              {'api_id': 16214,
               'api_qualifier_name': u'java.io.PipedReader.PipedReader(java.io.PipedWriter,int)',
               'probability': 0.191392547578094},
              {'api_qualifier_name': u'java.io.PipedReader', 'probability': 0.05125101730530327, 'api_id': 916}

              ]),

            ("getInsets",
             {"parent_api": "javax.swing.UIDefaults", "declaration": "public Insets getInsets(Object key, Locale l)"},
             [{'api_qualifier_name': u'javax.swing.UIDefaults.getInsets(java.lang.Object,java.shared.Locale)',
               'probability': 0.3472586256050669, 'api_id': 41497},
              {'api_qualifier_name': u'javax.swing.UIDefaults.getInsets(java.lang.Object)',
               'probability': 0.24224806737442328, 'api_id': 41496},
              {'api_qualifier_name': u'javax.swing.UIManager.getInsets(java.lang.Object,java.shared.Locale)',
               'probability': 0.14585129179020834, 'api_id': 41540},
              {
                  'api_qualifier_name': u'javax.swing.plaf.nimbus.NimbusStyle.getInsets(javax.swing.plaf.synth.SynthContext,java.awt.Insets)',
                  'probability': 0.1325507799418825, 'api_id': 45107},
              {
                  'api_qualifier_name': u'javax.swing.plaf.synth.SynthStyle.getInsets(javax.swing.plaf.synth.SynthContext,java.awt.Insets)',
                  'probability': 0.13209123528841893, 'api_id': 45754}

              ]),
        ]

        self.__try_test_for_test_case(linker, test_datas)
