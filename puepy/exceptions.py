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
    def __str__(self):
        return "Page not found"


class Forbidden(PageError):
    def __str__(self):
        return "Forbidden"


class Unauthorized(PageError):
    def __str__(self):
        return "Unauthorized"


class Redirect(PageError):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return f"Redirect to {self.path}"
