import unittest
from unittest.mock import MagicMock

import pytest

from .dom_test import DomTest
from .dom_tools import node_to_dict
from puepy import core


class TestTag(DomTest):
    def setUp(self):
        super().setup_dom()

        self.page = core.Page()
        self.text_paragraph_sentence = "The quick brown fox."
        self.text_paragraph = core.Tag("div", "ref_div1", self.page, children=[self.text_paragraph_sentence])

    def test_render_simple(self):
        self.assertEqual(self.text_paragraph.children, [self.text_paragraph_sentence])
        self.assertEqual(
            node_to_dict(self.text_paragraph.render()),
            {
                "attributes": {"id": self.text_paragraph.element_id},
                "children": [{"text": "The quick brown fox.", "type": "#text"}],
                "type": "div",
            },
        )


class TestIntegration(DomTest):
    def setUp(self):
        super().setUp()

        t = core.t

        @t.component()
        class Card(core.Component):
            default_role = "card"
            props = ["help_text", core.Prop("show_buttons", "whether to show buttons", bool, False)]

            def populate(self):
                with t.div(classes="card-header"):
                    self.insert_slot("card-header")
                with t.div(classes="card-body"):
                    self.insert_slot()
                    if self.show_buttons:
                        with t.div(classes="card-footer"):
                            t.button("Button 1")
                            t.button("Button 2")

        class SimplePage(core.Page):
            def initial(self):
                return {"field1": "value1", "field2": "", "draw_card": True, "card_buttons": True}

            def on_card_buttons_change(self, new_value):
                self.on_card_buttons_change_called = [new_value]

            def populate(self):
                with t.body():
                    with t.div(classes="header"):
                        t.h1("This is h1 content")
                    with t.div(classes="main-content"):
                        t.p("This is a paragraph", escaped_attribute_="hi")
                        t.button("Test events", on_click=self.on_button_click, role="button")
                        with t.ul():
                            t.li("List Content 1")
                            t.li("List Content 2")
                            with t.ul():
                                t.li("Sublist Content 1")
                                t.li("Sublist Content 2")
                        if self.state["draw_card"]:
                            with t.card(show_buttons=self.state["card_buttons"]) as card:
                                with card.slot("card-header"):
                                    t("This is a header")
                                with card.slot():
                                    t("This is the card body")
                                    t.ul(t.li(t.strong("Bold")), t.li(t.em("Italic")))
                                    t("Or ", t.a("a link", href="https://www.example.com"))
                                    t.input(bind="field1", placeholder="Field 1 in Card")
                                    t.input(bind="field2", placeholder="Field 2 in Card")
                                    t.button("In-Slot Button", on_click=[self.on_card_button_click])
                    with t.form():
                        t.input(bind="field1", placeholder="Field 1")
                        t.input(bind="field2", placeholder="Field 2")

            def on_button_click(self, *args, **kwargs):
                pass

            def on_card_button_click(self, *args, **kwargs):
                pass

        self.page = SimplePage()

    def test_mount_and_redraw(self):
        self.page.mount(self.html)

        # Make sure it's mounted
        mounted_element = self.page.element

        # Change values
        self.page.state["field2"] = "New Value"
        self.page.state["card_buttons"] = False
        self.assertEqual(self.page.on_card_buttons_change_called, [False])
        self.page.redraw()

        # Remove the card
        self.page.state["draw_card"] = False
        self.remove_ids_from_elements(self.html)  # Useful to remove ids (which change) from the comparison
        without_draw = self.html.toxml()

        self.page.state["draw_card"] = True
        self.remove_ids_from_elements(self.html)
        with_draw = self.html.toxml()

        self.assertEqual(
            with_draw,
            '<html><div><body><div class="header"><h1>This is h1 content</h1></div><div class="main-content"><p escaped-attribute="hi">This is a paragraph</p><button role="button">Test events</button><ul><li>List Content 1</li><li>List Content 2</li><ul><li>Sublist Content 1</li><li>Sublist Content 2</li></ul></ul></div><form><input placeholder="Field 1" value="value1"/><input placeholder="Field 2" value="New Value"/></form></body></div></html>',
        )

        self.assertEqual(
            without_draw,
            '<html><div><body><div class="header"><h1>This is h1 content</h1></div><div class="main-content"><p escaped-attribute="hi">This is a paragraph</p><button role="button">Test events</button><ul><li>List Content 1</li><li>List Content 2</li><ul><li>Sublist Content 1</li><li>Sublist Content 2</li></ul></ul></div><form><input placeholder="Field 1" value="value1"/><input placeholder="Field 2" value="New Value"/></form></body></div></html>',
        )


class TestCssClass:
    def test_cssclass_init(self):
        css_class = core.CssClass("margin: 10px", "font-size: 12px", color="red")

        assert len(css_class.rules) == 3
        assert "margin: 10px" in css_class.rules
        assert "font-size: 12px" in css_class.rules
        assert "color: red" in css_class.rules
        assert css_class.class_name.startswith("-ps-")

    def test_cssclass_str(self):
        css_class = core.CssClass("margin: 10px", "font-size: 12px", color="red")
        class_name_str = str(css_class)

        assert class_name_str == css_class.class_name

    def test_cssclass_render_css(self):
        css_class = core.CssClass("margin: 10px", "font-size: 12px", color="red")
        rendered_css = css_class.render_css()

        assert rendered_css.startswith(f".{css_class.class_name} {{")
        assert "margin: 10px;" in rendered_css
        assert "font-size: 12px;" in rendered_css
        assert "color: red" in rendered_css
        assert rendered_css.endswith(" }")


class TestPage:
    @pytest.fixture
    def page(self):
        return core.Page()

    @pytest.fixture
    def css_class(self):
        return core.CssClass(border="solid 1px blue")

    def test_add_python_css_classes(self, page, css_class):
        page.python_css_classes = [css_class]
        page.document = MagicMock()
        page.document.getElementById.return_value = None

        page.add_python_css_classes()

        page.document.getElementById.assert_called_once_with("puepy-runtime-css")
        page.document.createElement.assert_called_once_with("style")
        page.document.createTextNode.assert_called_once()

    def test_add_python_css_classes_existing_element(self, page, css_class):
        page.python_css_classes = [css_class]
        page.document = MagicMock()

        page.add_python_css_classes()

        page.document.getElementById.assert_called_once_with("puepy-runtime-css")
        page.document.createElement.assert_not_called()


if __name__ == "__main__":
    unittest.main()
