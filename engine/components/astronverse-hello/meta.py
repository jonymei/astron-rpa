import tomllib
import os
from pathlib import Path

from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.hello.hello import Hello


def get_version() -> str:
    component_dir = Path(__file__).resolve().parent
    pyproject_path = component_dir / "pyproject.toml"
    with pyproject_path.open("rb") as file:
        pyproject_data = tomllib.load(file)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    component_dir = Path(__file__).resolve().parent
    os.chdir(component_dir)
    config.set_config_file(str(component_dir / "config.yaml"))
    atomicMg.register(Hello, version=get_version())
    atomicMg.meta()
