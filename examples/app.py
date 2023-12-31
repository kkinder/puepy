from examples import components
from puepy.application import Application
from puepy.core import t
from puepy.router import Router

app = Application()
app.install_router(Router)
t.add_library(components)

app.base_title = "PuePy Examples"
