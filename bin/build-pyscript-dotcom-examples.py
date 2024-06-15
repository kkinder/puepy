"""
The script examples on pyscript.com are a little different. This builds what we upload there.
"""

import fnmatch
import os
import shutil
import json
import subprocess
from pathlib import Path

module_path = Path(__file__).resolve().parent
examples_path = module_path / "examples"
pyscript_examples_path = module_path / "pyscript_examples"


def replace_puepy_files_with_zip(content, zipfile_location):
    """
    Replaces the example with a PyScript one
    """

    if "files" in content:
        for file_source, file_dest in content["files"].copy().items():
            if fnmatch.fnmatch(file_source, "/puepy/*.py"):
                del content["files"][file_source]

        content["files"][zipfile_location] = "./*"

    return content


def build_pyscript_examples(source_dir: Path, destination_dir: Path):
    if not destination_dir.exists():
        os.makedirs(destination_dir, exist_ok=True)

    for origin_path, dirs, files in os.walk(source_dir):
        origin_path = Path(origin_path)

        zipfile_location = os.path.join(os.path.relpath(examples_path, origin_path), "puepy-bundle.zip")

        for file in files:
            relative_path = os.path.relpath(origin_path, source_dir)
            dest_path = destination_dir / relative_path
            os.makedirs(dest_path, exist_ok=True)

            if fnmatch.fnmatch(file, "pyscript*.json"):
                open(dest_path / file, "w").write(
                    json.dumps(
                        replace_puepy_files_with_zip(json.loads(open(origin_path / file).read()), zipfile_location),
                        indent=2,
                    )
                )
            else:
                shutil.copy2(origin_path / file, dest_path / file)


if __name__ == "__main__":
    build_pyscript_examples(examples_path, pyscript_examples_path)
    subprocess.check_call(f"zip -r {pyscript_examples_path / 'puepy-bundle.zip'} puepy/*.py", shell=True)
