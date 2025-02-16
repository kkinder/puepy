# Navigation Guards

When a page loads, you can guard navigation to that page by running a *precheck*  – a method that runs before the page is rendered. If the precheck raises an exception, the page is not rendered, and the exception is caught by the framework. This is useful for checking if a user is authenticated, for example.

Here's an example of a precheck that raises an exception if the user is not authenticated:

```py title="Showing error"
from puepy import exceptions, Page

class MyPage(Page):
    ...
    def precheck(self):
        if not self.application.state["authenticated_user"]:
            raise exceptions.Unauthorized()
```

In this example, if the `authenticated_user` key in the application state is `False`, the page will not render, and an `Unauthorized` exception will be raised. PuePy will then display your `application.unauthorized_page`.

Alternatively, you could redirect the user by raising puepu.exceptions.Redirect:

```py title="Redirecting to a login page"
from puepy import exceptions, Page


class LoginPage(Page):
    ...


class MyPage(Page):
    ...
    def precheck(self):
        if not self.application.state["authenticated_user"]:
            raise exceptions.Redirect(LoginPage)
```

