import unittest
from unittest.mock import patch

from src.validation.reconciliation_engine import ReconciliationEngine
from tests.pyspark_test_base import PySparkTestCase


class TestReconciliation(PySparkTestCase):
    def setUp(self):
        self.engine = ReconciliationEngine(self.spark)

    def test_compare_metrics_pass(self):
        source = {"row_count": 100}
        target = {"row_count": 100}

        report = self.engine._compare_metrics("test_table", source, target)

        self.assertEqual(report["status"], "PASSED")
        self.assertEqual(report["table_name"], "test_table")

    def test_compare_metrics_fail(self):
        source = {"row_count": 100}
        target = {"row_count": 90}

        report = self.engine._compare_metrics("test_table", source, target)

        self.assertEqual(report["status"], "FAILED")
        self.assertIn("Count mismatch", report["message"])

    @patch("src.config.config.Config.get_storage_path")
    def test_persist_report(self, mock_path):
        mock_path.return_value = "audit_path"
        mock_report = {
            "table_name": "test",
            "status": "PASSED",
            "source_metrics": "{}",
            "target_metrics": "{}",
            "message": "",
            "reconciled_at": "now",
        }

        # Execution
        # In demo mode it writes to a path, we can't easily mock write without deep patch but we can check if it tries to create df
        with patch.object(
            self.spark, "createDataFrame", wraps=self.spark.createDataFrame
        ) as mock_create:
            self.engine._persist_report(mock_report)
            mock_create.assert_called()


if __name__ == "__main__":
    unittest.main()
