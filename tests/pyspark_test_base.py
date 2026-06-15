import unittest

from src.config.config import Config
from src.utils.spark_utils import get_spark_session


class PySparkTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Config.EXECUTION_MODE = "demo"
        cls.spark = get_spark_session("UnitTests")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
