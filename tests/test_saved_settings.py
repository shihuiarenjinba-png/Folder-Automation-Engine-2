"""Saved -2 settings are read-only validated before applying to the GUI."""
import json
import tempfile
import unittest
from pathlib import Path
from folder_automation import ConfigError
from folder_desktop_flow import (
    build_config, build_multi_config, read_saved_config, validate_saved_config,
)


class SavedSettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "inbox").mkdir()
        (self.root / "processed").mkdir()
        self.base = build_config(root_dir=str(self.root), input_folder="inbox",
                                 output_folder="processed", filename_glob="*.pdf",
                                 action="copy")

    def test_roundtrip_copy_config(self):
        path = self.root / "rules.json"
        path.write_text(json.dumps(self.base), encoding="utf-8")
        self.assertEqual(read_saved_config(path), self.base)

    def test_multi_rule_roundtrip(self):
        config = build_multi_config(
            root_dir=str(self.root), input_folder="inbox",
            output_folder="processed", filename_glob="*.pdf", action="copy",
            extra_rules=[{"glob": "*.jpg", "destination": "images", "action": "move"}],
        )
        self.assertEqual(validate_saved_config(config), config)

    def test_overwrite_true_must_be_rejected(self):
        payload = json.loads(json.dumps(self.base))
        payload["rules"][0]["overwrite"] = True
        with self.assertRaises(ConfigError):
            validate_saved_config(payload)

    def test_arbitrary_state_database_must_be_rejected(self):
        payload = json.loads(json.dumps(self.base))
        payload["state_db"] = "outside.sqlite3"
        with self.assertRaises(ConfigError):
            validate_saved_config(payload)

    def test_hidden_extra_options_must_be_rejected(self):
        payload = json.loads(json.dumps(self.base))
        payload["unsafe_mode"] = True
        with self.assertRaises(ConfigError):
            validate_saved_config(payload)

    def test_invalid_json_or_oversize_is_rejected(self):
        path = self.root / "invalid.json"
        path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(ConfigError):
            read_saved_config(path)
        path.write_bytes(b" " * (256 * 1024 + 1))
        with self.assertRaises(ConfigError):
            read_saved_config(path)


if __name__ == "__main__":
    unittest.main()
