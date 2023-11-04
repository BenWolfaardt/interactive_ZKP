import logging
import random
import uuid

from collections import defaultdict
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


# TODO: get fom yaml config
g: int = 1
h: int = 2


class AuthServicer(zkp_auth_pb2_grpc.AuthServicer):
    def __init__(self) -> None:
        super().__init__()
        self.user: str | None = None
        self.user_data: dict = defaultdict(set)

    def Register(self, request: RegisterRequest, context: ServicerContext) -> RegisterResponse:
        self.user = request.user
        y1: int = request.y1
        y2: int = request.y2

        if self.user in self.user_data:
            e = f"User '{self.user}' already exists"
            logging.error(e)
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(e)
        else:
            self.user_data[self.user] = {
                "user_name": self.user,
                "y1": y1,
                "y2": y2,
            }
            logging.debug(f"{self.user} has registered with {y1=} and {y2=}")

        return RegisterResponse()

    def CreateAuthenticationChallenge(
        self, request: AuthenticationChallengeRequest, context: ServicerContext
    ) -> AuthenticationChallengeResponse:
        c: int = random.randint(0, 10)
        auth_id: uuid.UUID = uuid.uuid4()
        user: str = request.user
        r1: int = request.r1
        r2: int = request.r2

        self.user_data[user]["c"] = c
        self.user_data[user]["r1"] = r1
        self.user_data[user]["r2"] = r2
        logging.debug(f"{user} has parsed {r1=} and {r2=}")

        return AuthenticationChallengeResponse(
            auth_id=str(auth_id),
            c=c,
        )

    def VerifyAuthentication(
        self, request: AuthenticationAnswerRequest, context: ServicerContext
    ) -> AuthenticationAnswerResponse:
        s: int = request.s
        c: int = self.user_data[self.user]["c"]
        y1: int = self.user_data[self.user]["y1"]
        y2: int = self.user_data[self.user]["y2"]
        r1_original: int = self.user_data[self.user]["r1"]
        r2_original: int = self.user_data[self.user]["r2"]

        r1_new = g**s * y1**c
        r2_new = h**s * y2**c

        if r1_new == r1_original and r2_new == r2_original:
            logging.info(f"{self.user} has successfully been authenticated")
            return AuthenticationAnswerResponse(
                session_id="Eureka, you cracked the coding challenge",
            )
        else:
            e = f"The ZKP authentication was Unsuccessful for '{self.user}'."
            logging.error(e)
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(e)
            return AuthenticationAnswerResponse()


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    zkp_auth_pb2_grpc.add_AuthServicer_to_server(AuthServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    serve()
