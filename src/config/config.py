"""Configuration management for the Snowflake to Databricks migration accelerator.

This module handles loading environment variables and providing a centralized
Config class for all pipeline components.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Structured Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Config:
    """Central configuration management for the migration accelerator.

    Attributes:
        ENV (str): Deployment environment (dev, test, prod).
        EXECUTION_MODE (str): Execution mode (demo, production).
        DATABRICKS_HOST (str): Databricks workspace URL.
        DATABRICKS_TOKEN (str): Databricks PAT.
        SNOWFLAKE_ACCOUNT (str): Snowflake account identifier.
        SNOWFLAKE_USER (str): Snowflake username.
        SNOWFLAKE_PASSWORD (str): Snowflake password.
        SNOWFLAKE_WAREHOUSE (str): Snowflake warehouse name.
        SNOWFLAKE_DATABASE (str): Snowflake database name.
        SNOWFLAKE_SCHEMA (str): Snowflake schema name.
        SNOWFLAKE_ROLE (str): Snowflake role.
        ADLS_ACCOUNT_NAME (str): Azure Storage account name.
        ADLS_CONTAINER (str): ADLS Gen2 container name.
        ADLS_BASE_PATH (str): Base ABFSS path.
        LOCAL_DATA_DIR (str): Directory for local data in demo mode.
        UC_CATALOG (str): Unity Catalog catalog name.
        UC_BRONZE_SCHEMA (str): Bronze schema name.
        UC_SILVER_SCHEMA (str): Silver schema name.
        UC_GOLD_SCHEMA (str): Gold schema name.
    """

    ENV: str = os.getenv("ENV", "dev").lower()
    EXECUTION_MODE: str = os.getenv("EXECUTION_MODE", "demo").lower()

    # Databricks
    DATABRICKS_HOST: Optional[str] = os.getenv("DATABRICKS_HOST")
    DATABRICKS_TOKEN: Optional[str] = os.getenv("DATABRICKS_TOKEN")

    # Snowflake
    SNOWFLAKE_ACCOUNT: Optional[str] = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER: Optional[str] = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD: Optional[str] = os.getenv("SNOWFLAKE_PASSWORD")
    SNOWFLAKE_WAREHOUSE: Optional[str] = os.getenv("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_DATABASE: Optional[str] = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA: Optional[str] = os.getenv("SNOWFLAKE_SCHEMA")
    SNOWFLAKE_ROLE: Optional[str] = os.getenv("SNOWFLAKE_ROLE")

    # Azure Storage (ADLS Gen2)
    ADLS_ACCOUNT_NAME: Optional[str] = os.getenv("ADLS_ACCOUNT_NAME")
    ADLS_CONTAINER: str = os.getenv("ADLS_CONTAINER", "lakehouse")
    ADLS_BASE_PATH: str = os.getenv("ADLS_BASE_PATH", f"abfss://{ADLS_CONTAINER}@{ADLS_ACCOUNT_NAME}.dfs.core.windows.net")

    # Local Paths (Demo Mode)
    LOCAL_DATA_DIR: str = "data"

    # Unity Catalog
    UC_CATALOG: str = os.getenv("UC_CATALOG", f"migration_{ENV}")
    UC_BRONZE_SCHEMA: str = "bronze"
    UC_SILVER_SCHEMA: str = "silver"
    UC_GOLD_SCHEMA: str = "gold"

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Returns a configured logger instance.

        Args:
            name (str): Name of the logger.

        Returns:
            logging.Logger: Configured logger.
        """
        return logging.getLogger(name)

    @classmethod
    def get_storage_path(cls, layer: str, table_name: str = "") -> str:
        """Constructs the storage path for a given layer and table.

        Args:
            layer (str): Medallion layer or container name.
            table_name (str, optional): Name of the table. Defaults to "".

        Returns:
            str: Full path to the storage location.
        """
        if cls.EXECUTION_MODE == "demo":
            base = os.path.join(cls.LOCAL_DATA_DIR, layer)
        else:
            base = f"{cls.ADLS_BASE_PATH}/{layer}"

        return os.path.join(base, table_name) if table_name else base

    @classmethod
    def get_snowflake_config(cls) -> Dict[str, Any]:
        """Returns Snowflake connection parameters.

        Returns:
            Dict[str, Any]: Snowflake connection configuration.
        """
        return {
            "account": cls.SNOWFLAKE_ACCOUNT,
            "user": cls.SNOWFLAKE_USER,
            "password": cls.SNOWFLAKE_PASSWORD,
            "warehouse": cls.SNOWFLAKE_WAREHOUSE,
            "database": cls.SNOWFLAKE_DATABASE,
            "schema": cls.SNOWFLAKE_SCHEMA,
            "role": cls.SNOWFLAKE_ROLE
        }
