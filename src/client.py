import argparse
import logging
import random
import sys

from time import sleep

import grpc

from proto.zkp_auth_pb2 import (
    AuthenticationAnswerRequest,
    AuthenticationAnswerResponse,
    AuthenticationChallengeRequest,
    AuthenticationChallengeResponse,
    RegisterRequest,
)
from proto.zkp_auth_pb2_grpc import AuthStub
from pydantic import BaseModel

from src.settings import Flavour, Settings, log_level_mapping, zkp_settings


class ClientUserData(BaseModel):
    user_name: str
    x: int
    k: int = 0


class Client:
    def __init__(self) -> None:
        # service config
        self.settings: Settings | None = None
        self._logger: logging.Logger | None = None
        # public variables
        self.q: int = 0
        self.g: int = 0
        self.h: int = 0
        self.flavour: Flavour = Flavour.EXPONENTIATIONS
        self.bits: int = 0
        self.log_level: str = "info"
        # user session details
        self.user: str
        self.user_data: dict[str, ClientUserData] = {}

    def set_variables(self) -> None:
        self.settings = zkp_settings
        self.p = self.settings.p
        self.q = self.settings.q
        self.g = self.settings.g
        self.h = self.settings.h
        self.flavour = self.settings.flavour
        self.bits = self.settings.bits
        self.log_level = self.settings.log_level

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            self._logger = logging.getLogger("Client")
            self._logger.setLevel(log_level_mapping[self.log_level])
        return self._logger

    def Register(self, stub: AuthStub) -> None:
        self.user = input("Enter your username: ")

        while True:
            try:
                x = int(input("Enter your secret password (an integer): "))
                break
            except ValueError:
                self.logger.error(f"{self.user} your password must be an integer.")

        y1: int = pow(self.g, x, self.p)
        y2: int = pow(self.h, x, self.p)

        request = RegisterRequest(
            user=self.user,
            y1=y1,
            y2=y2,
        )

        try:
            stub.Register(request)
            self.logger.info(f"{self.user}, you have succesfully registered")
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.ALREADY_EXISTS:
                self.logger.error(f"{rpc_error.details()}")
            else:
                self.logger.exception(f"Caught a gRPC error: {rpc_error}")
                sys.exit()
        except Exception as e:
            self.logger.exception(f"Caught an exception: {e}")
            sys.exit()

        self.user_data[self.user] = ClientUserData(user_name=self.user, x=x)

    def CreateAuthenticationChallenge(self, stub: AuthStub) -> AuthenticationChallengeResponse:
        k: int = random.randint(1, self.q - 1)
        self.logger.debug(f"The random {k=}")
        r1: int = pow(self.g, k, self.p)
        r2: int = pow(self.h, k, self.p)

        self.user_data[self.user].k = k

        request = AuthenticationChallengeRequest(
            user=self.user,
            r1=r1,
            r2=r2,
        )

        self.logger.debug(f"The authentication challenge variables for {self.user} are: {k=}, {r1=}, {r2=}")
        response: AuthenticationChallengeResponse = stub.CreateAuthenticationChallenge(request)
        return response

    def VerifyAuthentication(
        self, stub: AuthStub, authentication_challenge_response: AuthenticationChallengeResponse
    ) -> None:
        auth_id: str = authentication_challenge_response.auth_id
        c: int = authentication_challenge_response.c
        k: int = self.user_data[self.user].k
        x: int = self.user_data[self.user].x

        s: int = (k - c * x) % self.q
        self.logger.debug(f"The computed {s=}")

        request = AuthenticationAnswerRequest(
            auth_id=auth_id,
            s=s,
        )

        try:
            response: AuthenticationAnswerResponse = stub.VerifyAuthentication(request)
            session_id = response.session_id
            self.logger.info(f"{self.user}'s {session_id=}")
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAUTHENTICATED:
                self.logger.error(f"{rpc_error.details()}")
            else:
                self.logger.exception(f"Caught a gRPC error: {rpc_error}")
            sys.exit()
        except Exception as e:
            self.logger.exception(f"Caught an exception: {e}")
            sys.exit()


def main() -> None:
    registered = False

    parser = argparse.ArgumentParser(description="Client for Chaum-Pederson Zero-Knowledge Proof")
    parser.add_argument("mode", choices=["local", "docker"], help="Choose 'local' or 'docker'")

    args = parser.parse_args()

    host = "server" if args.mode == "docker" else "localhost"

    while True:
        if not registered:
            print("You need to register before logging in.")
            action = "register"
        else:
            action = input("Please choose your desired action ('register', 'login' or 'exit'):\n")

        if action == "register":
            with grpc.insecure_channel(f"{host}:50051") as channel:
                stub: AuthStub = AuthStub(channel)
                c.Register(stub)
                registered = True
        elif action == "login":
            if not registered:
                print("Please register before trying to log in.")
            else:
                with grpc.insecure_channel(f"{host}:50051") as channel:
                    stub = AuthStub(channel)
                    authentication_challenge_response = c.CreateAuthenticationChallenge(stub)
                    c.VerifyAuthentication(stub, authentication_challenge_response)
        elif action == "exit":
            print("Exiting the application.")
            sys.exit(0)
        else:
            print("Invalid action. Please choose 'register', 'login', or 'exit'.")

        sleep(1)


if __name__ == "__main__":
    logging.basicConfig()
    c = Client()
    c.set_variables()
    main()
