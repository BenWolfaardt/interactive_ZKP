import logging
import sys

import grpc
import proto.zkp_auth_pb2 as zkp_auth_pb2
import proto.zkp_auth_pb2_grpc as zkp_auth_pb2_grpc


# TODO: test limitations of variables in the system?
g: int = 1
h: int = 2


# TODO: allow stdin to define the secret x (it is a number, validate that)
# TODO: Allow the user to re-register if the user already exists? add this to future considerations
# TODO: data validation with pydantic?
def Register(stub: zkp_auth_pb2_grpc.AuthStub) -> None:
    user: str = "Piet"
    x: int = 12

    y1: int = g**x
    y2: int = h**x

    try:
        request = zkp_auth_pb2.RegisterRequest(
            user=user,
            y1=y1,
            y2=y2,
        )
    except ValueError as e:
        logging.exception(f"ValueError: {e}")
        sys.exit()

    try:
        stub.Register(request)
        logging.debug(f"{user=} has registered with {y1=} and {y2=}")
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.ALREADY_EXISTS:
            logging.error(f"{rpc_error.details()}")
        else:
            logging.exception(f"Caught a gRPC error: {rpc_error}")
        sys.exit()
    except Exception as e:
        logging.exception(f"Caught an exception: {e}")
        sys.exit()


def CreateAuthenticationChallenge(stub: zkp_auth_pb2_grpc.AuthStub) -> None:
    request = zkp_auth_pb2.AuthenticationChallengeRequest(
        user="Ben",  # string
        r1=5,  # int64
        r2=6,  # int64
    )

    challenge = stub.CreateAuthenticationChallenge(request)

    print(challenge)


def VerifyAuthentication(stub: zkp_auth_pb2_grpc.AuthStub) -> None:
    request = zkp_auth_pb2.AuthenticationAnswerRequest(
        auth_id="1337",  # string
        s=5,  # int64
    )

    verify = stub.VerifyAuthentication(request)

    print(verify)


def run() -> None:
    with grpc.insecure_channel("localhost:50051") as channel:
        stub: zkp_auth_pb2_grpc.AuthStub = zkp_auth_pb2_grpc.AuthStub(channel)
        print("-------------- Register --------------")
        Register(stub)
        # print("-------------- CreateAuthenticationChallenge --------------")
        # CreateAuthenticationChallenge(stub)
        # print("-------------- VerifyAuthentication --------------")
        # VerifyAuthentication(stub)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
