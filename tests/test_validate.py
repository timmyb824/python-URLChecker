import os

from src.config.constants import ROOT_DIR
from src.config.validate import validate_yaml_file


def test_validate_yaml_file():
    schema = os.path.join(ROOT_DIR, "src", "schema", "schema.yaml")
    yaml = os.path.join(ROOT_DIR, "tests", "examples", "checks_good.yaml")
    assert validate_yaml_file(schema, yaml)


def test_validate_yaml_file_invalid():
    schema = os.path.join(ROOT_DIR, "src", "schema", "schema.yaml")
    yaml = os.path.join(ROOT_DIR, "tests", "examples", "checks_bad.yaml")
    assert not validate_yaml_file(schema, yaml)
