from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
from src.config.config import Config


def get_spark_session(app_name="SnowflakeMigration"):
    if Config.EXECUTION_MODE == "demo":
        builder = (
            SparkSession.builder.appName(app_name)
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config(
                "spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            )
            .master("local[*]")
        )
        return configure_spark_with_delta_pip(builder).getOrCreate()
    else:
        # In Databricks, the Spark session is already available
        return SparkSession.builder.getOrCreate()
