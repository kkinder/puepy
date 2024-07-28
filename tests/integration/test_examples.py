import os
import re
import socket
import subprocess
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

main_directory = Path(__file__).parent.parent.parent.resolve()

assert (main_directory / "serve_examples.py").exists()


PORT = 5566


def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((host, port))
    except (socket.timeout, ConnectionRefusedError):
        return False
    else:
        return True
    finally:
        sock.close()


@pytest.fixture(scope="session")
def http_server():
    already_running = check_port("localhost", PORT)

    if not already_running:
        os.chdir(main_directory)
        process = subprocess.Popen(
            ["python", "serve_examples.py", f"--port", str(PORT)], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    yield PORT

    if not already_running:
        process.terminate()
        process.wait()


def test_has_title(http_server, page: Page):
    page.goto(f"http://localhost:{PORT}/")
    expect(page).to_have_title(re.compile("PuePy Tutorial Examples"))


def test_hello_world(http_server, page: Page):
    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="Example 1: Hello, World").click()
    expect(page.locator("h1")).to_contain_text("Hello, World!")


def test_hello_name(page: Page):
    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="Example 2: Hello, Name").click()
    page.get_by_placeholder("name").click()
    page.get_by_placeholder("name").fill("Jack")
    page.get_by_placeholder("name").press("Enter")
    expect(page.locator("h1")).to_contain_text("Hello, Jack!")


def test_counter(page: Page):
    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="Example 3: Counter").click()
    page.get_by_role("button", name="+").click()
    expect(page.locator(".count")).to_contain_text("1")
    page.get_by_role("button", name="+").click()
    expect(page.locator(".count")).to_contain_text("2")
    page.get_by_role("button", name="-").click()
    expect(page.locator(".count")).to_contain_text("1")
    page.get_by_role("button", name="-").click()
    expect(page.locator(".count")).to_contain_text("0")
    page.get_by_role("button", name="-").click()
    expect(page.locator(".count")).to_contain_text("-1")


def test_refs_problem(page: Page):
    def input_is_active():
        return page.evaluate("document.querySelector(\"[placeholder='Type a word']\") === document.activeElement")

    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="Example 4: Refs Problem").click()
    page.get_by_placeholder("Type a word").click()

    # Input box has focus
    assert input_is_active()

    # You type...
    page.get_by_placeholder("Type a word").fill("F")

    # Input box loses focus
    assert not input_is_active()


def test_refs_solution(page: Page):
    def input_is_active():
        return page.evaluate("document.querySelector(\"[placeholder='Type a word']\") === document.activeElement")

    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="solution").click()
    page.get_by_placeholder("Type a word").click()

    assert input_is_active()
    page.get_by_placeholder("Type a word").fill("foobar")
    assert input_is_active()


def test_watchers(page: Page):
    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="Example 5: Watchers").click()
    page.get_by_placeholder("Enter a guess").click()
    page.get_by_placeholder("Enter a guess").fill("3")
    page.get_by_text("Keep trying...").click()
    page.get_by_placeholder("Enter a guess").click()
    page.get_by_placeholder("Enter a guess").fill("4")
    page.get_by_text("You guessed the number!").click()


def test_components(page: Page):
    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="Example 6: Components").click()

    page.get_by_role("button", name="Okay Then").click()
    expect(page.locator("#result")).to_contain_text("Custom event from card with type success")
    page.get_by_role("button", name="Got It").click()
    expect(page.locator("#result")).to_contain_text("Custom event from card with type warning")
    page.get_by_role("button", name="Understood").click()
    expect(page.locator("#result")).to_contain_text("Custom event from card with type error")


def test_routing(page: Page):
    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="Example 7: Routing").click()

    page.get_by_role("heading", name="PuePy Routing Demo: Pet").click()
    page.get_by_role("link", name="Scooby-Doo").click()
    page.get_by_text("Scooby-Doo").click()
    page.get_by_role("link", name="Back to Homepage").click()
    page.get_by_role("link", name="Garfield").click()
    page.get_by_text("Garfield").click()
    page.get_by_role("link", name="Back to Homepage").click()
    page.get_by_role("link", name="Snoopy").click()
    page.get_by_text("Snoopy").click()
    page.get_by_role("link", name="Back to Homepage").click()
    page.get_by_role("heading", name="PuePy Routing Demo: Pet").click()


def test_pypi_libraries(page: Page):
    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="Example 8: PyPi Libraries").click()
    page.get_by_role("textbox").first.click()
    page.get_by_role("textbox").first.fill("<html>\n<body>\n<h1>Hello, World!</h1>\n</body>\n</html>\n")
    page.get_by_role("button", name="Convert").click()
    expect(page.locator("#pp-b")).to_have_value(
        "from puepy import Application, Page, t\n\napp = Application()\n\n@app.page()\nclass DefaultPage(Page):\n    "
        "def populate(self):\n        with t.html():\n            with t.body():\n                with t.h1():\n     "
        "               t('Hello, World!')"
    )
    page.get_by_text("Generate full file").click()
    page.get_by_role("button", name="Convert").click()
    expect(page.locator("#pp-b")).to_have_value(
        "with t.html():\n    with t.body():\n        with t.h1():\n            t('Hello, World!')"
    )


def test_webcomponents(page: Page):
    page.goto(f"http://localhost:{PORT}/")
    page.get_by_role("link", name="Example 9: WebComponents").click()
    page.get_by_role("button", name="Open Dialog").click()
    page.locator("sl-button").filter(has_text="Close").get_by_role("button").click()


def test_a_full_app(page: Page):
    page.goto(f"http://localhost:{PORT}/")

    page.get_by_role("link", name="Example 10: A full-blown app").click()
    page.get_by_label("Username").click()
    page.get_by_label("Username").fill("foo")
    page.get_by_label("Username").press("Tab")
    page.get_by_label("Password").fill("bar")
    page.get_by_role("button", name="Login").click()
    page.get_by_role("heading", name="Hello, you are authenticated").click()
    page.get_by_label("User Settings").click()
    page.get_by_role("menuitem", name="Profile").locator("path").nth(3).click()
    page.get_by_role("link", name="Dashboard").click()
    page.get_by_role("heading", name="Hello, you are authenticated").click()
    page.get_by_role("link", name="Charts").click()
    page.get_by_role("link", name="Forms").click()
    page.get_by_label("Name").click()
    page.get_by_label("Name").fill("Hello")
    page.get_by_role("button", name="Submit").click()
    page.get_by_role("link", name="Dashboard").click()
    page.get_by_role("heading", name="Hello, you are authenticated").click()
