import importlib
import os
import tempfile
import unittest
from pathlib import Path


class LogsPersistenceTests(unittest.TestCase):
    def test_logs_are_persisted_to_a_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "clocktower-logs.txt"
            os.environ["CLOCKTOWER_LOG_FILE"] = str(log_path)

            import logs
            importlib.reload(logs)

            logs.add_log("render worker log")
            self.assertIn("render worker log", logs.get_logs())
            self.assertTrue(log_path.exists())
            self.assertIn("render worker log", log_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
