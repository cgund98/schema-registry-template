from google.protobuf import descriptor_pb2 as _descriptor_pb2
from schema_registry.registry.v1 import envelope_pb2 as _envelope_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UserCreated(_message.Message):
    __slots__ = ("user_id", "user_name", "email", "age")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    user_name: str
    email: str
    age: int
    def __init__(self, user_id: _Optional[str] = ..., user_name: _Optional[str] = ..., email: _Optional[str] = ..., age: _Optional[int] = ...) -> None: ...

class UserUpdated(_message.Message):
    __slots__ = ("user_id", "user_name", "email", "age")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    AGE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    user_name: str
    email: str
    age: int
    def __init__(self, user_id: _Optional[str] = ..., user_name: _Optional[str] = ..., email: _Optional[str] = ..., age: _Optional[int] = ...) -> None: ...

class UserDeleted(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...
