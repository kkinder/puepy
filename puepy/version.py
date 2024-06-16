import os


def get_version():
    pyproject_path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    with open(pyproject_path, "r") as pyproject_file:
        for line in pyproject_file.readlines():
            if "version" in line:
                return line.split("=")[1].strip().strip('"')


try:
    __version__ = get_version()
except Exception:
    __version__ = "Unknown; not in a PyProject.toml file."
