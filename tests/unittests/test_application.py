import unittest
from unittest.mock import Mock, patch

from .dom_test import DomTest
from puepy.application import Application
from puepy.exceptions import Redirect, Unauthorized, Forbidden
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

        @self.app.page("/cause-programming-error")
        class CauseProgrammingErrorPage(Page):
            def populate(self):
                raise ValueError

        @self.app.page("/trigger-login-redirect")
        class TriggerLoginRedirectPage(Page):
            def precheck(self):
                raise Redirect("/login")

        @self.app.page("/trigger-login-redirect2")
        class TriggerLoginRedirectPage2(Page):
            def precheck(self):
                raise Redirect(LoginPage)

        @self.app.page("/trigger-unauthorized")
        class TriggerUnauthorizedPage(Page):
            def precheck(self):
                raise Unauthorized

        @self.app.page("/trigger-forbidden")
        class TriggerForbiddenPage(Page):
            def precheck(self):
                raise Forbidden

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

    def test_error_page_defaults(self):
        with self.assertRaises(ValueError):
            self.app.mount(self.html, path="/cause-programming-error")
        self.assertIsInstance(self.app.active_page, self.app.error_page)

    def test_redirect_to_path_exception(self):
        self.app.mount(self.html, path="/trigger-login-redirect")
        self.assertIsInstance(self.app.active_page, self.login_page_class)

    def test_redirect_to_page_exception(self):
        self.app.mount(self.html, path="/trigger-login-redirect2")
        self.assertIsInstance(self.app.active_page, self.login_page_class)

    def test_unauthorized_page(self):
        self.app.mount(self.html, path="/trigger-unauthorized")
        self.assertIsInstance(self.app.active_page, self.app.unauthorized_page)

    def test_forbidden_page(self):
        self.app.mount(self.html, path="/trigger-forbidden")
        self.assertIsInstance(self.app.active_page, self.app.forbidden_page)

    def test_handle_not_found(self):
        self.app.mount(self.html, path="/not-found")
        self.assertIsInstance(self.app.active_page, self.app.not_found_page)


if __name__ == "__main__":
    unittest.main()
