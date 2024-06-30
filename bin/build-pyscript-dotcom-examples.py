"""
The script examples on pyscript.com are a little different. This builds what we upload there.
"""

import fnmatch
import os
import shutil
import json
import subprocess
from pathlib import Path

module_path = Path(__file__).resolve().parent.parent
examples_path = module_path / "examples"
pyscript_examples_path = module_path / "pyscript_examples"


def replace_puepy_files_with_dist(content, wheel_location):
    """
    Replaces the example with a PyScript one
    """

    if "files" in content:
        for file_source, file_dest in content["files"].copy().items():
            if fnmatch.fnmatch(file_source, "/puepy/*.py"):
                del content["files"][file_source]

    if "packages" not in content:
        content["packages"] = []
    content["packages"].append(wheel_location)

    return content


def build_pyscript_examples(source_dir: Path, destination_dir: Path):
    if not destination_dir.exists():
        os.makedirs(destination_dir, exist_ok=True)

    for origin_path, dirs, files in os.walk(source_dir):
        origin_path = Path(origin_path)

        wheel_location = os.path.join(os.path.relpath(examples_path, origin_path), wheel_file.name)

        for file in files:
            relative_path = os.path.relpath(origin_path, source_dir)
            dest_path = destination_dir / relative_path
            os.makedirs(dest_path, exist_ok=True)

            if fnmatch.fnmatch(file, "pyscript*.json"):
                open(dest_path / file, "w").write(
                    json.dumps(
                        replace_puepy_files_with_dist(json.loads(open(origin_path / file).read()), wheel_location),
                        indent=2,
                    )
                )
            else:
                shutil.copy2(origin_path / file, dest_path / file)


if __name__ == "__main__":
    # Get puepy version
    version = subprocess.check_output("poetry version -s", shell=True).decode().strip()
    wheel_file = Path(module_path / "dist" / f"puepy-{version}-py3-none-any.whl")

    assert wheel_file.exists(), f"Wheel file not found: {wheel_file}"
    existing_install_config = examples_path / "installation" / "pyscript.json"

    os.makedirs(pyscript_examples_path, exist_ok=True)
    subprocess.check_call(f"cp {wheel_file} {pyscript_examples_path}", shell=True)
    build_pyscript_examples(examples_path, pyscript_examples_path)
