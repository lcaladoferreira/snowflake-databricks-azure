import pytest
import os
from src.config.config import Config

def test_config_demo_mode():
    assert Config.EXECUTION_MODE in ["demo", "production"]
    assert Config.LOCAL_DATA_DIR == "data"

def test_directory_structure():
    required_dirs = ["data/sample", "src/config", "jobs/bronze", "sql/unity_catalog"]
    for d in required_dirs:
        assert os.path.isdir(d)

def test_sample_data_exists():
    # This assumes generate_sample_data.py has been run
    assert os.path.exists("data/sample/customers.csv")
    assert os.path.exists("data/sample/orders.csv")
