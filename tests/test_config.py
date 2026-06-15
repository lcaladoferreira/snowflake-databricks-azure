import unittest
from src.config.config import Config


class TestConfig(unittest.TestCase):
    def test_get_storage_path_demo(self):
        Config.EXECUTION_MODE = "demo"
        path = Config.get_storage_path("bronze", "customers")
        self.assertEqual(path, "data/bronze/customers")

    def test_get_storage_path_prod(self):
        Config.EXECUTION_MODE = "production"
        Config.ADLS_ACCOUNT_NAME = "acc"
        Config.ADLS_CONTAINER = "lake"
        Config.ADLS_BASE_PATH = "abfss://lake@acc.dfs.core.windows.net"
        path = Config.get_storage_path("bronze", "customers")
        self.assertEqual(path, "abfss://lake@acc.dfs.core.windows.net/bronze/customers")


if __name__ == "__main__":
    unittest.main()
