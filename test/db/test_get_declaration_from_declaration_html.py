
from unittest import TestCase

from bs4 import BeautifulSoup


class TestGet_declaration_from_declaration_html(TestCase):
    def test_get_declaration_html(self):
        declaration_html='''

        <tr class="api apilevel-8" data-version-added="8">
        <td><code>





                void</code>
        </td>
        <td width="100%">
        <code>
        <a href="https://developer.android.google.cn/reference/javax/xml/transform/stream/StreamResult.html#setOutputStream(java.io.OutputStream)">setOutputStream</a>(<a href="https://developer.android.google.cn/reference/java/io/OutputStream.html">OutputStream</a> outputStream)
              </code>
        <p>Set the ByteStream that is to be written to.


        </p>
        </td>
        </tr>
        '''
        soup = BeautifulSoup(declaration_html, "lxml")
        p_list = soup.find_all(name=["p", ])

        for p in p_list:
            p.decompose()

        soup.prettify()
        print(str(soup))
        print(soup.get_text())