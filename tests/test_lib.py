import unittest

from unittest.mock import MagicMock, patch

from envyaml import EnvYAML

from src.lib import PublicVariableGenerator


class TestPublicVariableGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = PublicVariableGenerator()

    @patch("src.settings.zkp_settings")
    def test_get_bits(self, mock_zkp_settings: MagicMock) -> None:
        yaml_config = EnvYAML("./config/local.yaml", strict=False)

        self.assertEqual(self.generator.get_bits(), yaml_config["implementation"]["bits"])

    def test_is_prime(self) -> None:
        self.assertTrue(self.generator._is_prime(5))
        self.assertFalse(self.generator._is_prime(4))

    @patch("random.getrandbits")
    def test_get_prime(self, mock_getrandbits: MagicMock) -> None:
        mock_getrandbits.return_value = 11
        prime = self.generator._get_prime(4)
        self.assertTrue(self.generator._is_prime(prime))

    @patch("random.getrandbits")
    def test_get_safe_prime(self, mock_getrandbits: MagicMock) -> None:
        mock_getrandbits.return_value = 5
        p, q = self.generator._get_safe_prime(4)
        self.assertTrue(self.generator._is_prime(p))
        self.assertTrue((p - 1) // 2 == q)

    @patch("random.randint")
    def test_find_generator(self, mock_randint: MagicMock) -> None:
        mock_randint.return_value = 6791122
        p, q = 7394867, 3697433
        generator = self.generator._find_generator(p, q)
        self.assertNotEqual(pow(generator, 2, p), 1)
        self.assertEqual(pow(generator, q, p), 1)

    def test_approach1(self) -> None:
        approach = self.generator.Approach1(self.generator)
        p, q, g, h = approach.get_public_variables()
        self.assertTrue(self.generator._is_prime(p))
        self.assertTrue(self.generator._is_prime(q))
        self.assertNotEqual(g, h)


if __name__ == "__main__":
    unittest.main()
