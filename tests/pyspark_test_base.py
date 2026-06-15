import unittest
from src.utils.spark_utils import get_spark_session
from src.config.config import Config


class PySparkTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Config.EXECUTION_MODE = "demo"
        cls.spark = get_spark_session("UnitTests")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
