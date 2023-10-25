import os
import glob
import pathlib


os.environ["SETTINGS_MODULE"] = "src.config.settings.test"

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


def _clean_name(val: str):
    return val.replace("/", ".").replace("\\", ".").replace(".py", "")


fixture_plugins = [
    _clean_name(name) for name in glob.glob("tests/fixtures/[!_]*py", root_dir=BASE_DIR)
]

pytest_plugins = [
    "pytest_asyncio",
] + fixture_plugins
