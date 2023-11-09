import logging
import unittest

from unittest.mock import MagicMock, patch

from src.settings import Flavour, Settings, log_level_mapping


class TestSettings(unittest.TestCase):
    @patch("src.settings.EnvYAML")
    def test_settings_initialization(self, mock_envyaml: MagicMock) -> None:
        mock_envyaml.return_value = {
            "public_variables": {"p": 123, "q": 456, "g": 789, "h": 1337},
            "implementation": {"flavour": "exponentiations", "bits": 32},
            "logging": {"level": "info"},
        }

        settings = Settings()

        self.assertEqual(settings.p, 123)
        self.assertEqual(settings.q, 456)
        self.assertEqual(settings.g, 789)
        self.assertEqual(settings.h, 1337)
        self.assertEqual(settings.flavour, Flavour.EXPONENTIATIONS)
        self.assertEqual(settings.bits, 32)
        self.assertEqual(settings.log_level, "info")

    def test_value_size_validator_correct(self) -> None:
        Settings.check_value_size(123)

    def test_value_size_validator_incorrect_too_small(self) -> None:
        with self.assertRaises(ValueError):
            Settings.check_value_size(-1)

    def test_value_size_validator_incorrect_too_big(self) -> None:
        with self.assertRaises(ValueError):
            Settings.check_value_size(1 << 63)

    def test_bits_range_validator_correct(self) -> None:
        Settings.check_bits_range(63)

    def test_bits_range_validator_incorrect_too_small(self) -> None:
        with self.assertRaises(ValueError):
            Settings.check_bits_range(-1)

    def test_bits_range_validator_incorrect_too_big(self) -> None:
        with self.assertRaises(ValueError):
            Settings.check_bits_range(64)

    def test_log_level_mapping_correct(self) -> None:
        self.assertEqual(log_level_mapping["debug"], logging.DEBUG)
        self.assertEqual(log_level_mapping["info"], logging.INFO)
        self.assertEqual(log_level_mapping["warning"], logging.WARNING)
        self.assertEqual(log_level_mapping["error"], logging.ERROR)
        self.assertEqual(log_level_mapping["critical"], logging.CRITICAL)

    def test_log_level_mapping_incorrect(self) -> None:
        with self.assertRaises(KeyError):
            self.assertEqual(log_level_mapping["dbg"], logging.DEBUG)


if __name__ == "__main__":
    unittest.main()
