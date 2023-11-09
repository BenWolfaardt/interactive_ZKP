import logging
import random
import uuid

from concurrent import futures

import grpc
import proto.zkp_auth_pb2_grpc as zkp_auth_pb2_grpc

from grpc import ServicerContext
from proto.zkp_auth_pb2 import (
    AuthenticationAnswerRequest,
    AuthenticationAnswerResponse,
    AuthenticationChallengeRequest,
    AuthenticationChallengeResponse,
    RegisterRequest,
    RegisterResponse,
)
from pydantic import BaseModel

from src.settings import Settings, log_level_mapping, zkp_settings


class ServerUserData(BaseModel):
    user_name: str
    y1: int
    y2: int
    c: int
    r1: int
    r2: int


class AuthServicer(zkp_auth_pb2_grpc.AuthServicer):
    # service config
    _logger: logging.Logger | None = None
    settings: Settings | None = None
    # user session details
    user: str
    user_data: dict[str, ServerUserData] = {}

    @classmethod
    def set_variables(cls) -> None:
        if cls.settings is None:
            cls.settings = zkp_settings

    def __init__(self) -> None:
        if AuthServicer.settings is None:
            AuthServicer.set_variables()

        if AuthServicer.settings:
            # public variables
            self.p = AuthServicer.settings.p
            self.q = AuthServicer.settings.q
            self.g = AuthServicer.settings.g
            self.h = AuthServicer.settings.h
            self.flavour = AuthServicer.settings.flavour
            self.bits = AuthServicer.settings.bits
            self.log_level = AuthServicer.settings.log_level

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            self._logger = logging.getLogger("Server")
            self._logger.setLevel(log_level_mapping[self.log_level])
        return self._logger

    def Register(self, request: RegisterRequest, context: ServicerContext) -> RegisterResponse:
        self.user = request.user
        y1: int = request.y1
        y2: int = request.y2

        if self.user in self.user_data:
            e = f"User '{self.user}' already exists"
            self.logger.error(e)
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(e)
        else:
            self.user_data[self.user] = ServerUserData(user_name=self.user, y1=y1, y2=y2)
            self.logger.debug(f"{self.user} has registered with {y1=} and {y2=}")

        return RegisterResponse()

    def CreateAuthenticationChallenge(
        self, request: AuthenticationChallengeRequest, context: ServicerContext
    ) -> AuthenticationChallengeResponse:
        auth_id: uuid.UUID = uuid.uuid4()
        user: str = request.user
        r1: int = request.r1
        r2: int = request.r2
        c: int = random.randint(1, self.q - 1)
        self.logger.debug(f"The random challenge {c=}")

        self.user_data[user].c = c
        self.user_data[user].r1 = r1
        self.user_data[user].r2 = r2
        self.logger.debug(f"{user} has parsed {r1=} and {r2=}")

        return AuthenticationChallengeResponse(
            auth_id=str(auth_id),
            c=c,
        )

    def VerifyAuthentication(
        self, request: AuthenticationAnswerRequest, context: ServicerContext
    ) -> AuthenticationAnswerResponse:
        s: int = request.s

        c = self.user_data[self.user].c
        y1 = self.user_data[self.user].y1
        y2 = self.user_data[self.user].y2
        r1_original = self.user_data[self.user].r1
        r2_original = self.user_data[self.user].r2

        r1_new = (pow(self.g, s, self.p) * pow(y1, c, self.p)) % self.p
        r2_new = (pow(self.h, s, self.p) * pow(y2, c, self.p)) % self.p

        # TODO: add expiration to the auth_id
        # TODO: reset the auth_id as it's been used
        if r1_new == r1_original and r2_new == r2_original:
            self.logger.info(f"{self.user} has successfully been authenticated")
            return AuthenticationAnswerResponse(
                session_id="Eureka, you cracked the coding challenge",
            )
        else:
            e = f"The ZKP authentication was Unsuccessful for '{self.user}'."
            self.logger.error(e)
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(e)
            return AuthenticationAnswerResponse()


def main() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    zkp_auth_pb2_grpc.add_AuthServicer_to_server(AuthServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    AuthServicer.set_variables()
    s = AuthServicer()
    main()
