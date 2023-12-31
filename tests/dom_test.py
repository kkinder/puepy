import unittest
from xml.dom import getDOMImplementation

from puepy import core


class DomTest(unittest.TestCase):
    def setUp(self):
        self.setup_dom()

    def setup_dom(self):
        self.impl = getDOMImplementation()
        self.doctype = self.impl.createDocumentType(
            "html", "-//W3C//DTD HTML 4.01 Transitional//EN", "http://www.w3.org/TR/html4/loose.dtd"
        )
        self.document = self.impl.createDocument(None, "html", self.doctype)
        self.html = self.document.documentElement

        core.Tag.document = self.document
