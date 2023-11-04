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


class AuthServicer(zkp_auth_pb2_grpc.AuthServicer):
    """Provides methods that implement functionality of AuthServicer server."""

    # TODO: Consider saving the current user in a self for reference in the program
    def __init__(self) -> None:
        super().__init__()
        self.user_data: dict = {}

    def Register(self, request: RegisterRequest, context: ServicerContext) -> RegisterResponse:
        user: str = request.user
        y1: int = request.y1
        y2: int = request.y2

        if user in self.user_data:
            e = f"User '{user}' already exists"
            logging.error(e)
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(e)
        else:
            self.user_data[user] = {
                "user_name": user,
                "y1": y1,
                "y2": y2,
            }
            logging.debug(f"{user=} has registered with {y1=} and {y2=}")

        return RegisterResponse()

    def CreateAuthenticationChallenge(
        self, request: AuthenticationChallengeRequest, context: ServicerContext
    ) -> AuthenticationChallengeResponse:
        c: int = random.randint(0, 1_000_000)
        auth_id: uuid.UUID = uuid.uuid4()
        user: str = request.user
        r1: int = request.r1
        r2: int = request.r2

        self.user_data[user] = {
            "r1": r1,
            "r2": r2,
        }
        logging.debug(f"{user=} has parsed {r1=} and {r2=}")

        return AuthenticationChallengeResponse(
            auth_id=str(auth_id),
            c=c,
        )

    def VerifyAuthentication(
        self, request: AuthenticationAnswerRequest, context: ServicerContext
    ) -> AuthenticationAnswerResponse:
        # TODO calculate response

        return AuthenticationAnswerResponse(
            session_id="7331",  # string
        )


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    zkp_auth_pb2_grpc.add_AuthServicer_to_server(AuthServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    serve()
