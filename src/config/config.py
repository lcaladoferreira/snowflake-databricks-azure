import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    EXECUTION_MODE = os.getenv("EXECUTION_MODE", "demo").lower()

    # Databricks
    DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
    DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

    # Snowflake
    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
    SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

    # Storage Bases
    LOCAL_DATA_DIR = "data"
    ADLS_BASE_PATH = os.getenv("ADLS_BASE_PATH", "abfss://landing@stdatalakeprod.dfs.core.windows.net")

    # Local Paths (always needed for Demo)
    RAW_DIR = os.path.join(LOCAL_DATA_DIR, "raw")
    BRONZE_DIR = os.path.join(LOCAL_DATA_DIR, "bronze")
    SILVER_DIR = os.path.join(LOCAL_DATA_DIR, "silver")
    GOLD_DIR = os.path.join(LOCAL_DATA_DIR, "gold")

    # Unity Catalog
    UC_CATALOG = os.getenv("UC_CATALOG", "main")
    UC_BRONZE_SCHEMA = os.getenv("UC_BRONZE_SCHEMA", "bronze")
    UC_SILVER_SCHEMA = os.getenv("UC_SILVER_SCHEMA", "silver")
    UC_GOLD_SCHEMA = os.getenv("UC_GOLD_SCHEMA", "gold")

    @classmethod
    def get_storage_path(cls, layer, table_name=""):
        if cls.EXECUTION_MODE == "demo":
            base = os.path.join(cls.LOCAL_DATA_DIR, layer)
        else:
            base = f"{cls.ADLS_BASE_PATH}/{layer}"

        return os.path.join(base, table_name) if table_name else base

    @classmethod
    def get_dbutils(cls, spark):
        try:
            from pyspark.dbutils import DBUtils
            return DBUtils(spark)
        except ImportError:
            return None
