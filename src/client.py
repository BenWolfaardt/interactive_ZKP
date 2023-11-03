import logging

import grpc
import proto.zkp_auth_pb2 as zkp_auth_pb2
import proto.zkp_auth_pb2_grpc as zkp_auth_pb2_grpc


def Register(stub: zkp_auth_pb2_grpc.AuthStub) -> None:
    request = zkp_auth_pb2.RegisterRequest(
        user="Piet",  # string
        y1=5,  # int64
        y2=6,  # int64
    )

    register = stub.Register(request)

    print(register)


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
        print("-------------- CreateAuthenticationChallenge --------------")
        CreateAuthenticationChallenge(stub)
        print("-------------- VerifyAuthentication --------------")
        VerifyAuthentication(stub)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
