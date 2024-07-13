"""
Common exceptions in the PuePy framework.

Classes:
    ElementNotInDom: Raised when an element is not found in the DOM, but it is expected to be, such as when getting Tag.element
    PropsError: Raised when unexpected props are passed to a component
    PageError: Analogous to http errors, but for a single-page app where the error is client-side
    NotFound: Page not found
    Forbidden: Forbidden
    Unauthorized: Unauthorized
    Redirect: Redirect
"""


class ElementNotInDom(Exception):
    """
    Raised when an element is not found in the DOM, but it is expected to be, such as when getting Tag.element
    """

    pass


class PropsError(ValueError):
    """
    Raised when unexpected props are passed to a component
    """


class PageError(Exception):
    """
    Analogous to http errors, but for a single-page app where the error is client-side
    """

    pass


class NotFound(PageError):
    """
    Raised when the router could not find a page matching the user's URL.
    """

    def __str__(self):
        return "Page not found"


class Forbidden(PageError):
    """
    Raised manually, presumably when the user is not authorized to access a page.
    """

    def __str__(self):
        return "Forbidden"


class Unauthorized(PageError):
    """
    Raised manually, presumably when the user is not authenticated.
    """

    def __str__(self):
        return "Unauthorized"


class Redirect(PageError):
    """
    Raised manually when the user should be redirected to another page.
    """

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return f"Redirect to {self.path}"
