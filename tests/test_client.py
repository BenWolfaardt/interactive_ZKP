import logging
import unittest

from unittest.mock import MagicMock, patch

from envyaml import EnvYAML
from proto.zkp_auth_pb2 import AuthenticationChallengeResponse

from client import Client, ClientUserData


class TestClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.client.set_variables()

    def test_set_variables(self) -> None:
        yaml_config = EnvYAML("./config/local.yaml", strict=False)

        self.assertEqual(self.client.p, yaml_config["public_variables"]["p"])
        self.assertEqual(self.client.q, yaml_config["public_variables"]["q"])
        self.assertEqual(self.client.g, yaml_config["public_variables"]["g"])
        self.assertEqual(self.client.h, yaml_config["public_variables"]["h"])
        self.assertEqual(self.client.flavour, yaml_config["implementation"]["flavour"])
        self.assertEqual(self.client.bits, yaml_config["implementation"]["bits"])
        self.assertEqual(self.client.log_level, yaml_config["logging"]["level"])

    @patch("src.client.logging.getLogger")
    def test_logger(self, mock_get_logger: MagicMock) -> None:
        log_level = self.client.settings.log_level.upper()
        log_level_num = getattr(logging, log_level)

        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        self.client.settings.log_level = self.client.log_level.lower()
        logger = self.client.logger

        mock_get_logger.assert_called_once_with("Client")
        mock_logger.setLevel.assert_called_once_with(log_level_num)

        self.assertEqual(logger, mock_logger)
        same_logger = self.client.logger
        self.assertEqual(same_logger, mock_logger)
        mock_logger.setLevel.assert_called_once()

    @patch("builtins.input", side_effect=["testuser", "1234"])
    @patch("client.grpc")
    def test_client_register_success(self, mock_grpc: MagicMock, mock_input: MagicMock) -> None:
        stub = MagicMock()
        mock_grpc.AuthStub.return_value = stub

        self.client.Register(stub)

        self.assertEqual(self.client.user, "testuser")
        stub.Register.assert_called_once()

    @patch("builtins.input", side_effect=["testuser", "not_an_int", "1234"])
    @patch("client.grpc")
    def test_client_register_retry_on_invalid_password(
        self, mock_grpc: MagicMock, mock_input: MagicMock
    ) -> None:
        stub = MagicMock()
        mock_grpc.AuthStub.return_value = stub
        with self.assertLogs(level="ERROR") as log:
            self.client.Register(stub)

        self.assertEqual(self.client.user, "testuser")
        self.assertIn("your password must be an integer", log.output[0])

    @patch("client.random.randint")
    @patch("client.AuthStub")
    def test_create_authentication_challenge(
        self, mock_stub_class: MagicMock, mock_randint: MagicMock
    ) -> None:
        mock_randint.return_value = 42  # k
        mock_stub_instance = MagicMock()
        mock_stub_instance.CreateAuthenticationChallenge.return_value = AuthenticationChallengeResponse()
        mock_stub_class.return_value = mock_stub_instance

        self.client.user = "testuser"
        self.client.user_data[self.client.user] = ClientUserData(
            user_name=self.client.user, k=mock_randint.return_value, x=123
        )
        self.client.p = 23
        self.client.q = 29
        self.client.g = 2
        self.client.h = 5
        self.client.set_variables()

        response = self.client.CreateAuthenticationChallenge(mock_stub_class())

        self.assertIsInstance(response, AuthenticationChallengeResponse)
        # TODO: confirm actual values - see test_verify_authentication_corrects
        mock_stub_instance.CreateAuthenticationChallenge.assert_called_once()

    @patch("client.AuthStub")
    def test_verify_authentication_correct(self, mock_stub_class: MagicMock) -> None:
        self.client.user = "testuser"
        self.client.user_data["testuser"] = ClientUserData(
            user_name="testuser",
            k=123,
            x=456,
        )
        self.client.q = 29

        mock_response = MagicMock()
        mock_response.session_id = "session123"
        mock_stub_instance = MagicMock()
        mock_stub_instance.VerifyAuthentication.return_value = mock_response
        mock_stub_class.return_value = mock_stub_instance

        challenge_response = MagicMock()
        challenge_response.auth_id = "auth123"
        challenge_response.c = 789

        self.client.VerifyAuthentication(mock_stub_class(), challenge_response)

        mock_stub_instance.VerifyAuthentication.assert_called_once()


if __name__ == "__main__":
    unittest.main()
