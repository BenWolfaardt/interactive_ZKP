import logging
import unittest

from unittest.mock import MagicMock, patch

import grpc

from envyaml import EnvYAML
from proto.zkp_auth_pb2 import AuthenticationChallengeRequest

from server import AuthServicer, ServerUserData


class TestServerRegister(unittest.TestCase):
    def setUp(self) -> None:
        self.server = AuthServicer()

    def test_set_variables(self) -> None:
        yaml_config = EnvYAML("./config/local.yaml", strict=False)

        self.assertEqual(self.server.p, yaml_config["public_variables"]["p"])
        self.assertEqual(self.server.q, yaml_config["public_variables"]["q"])
        self.assertEqual(self.server.g, yaml_config["public_variables"]["g"])
        self.assertEqual(self.server.h, yaml_config["public_variables"]["h"])
        self.assertEqual(self.server.flavour, yaml_config["implementation"]["flavour"])
        self.assertEqual(self.server.bits, yaml_config["implementation"]["bits"])
        self.assertEqual(self.server.log_level, yaml_config["logging"]["level"])

    @patch("src.server.logging.getLogger")
    def test_logger(self, mock_get_logger: MagicMock) -> None:
        log_level = self.server.settings.log_level.upper()
        log_level_num = getattr(logging, log_level)

        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        self.server.settings.log_level = self.server.log_level.lower()
        logger = self.server.logger

        mock_get_logger.assert_called_once_with("Server")
        mock_logger.setLevel.assert_called_once_with(log_level_num)

        self.assertEqual(logger, mock_logger)
        same_logger = self.server.logger
        self.assertEqual(same_logger, mock_logger)
        mock_logger.setLevel.assert_called_once()

    @patch("server.grpc")
    def test_server_register_new_user(self, mock_grpc: MagicMock) -> None:
        request = MagicMock()
        request.user = "newuser"
        request.y1 = 123
        request.y2 = 456
        context = MagicMock()

        response = self.server.Register(request, context)

        self.assertIsNotNone(response)
        self.assertIn(request.user, self.server.user_data)
        self.assertFalse(context.set_code.called)
        self.assertFalse(context.set_details.called)

    @patch("server.grpc.StatusCode.ALREADY_EXISTS", new_callable=lambda: grpc.StatusCode.ALREADY_EXISTS)
    @patch("server.grpc")
    def test_server_register_existing_user(self, mock_grpc: MagicMock, mock_status_code: MagicMock) -> None:
        existing_user = "existinguser"
        self.server.user_data[existing_user] = {"y1": 123, "y2": 456}
        request = MagicMock()
        request.user = existing_user
        request.y1 = 123
        request.y2 = 456
        context = MagicMock()

        self.server.Register(request, context)

        context.set_code.assert_called_once_with(grpc.StatusCode.ALREADY_EXISTS)
        context.set_details.assert_called_once()

    @patch("server.random.randint")
    def test_create_authentication_challenge(self, mock_randint: MagicMock) -> None:
        mock_randint.return_value = 42  # c
        self.server.p = 23
        self.server.q = 29
        self.server.g = 2
        self.server.h = 5

        self.server.user_data["testuser"] = ServerUserData(
            user_name="testuser",
            y1=774238805953695667,
            y2=3058468420466158753,
            c=42,
            r1=2600753519832085216,
            r2=2417243292234350294,
        )

        request = AuthenticationChallengeRequest(user="testuser", r1=7, r2=14)
        response = self.server.CreateAuthenticationChallenge(request, MagicMock())

        self.assertEqual(response.c, 42)
        self.assertIn("testuser", self.server.user_data)
        self.assertEqual(self.server.user_data["testuser"].c, 42)

    @patch("server.ServicerContext")
    def test_verify_authentication_correct(self, mock_context: MagicMock) -> None:
        self.server.g = 47
        self.server.h = 76
        self.server.p = 179
        self.server.user = "testuser"
        self.server.user_data["testuser"] = ServerUserData(
            user_name="testuser",
            c=11,
            y1=82,
            y2=66,
            r1=124,
            r2=142,
        )

        request = MagicMock()
        request.s = 53

        response = self.server.VerifyAuthentication(request, mock_context)

        self.assertEqual(response.session_id, "Eureka, you cracked the coding challenge")

    @patch("server.grpc.StatusCode")
    @patch("server.ServicerContext")
    def test_verify_authentication_incorrect(
        self, mock_context: MagicMock, mock_status_code: MagicMock
    ) -> None:
        self.server.g = 47
        self.server.h = 76
        self.server.p = 179
        self.server.user = "testuser"
        self.server.user_data["testuser"] = ServerUserData(
            user_name="testuser",
            c=11,
            y1=82,
            y2=66,
            r1=124,
            r2=142,
        )

        request = MagicMock()
        request.s = 1

        response = self.server.VerifyAuthentication(request, mock_context)

        mock_context.set_code.assert_called_once_with(grpc.StatusCode.UNAUTHENTICATED)
        expected_error_message = f"The ZKP authentication was Unsuccessful for '{self.server.user}'."
        mock_context.set_details.assert_called_once_with(expected_error_message)

        self.assertEqual(response.session_id, "")

    @patch("server.ServicerContext", create=True)
    def test_verify_authentication_unauthenticated(self, mock_context: MagicMock) -> None:
        self.server.g = 47
        self.server.h = 76
        self.server.p = 179
        self.server.q = 191
        self.server.user = "testuser"
        self.server.user_data["testuser"] = ServerUserData(
            user_name=self.server.user,
            c=11,
            y1=82,
            y2=66,
            r1=125,
            r2=143,
            k=7,
        )

        request = MagicMock()
        request.s = 10

        self.server.VerifyAuthentication(request, mock_context)

        mock_context.set_code.assert_called_once_with(grpc.StatusCode.UNAUTHENTICATED)
        expected_error_message = f"The ZKP authentication was Unsuccessful for '{self.server.user}'."
        mock_context.set_details.assert_called_once_with(expected_error_message)


if __name__ == "__main__":
    unittest.main()
