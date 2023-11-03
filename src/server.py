import logging

from concurrent import futures
from typing import Any

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

    def Register(self, request: RegisterRequest, context: ServicerContext) -> Any:
        # logging.info("hoyah")
        # context.
        return RegisterResponse()

    def CreateAuthenticationChallenge(
        self, request: AuthenticationChallengeRequest, context: ServicerContext
    ) -> Any:
        # TODO calculate response

        return AuthenticationChallengeResponse(
            auth_id="string",  # string
            c=5,  # int64
        )

    def VerifyAuthentication(self, request: AuthenticationAnswerRequest, context: ServicerContext) -> Any:
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
