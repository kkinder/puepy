import re
from bs4 import BeautifulSoup, Comment
from puepy import Application, Page, t

app = Application()

PYTHON_KEYWORDS = [
    "false",
    "none",
    "true",
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
]


class TagGenerator:
    def __init__(self, indentation=4):
        self.indent_level = 0
        self.indentation = indentation

    def indent(self):
        return " " * self.indentation * self.indent_level

    def sanitize(self, key):
        key = re.sub(r"\W", "_", key)
        if not key[0].isalpha():
            key = f"_{key}"
        if key == "class":
            key = "classes"
        elif key.lower() in PYTHON_KEYWORDS:
            key = f"{key}_"
        return key

    def generate_tag(self, tag):
        attr_list = [
            f"{self.sanitize(key)}={repr(' '.join(value) if isinstance(value, list) else value)}"
            for key, value in tag.attrs.items()
        ]

        underscores_tag_name = tag.name.replace("-", "_")

        sanitized_tag_name = self.sanitize(underscores_tag_name)
        if sanitized_tag_name != underscores_tag_name:
            # For the rare case where it really just has to be the original tag
            attr_list.append(f"tag={repr(tag.name)}")

        attributes = ", ".join(attr_list)

        return (
            f"{self.indent()}with t.{sanitized_tag_name}({attributes}):"
            if tag.contents
            else f"{self.indent()}t.{sanitized_tag_name}({attributes})"
        )

    def iterate_node(self, node):
        output = []
        for child in node.children:
            if child.name:  # Element
                output.append(self.generate_tag(child))
                self.indent_level += 1
                if child.contents:
                    output.extend(self.iterate_node(child))
                self.indent_level -= 1
            elif isinstance(child, Comment):
                for line in child.strip().split("\n"):
                    output.append(f"{self.indent()}# {line}")
            elif isinstance(child, str) and child.strip():  # Text node
                output.append(f"{self.indent()}t({repr(child.strip())})")
        return output

    def generate_app_root(self, node, generate_full_file=True):
        header = (
            [
                "from puepy import Application, Page, t",
                "",
                "app = Application()",
                "",
                "@app.page()",
                "class DefaultPage(Page):",
                "    def populate(self):",
            ]
            if generate_full_file
            else []
        )
        self.indent_level = 2 if generate_full_file else 0
        body = self.iterate_node(node)
        return "\n".join(header + body)


def convert_html_to_context_manager(html, indent=4, generate_full_file=True):
    soup = BeautifulSoup(html, "html.parser")
    generator = TagGenerator(indentation=indent)
    return generator.generate_app_root(soup, generate_full_file=generate_full_file)


@app.page()
class DefaultPage(Page):
    def initial(self):
        return {"input": "", "output": "", "error": "", "generate_full_file": True}

    def populate(self):
        with t.div(classes="section"):
            t.h1("Convert HTML to PuePy syntax with BeautifulSoup", classes="title is-1")
            with t.div(classes="columns is-variable is-8 is-multiline"):
                with t.div(classes="column is-half-desktop is-full-mobile"):
                    with t.div(classes="field"):
                        t.div("Enter HTML Here", classes="label")
                        t.textarea(bind="input", classes="textarea")
                with t.div(classes="column is-half-desktop is-full-mobile"):
                    with t.div(classes="field"):
                        t.div("Output", classes="label")
                        t.textarea(bind="output", classes="textarea", readonly=True)
            with t.div(classes="field is-grouped"):
                with t.p(classes="control"):
                    t.button("Convert", classes="button is-primary", on_click=self.on_convert_click)
                with t.p(classes="control"):
                    with t.label(classes="checkbox"):
                        t.input(bind="generate_full_file", type="checkbox")
                        t(" Generate full file")
            if self.state["error"]:
                with t.div(classes="notification is-danger"):
                    t(self.state["error"])

    def on_convert_click(self, event):
        self.state["error"] = ""
        try:
            self.state["output"] = convert_html_to_context_manager(
                self.state["input"], generate_full_file=self.state["generate_full_file"]
            )
        except Exception as e:
            self.state["error"] = str(e)


app.mount("#app")
