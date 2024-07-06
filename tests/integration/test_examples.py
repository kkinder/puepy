import os
import re
import signal
import socket
import subprocess
import time
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
        response = process.stdout.readline()
        assert response == b"Serving at port *:5566\n"

    yield PORT

    if not already_running:
        os.kill(process.pid, signal.SIGTERM)
        process.wait()


def test_has_title(http_server, page: Page):
    page.goto(f"http://localhost:{PORT}/")
    expect(page).to_have_title(re.compile("PuePy Tutorial Examples"))


def test_hello_world(http_server, page: Page):
    page.goto("http://localhost:5566/")
    page.get_by_role("link", name="Example 1: Hello, World").click()
    expect(page.locator("h1")).to_contain_text("Hello, World!")


def test_hello_name(page: Page) -> None:
    page.goto("http://localhost:5566/")
    page.get_by_role("link", name="Example 2: Hello, Name").click()
    page.get_by_placeholder("name").click()
    page.get_by_placeholder("name").fill("Jack")
    page.get_by_placeholder("name").press("Enter")
    expect(page.locator("h1")).to_contain_text("Hello, Jack!")


#
# def test_has_title(page: Page):
#     page.goto("https://playwright.dev/")
#
#     # Expect a title "to contain" a substring.
#     expect(page).to_have_title(re.compile("Playwright"))
#
#
# def test_get_started_link(page: Page):
#     page.goto("https://playwright.dev/")
#
#     # Click the get started link.
#     page.get_by_role("link", name="Get started").click()
#
#     # Expects page to have a heading with the name of Installation.
#     expect(page.get_by_role("heading", name="Installation")).to_be_visible()
