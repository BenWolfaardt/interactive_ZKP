import logging
import random
import sys

import grpc
import proto.zkp_auth_pb2 as zkp_auth_pb2
import proto.zkp_auth_pb2_grpc as zkp_auth_pb2_grpc


# TODO: test limitations of variables in the system?
# TODO: get fom yaml config
g: int = 1
h: int = 2


class Client:
    def __init__(self) -> None:
        super().__init__()
        self.user: str | None = None
        self.user_data: dict = {}

    # TODO: allow stdin to define the secret x (it is a number, validate that)
    # TODO: data validation with pydantic?
    def Register(self, stub: zkp_auth_pb2_grpc.AuthStub) -> None:
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
            request = zkp_auth_pb2.RegisterRequest(
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

    def CreateAuthenticationChallenge(self, stub: zkp_auth_pb2_grpc.AuthStub) -> None:
        if self.user:
            user: str = self.user

        k: int = random.randint(0, 10)
        r1: int = g**k
        r2: int = h**k

        request = zkp_auth_pb2.AuthenticationChallengeRequest(
            user=user,
            r1=r1,
            r2=r2,
        )

        logging.debug(f"The authentication challenge variables for {user} are: {k=}, {r1=}, {r2=}")
        stub.CreateAuthenticationChallenge(request)

    def VerifyAuthentication(self, stub: zkp_auth_pb2_grpc.AuthStub) -> None:
        request = zkp_auth_pb2.AuthenticationAnswerRequest(
            auth_id="1337",  # string
            s=5,  # int64
        )

        stub.VerifyAuthentication(request)

    def run(self) -> None:
        with grpc.insecure_channel("localhost:50051") as channel:
            stub: zkp_auth_pb2_grpc.AuthStub = zkp_auth_pb2_grpc.AuthStub(channel)
            print("-------------- Register --------------")
            self.Register(stub)
            print("-------------- CreateAuthenticationChallenge --------------")
            self.CreateAuthenticationChallenge(stub)
            # print("-------------- VerifyAuthentication --------------")
            # VerifyAuthentication(stub)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    c = Client()
    c.run()
