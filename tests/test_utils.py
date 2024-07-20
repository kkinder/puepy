import unittest
from xml.dom import getDOMImplementation

from puepy.util import merge_classes, _extract_event_handlers, patch_dom_element
from .dom_tools import node_to_dict


class TestMergeClasses(unittest.TestCase):
    def test_single_str_input(self):
        result = merge_classes("class1")
        self.assertSetEqual(result, {"class1"})

    def test_multiple_str_input(self):
        result = merge_classes("class1 class2")
        self.assertSetEqual(result, {"class1", "class2"})

    def test_multiple_different_input(self):
        result = merge_classes("class1", ["class2", "class3"])
        self.assertSetEqual(result, {"class1", "class2", "class3"})

    def test_dict_input_true_values(self):
        result = merge_classes({"class1": True, "class2": True})
        self.assertSetEqual(result, {"class1", "class2"})

    def test_dict_input_false_values(self):
        result = merge_classes({"class1": False, "class2": False})
        self.assertSetEqual(result, set())

    def test_dict_input_mixed_values(self):
        result = merge_classes({"class1": True, "class2": False})
        self.assertSetEqual(result, {"class1"})

    def test_exclude_class(self):
        result = merge_classes("/class1", "class1 class2")
        self.assertEqual(result, {"class2"})

    def test_none_input(self):
        result = merge_classes(None)
        self.assertSetEqual(result, set())

    def test_class_list_input(self):
        result = merge_classes(("class1", "class2"))
        self.assertSetEqual(result, {"class1", "class2"})


class TestExtractEventHandlers(unittest.TestCase):
    def test_extract_event_handlers(self):
        kwargs = {"on_click": "click", "on_hover": "hover", "not_event": "value"}
        result = _extract_event_handlers(kwargs)

        # check correct extracted event handlers
        self.assertDictEqual(result, {"click": "click", "hover": "hover"})

        # check correct kwargs pair left
        self.assertDictEqual(kwargs, {"not_event": "value"})

        # edge case: no events to extract
        kwargs = {"key1": "value1", "key2": "value2"}
        result = _extract_event_handlers(kwargs)
        self.assertEqual(result, {})

        # check kwargs is still same when no events are extracted
        self.assertDictEqual(kwargs, {"key1": "value1", "key2": "value2"})


class TestPatchDomElement(unittest.TestCase):
    def setUp(self):
        self.impl = getDOMImplementation()
        self.doctype = self.impl.createDocumentType("html", None, None)
        self.document = self.impl.createDocument(None, "html", self.doctype)
        self.html = self.document.documentElement

    def test_patch_dom_element(self):
        starting_ul = self._build_list(self.document)
        self.html.appendChild(starting_ul)
        p1 = self.document.createElement("p")
        p1.appendChild(self.document.createTextNode("This should persist"))
        self.html.appendChild(p1)

        self.assertDictEqual(
            node_to_dict(self.html),
            {
                "attributes": {},
                "children": [
                    {
                        "attributes": {"attr-a": "attr1"},
                        "children": [
                            {
                                "attributes": {"attr-0": "attr0"},
                                "children": [{"text": "Text 0", "type": "#text"}],
                                "type": "li",
                            },
                            {
                                "attributes": {"attr-1": "attr1"},
                                "children": [{"text": "Text 1", "type": "#text"}],
                                "type": "li",
                            },
                            {
                                "attributes": {"attr-2": "attr2"},
                                "children": [{"text": "Text 2", "type": "#text"}],
                                "type": "li",
                            },
                        ],
                        "type": "ul",
                    },
                    {"attributes": {}, "children": [{"text": "This should persist", "type": "#text"}], "type": "p"},
                ],
                "type": "html",
            },
        )

        # Make it bigger
        patch_dom_element(self._build_list(self.document, size=4), starting_ul)
        self.assertDictEqual(
            node_to_dict(self.html),
            {
                "attributes": {},
                "children": [
                    {
                        "attributes": {"attr-a": "attr1"},
                        "children": [
                            {
                                "attributes": {"attr-0": "attr0"},
                                "children": [{"text": "Text 0", "type": "#text"}],
                                "type": "li",
                            },
                            {
                                "attributes": {"attr-1": "attr1"},
                                "children": [{"text": "Text 1", "type": "#text"}],
                                "type": "li",
                            },
                            {
                                "attributes": {"attr-2": "attr2"},
                                "children": [{"text": "Text 2", "type": "#text"}],
                                "type": "li",
                            },
                            {
                                "attributes": {"attr-3": "attr3"},
                                "children": [{"text": "Text 3", "type": "#text"}],
                                "type": "li",
                            },
                        ],
                        "type": "ul",
                    },
                    {"attributes": {}, "children": [{"text": "This should persist", "type": "#text"}], "type": "p"},
                ],
                "type": "html",
            },
        )

        # Now shorter
        patch_dom_element(self._build_list(self.document, size=2), starting_ul)

        self.assertDictEqual(
            node_to_dict(self.html),
            {
                "attributes": {},
                "children": [
                    {
                        "attributes": {"attr-a": "attr1"},
                        "children": [
                            {
                                "attributes": {"attr-0": "attr0"},
                                "children": [{"text": "Text 0", "type": "#text"}],
                                "type": "li",
                            },
                            {
                                "attributes": {"attr-1": "attr1"},
                                "children": [{"text": "Text 1", "type": "#text"}],
                                "type": "li",
                            },
                        ],
                        "type": "ul",
                    },
                    {"attributes": {}, "children": [{"text": "This should persist", "type": "#text"}], "type": "p"},
                ],
                "type": "html",
            },
        )

    def test_change_attributes(self):
        div = self.document.createElement("div")
        p = self.document.createElement("p")
        p.setAttribute("class", "test")
        div.appendChild(p)
        self.html.appendChild(div)

        self.assertDictEqual(
            node_to_dict(self.html),
            {
                "attributes": {},
                "children": [
                    {"attributes": {}, "children": [{"attributes": {"class": "test"}, "type": "p"}], "type": "div"}
                ],
                "type": "html",
            },
        )

        new_div = self.document.createElement("div")
        new_p = self.document.createElement("p")
        new_p.setAttribute("test", "1")
        new_div.appendChild(new_p)

        patch_dom_element(new_div, div)

        x = node_to_dict(self.html)

        self.assertDictEqual(
            node_to_dict(self.html),
            {
                "attributes": {},
                "children": [
                    {"attributes": {}, "children": [{"attributes": {"test": "1"}, "type": "p"}], "type": "div"}
                ],
                "type": "html",
            },
        )

    def test_replace_element(self):
        div = self.document.createElement("div")
        p = self.document.createElement("p")
        p.setAttribute("class", "test")
        div.appendChild(p)
        self.html.appendChild(div)

        self.assertDictEqual(
            node_to_dict(self.html),
            {
                "attributes": {},
                "children": [
                    {
                        "attributes": {},
                        "children": [{"attributes": {"class": "test"}, "type": "p"}],
                        "type": "div",
                    }
                ],
                "type": "html",
            },
        )

        new_div = self.document.createElement("div")
        new_e = self.document.createElement("b")
        new_div.appendChild(new_e)

        patch_dom_element(new_div, div)

        self.assertDictEqual(
            node_to_dict(self.html),
            {
                "attributes": {},
                "children": [
                    {
                        "attributes": {},
                        "children": [{"attributes": {}, "type": "b"}],
                        "type": "div",
                    }
                ],
                "type": "html",
            },
        )

    def _build_list(self, document, size=3):
        starting_ul = document.createElement("ul")
        starting_ul.setAttribute("attr-a", "attr1")
        for i in range(size):
            li = document.createElement("li")
            li.setAttribute(f"attr-{i}", f"attr{i}")
            t = document.createTextNode(f"Text {i}")
            li.appendChild(t)
            starting_ul.appendChild(li)
        return starting_ul


if __name__ == "__main__":
    unittest.main()
