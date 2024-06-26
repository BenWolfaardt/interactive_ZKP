"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.message
import sys

if sys.version_info >= (3, 8):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing_extensions.final
class RegisterRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    USER_FIELD_NUMBER: builtins.int
    Y1_FIELD_NUMBER: builtins.int
    Y2_FIELD_NUMBER: builtins.int
    user: builtins.str
    y1: builtins.int
    y2: builtins.int
    def __init__(
        self,
        *,
        user: builtins.str = ...,
        y1: builtins.int = ...,
        y2: builtins.int = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["user", b"user", "y1", b"y1", "y2", b"y2"]
    ) -> None: ...

global___RegisterRequest = RegisterRequest

@typing_extensions.final
class RegisterResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    def __init__(
        self,
    ) -> None: ...

global___RegisterResponse = RegisterResponse

@typing_extensions.final
class AuthenticationChallengeRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    USER_FIELD_NUMBER: builtins.int
    R1_FIELD_NUMBER: builtins.int
    R2_FIELD_NUMBER: builtins.int
    user: builtins.str
    r1: builtins.int
    r2: builtins.int
    def __init__(
        self,
        *,
        user: builtins.str = ...,
        r1: builtins.int = ...,
        r2: builtins.int = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["r1", b"r1", "r2", b"r2", "user", b"user"]
    ) -> None: ...

global___AuthenticationChallengeRequest = AuthenticationChallengeRequest

@typing_extensions.final
class AuthenticationChallengeResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    AUTH_ID_FIELD_NUMBER: builtins.int
    C_FIELD_NUMBER: builtins.int
    auth_id: builtins.str
    c: builtins.int
    def __init__(
        self,
        *,
        auth_id: builtins.str = ...,
        c: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["auth_id", b"auth_id", "c", b"c"]) -> None: ...

global___AuthenticationChallengeResponse = AuthenticationChallengeResponse

@typing_extensions.final
class AuthenticationAnswerRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    AUTH_ID_FIELD_NUMBER: builtins.int
    S_FIELD_NUMBER: builtins.int
    auth_id: builtins.str
    s: builtins.int
    def __init__(
        self,
        *,
        auth_id: builtins.str = ...,
        s: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["auth_id", b"auth_id", "s", b"s"]) -> None: ...

global___AuthenticationAnswerRequest = AuthenticationAnswerRequest

@typing_extensions.final
class AuthenticationAnswerResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SESSION_ID_FIELD_NUMBER: builtins.int
    session_id: builtins.str
    def __init__(
        self,
        *,
        session_id: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["session_id", b"session_id"]) -> None: ...

global___AuthenticationAnswerResponse = AuthenticationAnswerResponse
