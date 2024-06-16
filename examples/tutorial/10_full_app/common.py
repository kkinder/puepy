from puepy import Application
from puepy.router import Router, Route


class AwesomeApp(Application):
    def initial(self):
        return {"authenticated_user": ""}

    def handle_unauthorized(self, exception):
        from pages import LoginPage

        self.router.navigate_to_path(LoginPage, return_to=self.current_path)


app = AwesomeApp()
app.install_router(Router, link_mode=Router.LINK_MODE_HASH)
