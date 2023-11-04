import logging
import random
import sys

from collections import defaultdict

import grpc

from proto.zkp_auth_pb2 import (
    AuthenticationAnswerRequest,
    AuthenticationAnswerResponse,
    AuthenticationChallengeRequest,
    AuthenticationChallengeResponse,
    RegisterRequest,
)
from proto.zkp_auth_pb2_grpc import AuthStub


# TODO: test limitations of variables in the system?
# TODO: get fom yaml config
g: int = 1
h: int = 2


class Client:
    def __init__(self) -> None:
        super().__init__()
        self.user: str | None = None
        self.user_data: dict = defaultdict(set)

    # TODO: data validation with pydantic?
    def Register(self, stub: AuthStub) -> None:
        # self.user = input("Enter your username: ")

        # while True:
        #     try:
        #         x = int(input("Enter your secret password (an integer): "))
        #         break
        #     except ValueError:
        #         logging.error(f"{self.user} your password must be an integer.")

        self.user = "Bob"
        x = 3

        y1: int = g**x
        y2: int = h**x

        try:
            request = RegisterRequest(
                user=self.user,
                y1=y1,
                y2=y2,
            )
        # TODO: if we know the limits on this error we can implement it at the stdin part
        except ValueError as e:
            logging.exception(f"ValueError: {e}")
            sys.exit()

        try:
            stub.Register(request)
            logging.info(f"{self.user}, you have succesfully registered")
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.ALREADY_EXISTS:
                logging.error(f"{rpc_error.details()}")
            else:
                logging.exception(f"Caught a gRPC error: {rpc_error}")
            sys.exit()
        except Exception as e:
            logging.exception(f"Caught an exception: {e}")
            sys.exit()

        self.user_data[self.user] = {
            "user_name": self.user,
            "x": x,
        }

    def CreateAuthenticationChallenge(self, stub: AuthStub) -> AuthenticationChallengeResponse:
        if self.user:
            user: str = self.user

        k: int = random.randint(0, 10)
        r1: int = g**k
        r2: int = h**k

        request = AuthenticationChallengeRequest(
            user=user,
            r1=r1,
            r2=r2,
        )

        self.user_data[self.user]["k"] = k

        logging.debug(f"The authentication challenge variables for {user} are: {k=}, {r1=}, {r2=}")
        response: AuthenticationChallengeResponse = stub.CreateAuthenticationChallenge(request)
        return response

    def VerifyAuthentication(
        self, stub: AuthStub, authentication_challenge_response: AuthenticationChallengeResponse
    ) -> None:
        auth_id: str = authentication_challenge_response.auth_id
        c: int = authentication_challenge_response.c
        k: int = self.user_data[self.user]["k"]
        x: int = self.user_data[self.user]["x"]

        # TODO figure out the maths
        s = k - c * x

        request = AuthenticationAnswerRequest(
            auth_id=auth_id,
            s=s,
        )

        response: AuthenticationAnswerResponse = stub.VerifyAuthentication(request)
        session_id = response.session_id
        logging.debug(f"{self.user}'s {session_id=}")

    def run(self) -> None:
        with grpc.insecure_channel("localhost:50051") as channel:
            stub: AuthStub = AuthStub(channel)
            print("-------------- Register --------------")
            self.Register(stub)
            print("-------------- CreateAuthenticationChallenge --------------")
            authentication_challenge_response = self.CreateAuthenticationChallenge(stub)
            print("-------------- VerifyAuthentication --------------")
            self.VerifyAuthentication(stub, authentication_challenge_response)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    c = Client()
    c.run()
