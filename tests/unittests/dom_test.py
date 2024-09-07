import unittest
from xml.dom import getDOMImplementation, Node

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

    def remove_ids_from_elements(self, element):
        """
        Recursively remove 'id' attributes from all elements in the given XML DOM element.
        """
        if element.hasAttribute("id"):
            element.removeAttribute("id")

        for child in element.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                self.remove_ids_from_elements(child)
