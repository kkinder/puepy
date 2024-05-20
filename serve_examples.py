import json
import os
import pathlib
import posixpath
import sys
import urllib.parse
from http import server, HTTPStatus

project_path = pathlib.Path(__file__).parent
puepy_path = project_path / "puepy"
examples_path = project_path / "examples"

assert project_path.is_dir()
assert puepy_path.is_dir()
assert (puepy_path / "core.py").exists()

sys.path.append(str(project_path))

puepy_package_files = []

PUEPY_PATH = "puepy"  # In URLs, this will be the directory the puepy files are served from (core.py, etc)


class Handler(server.SimpleHTTPRequestHandler):
    def translate_path2(self, path):
        """
        Just a tweak of the superclass's that sends puepy files elsewhere. It's just easier to layout
        the project this way.
        """
        path = path.split("?", 1)[0]
        path = path.split("#", 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith("/")
        try:
            path = urllib.parse.unquote(path, errors="surrogatepass")
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split("/")

        if words[0] == PUEPY_PATH or (words[0] == "" and words[1] == PUEPY_PATH):
            directory = os.fspath(puepy_path)
        else:
            directory = self.directory

        words = filter(None, words)
        path = directory
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += "/"
        return path

    def do_GET(self):
        """
        Routes everything to example_page.html if it doesn't exist, so the frontend code can do the routing.
        """
        path = self.path.split("?")[0]
        if path == "/pyscript-config.json":
            content = json.dumps(build_config()).encode("utf8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        elif path == "/" or not os.path.exists(path[1:]):
            self.path = "examples/example_page.html"
        return super().do_GET()

    def end_headers(self):
        """
        Cache nothing!
        """
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def gather_py_files(directory):
    return_value = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".py"):
                return_value.append(pathlib.Path(os.path.join(dirpath, filename)))

    return return_value


def build_config():
    files = {}

    def add_files(path):
        for file in gather_py_files(path):
            f = str(file.relative_to(project_path))
            files[f] = f

    add_files(puepy_path)
    add_files(examples_path)

    return dict(debug=True, files=files)


if __name__ == "__main__":
    os.chdir(project_path)
    server_address = ("", 8000)
    httpd = server.HTTPServer(server_address, Handler)
    print(f"Serving at port 8000")
    httpd.serve_forever()
