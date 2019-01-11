#!/usr/bin/python
# -*- coding: UTF-8 -*-

from unittest import TestCase

from db.util.code_text_process import clean_html_text_with_format, clean_html_text


class TestClean_html_text_with_format(TestCase):
    def test_clean_html_text_with_format(self):
        examples = [u'''<div class="block">Prints out a list, starting at the specified indentation, to the
 specified print stream.</div>''', u'''<div class="block"><span class="deprecatedLabel">Deprecated.</span> <span class="deprecationComment">As of JDK version 1.1,
 replaced by processFocusEvent(FocusEvent).</span></div>''', u'''<div class="block">The user has pressed the mouse button. The <code>ALT_MASK</code>
 flag indicates that the middle button has been pressed.
 The <code>META_MASK</code>flag indicates that the
 right button has been pressed.</div>''', u'''<div class="block">Gets the URL of the document in which the applet is embedded.
 For example, suppose an applet is contained
 within the document:
 <blockquote><pre>
    http://www.oracle.com/technetwork/java/index.html
 </pre></blockquote>
 The document base is:
 <blockquote><pre>
    http://www.oracle.com/technetwork/java/index.html
 </pre></blockquote></div>''', u'''<div class="block">Returns the value of the named parameter in the HTML tag. For
 example, if an applet is specified as
 <blockquote><pre>
 &lt;applet code="Clock" width=50 height=50&gt;
 &lt;param name=Color value="blue"&gt;
 &lt;/applet&gt;
 </pre></blockquote>
 <p>
 then a call to <code>getParameter("Color")</code> returns the
 value <code>"blue"</code>.</p></div>''', u'''<div class="block">Constructs a new Applet.
 <p>
 Note: Many methods in <code>java.applet.Applet</code>
 may be invoked by the applet only after the applet is
 fully constructed; applet should avoid calling methods
 in <code>java.applet.Applet</code> in the constructor.</p></div>''', u'''<div class="block">Called by the browser or applet viewer to inform
 this applet that it should stop its execution. It is called when
 the Web page that contains this applet has been replaced by
 another page, and also just before the applet is to be destroyed.
 <p>
 A subclass of <code>Applet</code> should override this method if
 it has any operation that it wants to perform each time the Web
 page containing it is no longer visible. For example, an applet
 with animation might want to use the <code>start</code> method to
 resume animation, and the <code>stop</code> method to suspend the
 animation.
 </p><p>
 The implementation of this method provided by the
 <code>Applet</code> class does nothing.</p></div>''']
        for example in examples:
            self.print_compare(example)

    def print_compare(self, html):
        # print html
        old_text = clean_html_text(html)
        print "old text: "

        print old_text
        text = clean_html_text_with_format(html)
        print "new method text: "
        print text
