import os
import pathlib
import sys
from http import server

project_path = pathlib.Path(__file__).parent
puepy_path = project_path / "puepy"
examples_path = project_path / "examples"

assert project_path.is_dir()
assert puepy_path.is_dir()
assert (puepy_path / "core.py").exists()

sys.path.append(str(project_path))


class Handler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]

        # We want to serve the examples from the /examples directory, but also allow pulls from /puepy/ for live
        # changes to code. This basically just treats /examples as the content root, unless the path starts with /puepy/
        if not path.startswith("/puepy/"):
            self.path = f"/examples{path}"

        return super().do_GET()

    def end_headers(self):
        """
        Cache nothing!
        """
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


if __name__ == "__main__":
    os.chdir(project_path)
    server_address = ("", 8000)
    httpd = server.HTTPServer(server_address, Handler)
    print(f"Serving at port 8000")
    httpd.serve_forever()
