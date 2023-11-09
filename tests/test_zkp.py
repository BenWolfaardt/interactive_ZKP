import random
import unittest

from typing import Any
from unittest.mock import MagicMock, patch

from proto.zkp_auth_pb2 import AuthenticationAnswerResponse, AuthenticationChallengeResponse
from proto.zkp_auth_pb2_grpc import AuthStub

from client import Client
from server import AuthServicer


def mock_register_stub(auth_stub: AuthStub, client: Client, server: AuthServicer) -> None:
    def register_side_effect(*args: Any, **kwargs: Any) -> None:
        server.user_data[client.user] = {
            "user_name": "testuser",
            "y1": "774238805953695667",
            "y2": "3058468420466158753",
            "r1": "2600753519832085216",
            "r2": "2417243292234350294",
            "c": "1773715626668727651",
        }

    auth_stub.Register = MagicMock(side_effect=register_side_effect)
    client.Register(auth_stub)


def mock_create_authentication_challenge_stub(
    mock_stub: MagicMock, client: Client
) -> AuthenticationChallengeResponse:
    mock_stub.CreateAuthenticationChallenge = MagicMock(
        return_value=AuthenticationChallengeResponse(c=random.randint(1, client.q - 1))
    )
    return client.CreateAuthenticationChallenge(mock_stub)  # type: ignore[no-any-return]


def mock_verify_authentication_stub(
    mock_stub: MagicMock, client: Client, challenge_response: AuthenticationChallengeResponse
) -> None:
    mock_stub.VerifyAuthentication = MagicMock(
        return_value=AuthenticationAnswerResponse(session_id="dummy_session_id")
    )
    client.VerifyAuthentication(mock_stub, challenge_response)


class TestChaumPedersenProtocol(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.server = AuthServicer()

        self.server.p = 3755596804371315599
        self.server.q = 1877798402185657799
        self.server.g = 1891374716607036356
        self.server.h = 1773229570835484706

        self.client.p = self.server.p
        self.client.q = self.server.q
        self.client.g = self.server.g
        self.client.h = self.server.h

        self.client.set_variables()
        self.server.set_variables()

        self.auth_stub = MagicMock()

    @patch("builtins.input", side_effect=["testuser", "123"])
    def test_chaum_pedersen_protocol(self, mock_get_user_credentials: MagicMock) -> None:
        mock_register_stub(self.auth_stub, self.client, self.server)

        challenge_response = mock_create_authentication_challenge_stub(self.auth_stub, self.client)

        mock_verify_authentication_stub(self.auth_stub, self.client, challenge_response)

        y1 = int(self.server.user_data[self.client.user]["y1"])
        y2 = int(self.server.user_data[self.client.user]["y2"])
        r1_original = int(self.server.user_data[self.client.user]["r1"])
        r2_original = int(self.server.user_data[self.client.user]["r2"])
        c = int(self.server.user_data[self.client.user]["c"])
        self.client.user_data[self.client.user].k = 1559190552114951134

        s = (
            int(self.client.user_data[self.client.user].k)
            - (c * int(self.client.user_data[self.client.user].x))
        ) % self.server.q

        r1_new = (pow(self.server.g, s, self.server.p) * pow(y1, c, self.server.p)) % self.server.p
        r2_new = (pow(self.server.h, s, self.server.p) * pow(y2, c, self.server.p)) % self.server.p

        accept = (r1_new == r1_original) and (r2_new == r2_original)

        self.assertTrue(accept, "The Chaum-Pedersen verification should succeed.")


if __name__ == "__main__":
    unittest.main()
