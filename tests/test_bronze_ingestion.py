import unittest
from unittest.mock import patch

from jobs.bronze.raw_to_bronze import ingest_raw_to_bronze
from tests.pyspark_test_base import PySparkTestCase


class TestBronzeIngestion(PySparkTestCase):
    def setUp(self):
        # Create a dummy parquet file to satisfy Spark's path check
        self.dummy_path = "tests/dummy.parquet"
        data = [(1, "test")]
        schema = ["id", "val"]
        self.spark.createDataFrame(data, schema).write.parquet(
            self.dummy_path, mode="overwrite"
        )

    @patch("src.config.config.Config.get_storage_path")
    def test_ingest_raw_to_bronze_batch(self, mock_path):
        mock_path.side_effect = lambda layer, table: (
            self.dummy_path if layer == "landing" else f"data/{layer}/{table}"
        )

        # Test parameters
        table_name = "customers"
        batch_id = "test_batch_123"

        # Execution - verify it runs without error (means it read the dummy and processed metadata)
        # We use a real path but check if it attempted to write
        target_path = f"data/bronze/{table_name}"
        ingest_raw_to_bronze(self.spark, table_name, batch_id)

        # Verify result exists
        import os

        self.assertTrue(os.path.exists(target_path))


if __name__ == "__main__":
    unittest.main()
