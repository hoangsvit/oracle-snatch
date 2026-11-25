import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import oci
import snatch

class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.cfg = dict(ocpus=4, memory_gb=24, boot_volume_gb=50,
                        interval=120, rate_limit_sleep=300)

    def test_limits(self):
        snatch.validate_settings(self.cfg)
        for key, value in (("ocpus", 5), ("memory_gb", float("nan")),
                           ("boot_volume_gb", 201), ("interval", 1)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                snatch.validate_settings(dict(self.cfg, **{key: value}))

    def test_success_persists_before_ip_lookup(self):
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "state.json")
            compute = Mock()
            compute.launch_instance.return_value.data = SimpleNamespace(
                id="instance", display_name="test")
            snatch.launch_and_record(compute, None, self.cfg, "AD", path)
            self.assertIn('"status": "created"', Path(path).read_text())
            with self.assertRaises(FileExistsError):
                snatch.launch_and_record(compute, None, self.cfg, "AD", path)
            compute.launch_instance.assert_called_once()

    def test_ambiguous_failure_retains_intent(self):
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "state.json")
            compute = Mock()
            compute.launch_instance.side_effect = TimeoutError()
            with self.assertRaises(TimeoutError):
                snatch.launch_and_record(compute, None, self.cfg, "AD", path)
            self.assertIn('"status": "pending"', Path(path).read_text())

    def test_rate_limit_clears_intent(self):
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "state.json")
            compute = Mock()
            compute.launch_instance.side_effect = oci.exceptions.ServiceError(
                429, "TooManyRequests", {}, "rate limit")
            with self.assertRaises(oci.exceptions.ServiceError):
                snatch.launch_and_record(compute, None, self.cfg, "AD", path)
            self.assertFalse(Path(path).exists())

if __name__ == "__main__":
    unittest.main()
