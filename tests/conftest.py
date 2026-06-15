import pytest
from pyspark.sql import SparkSession

from src.config.config import Config


@pytest.fixture(scope="session")
def spark():
    """Fixture for a shared Spark session."""
    Config.EXECUTION_MODE = "demo"
    spark = (
        SparkSession.builder.master("local[1]")
        .appName("pytest-spark-session")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .getOrCreate()
    )
    yield spark
    spark.stop()


@pytest.fixture
def mock_config(monkeypatch):
    """Fixture to mock common config values."""
    monkeypatch.setenv("EXECUTION_MODE", "demo")
    monkeypatch.setenv("ENV", "test")
    return Config
