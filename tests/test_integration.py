# import logging
# import threading
# import unittest
# import grpc
# import time
# from client import Client
# from proto.zkp_auth_pb2 import AuthenticationAnswerRequest, AuthenticationAnswerResponse, AuthenticationChallengeRequest, AuthenticationChallengeResponse, RegisterRequest
# from proto.zkp_auth_pb2_grpc import AuthStub

# from server import AuthServicer, main as server_main

# def run_test_server():
#     logging.basicConfig()
#     AuthServicer.set_variables()
#     s = AuthServicer()
#     server_main()


# class TestAuthIntegration(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.server_thread = threading.Thread(target=run_test_server, daemon=True)
#         cls.server_thread.start()
#         time.sleep(1)

#         cls.channel = grpc.insecure_channel('localhost:50051')
#         cls.stub = AuthStub(cls.channel)
#         cls.client = Client()
#         cls.client.set_variables()

#     @classmethod
#     def tearDownClass(cls):
#         cls.channel.close()
#         cls.server_thread.join()

#     def test_registration_and_authentication_flow(self):
#         register_request = RegisterRequest(
#             user="Ben",
#             y1=82,
#             y2=66,
#         )
#         self.stub.Register(register_request)

#         self.client.Register(self.stub)

#         # challenge_request = AuthenticationChallengeRequest(
#         #     user="Ben",
#         #     r1=20,
#         #     r2=173,
#         # )
#         # challenge_response: AuthenticationChallengeResponse = self.stub.CreateAuthenticationChallenge(challenge_request)
#         # challenge_response.c = 24
#         # self.assertIsNotNone(challenge_response)

#         # verify_request = AuthenticationAnswerRequest(
#         #     auth_id=challenge_response.auth_id,
#         #     s=64,
#         # )
#         # verify_response: AuthenticationAnswerResponse = self.stub.VerifyAuthentication(verify_request)
#         # self.assertTrue(verify_response.authenticated)


#     # More test cases as needed...


# if __name__ == '__main__':
#     unittest.main()
