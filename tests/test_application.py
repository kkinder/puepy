import unittest
from unittest.mock import Mock

from dom_test import DomTest
from puepy.application import Application
from puepy.router import Router
from puepy.core import Page, t


class TestApplication(DomTest):
    def setUp(self):
        super().setUp()

        self.app = Application()
        self.app.install_router(Router)

        @self.app.page()
        class MainPage(Page):
            def populate(self):
                t.p("Main Page")

        @self.app.page("/login")
        class LoginPage(Page):
            def populate(self):
                t.p("Login Page")

        self.main_page_class = MainPage
        self.login_page_class = LoginPage

    def test_install_router(self):
        self.assertIsInstance(self.app.router, Router)

    def test_mount_main_page(self):
        self.app.mount(self.html, path="/")
        self.assertIn("Main Page", self.html.toxml())

    def test_mount_login_page(self):
        self.app.mount(self.html, path="/login")
        self.assertIn("Login Page", self.html.toxml())


if __name__ == "__main__":
    unittest.main()
