import datetime

from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
event_type: _descriptor.FieldDescriptor
IS_AGGREGATE_ID_FIELD_NUMBER: _ClassVar[int]
is_aggregate_id: _descriptor.FieldDescriptor

class Envelope(_message.Message):
    __slots__ = ("id", "source", "specversion", "type", "attributes", "binary_data", "text_data", "time")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: CloudEventAttributeValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[CloudEventAttributeValue, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SPECVERSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    BINARY_DATA_FIELD_NUMBER: _ClassVar[int]
    TEXT_DATA_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    source: str
    specversion: str
    type: str
    attributes: _containers.MessageMap[str, CloudEventAttributeValue]
    binary_data: bytes
    text_data: str
    time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., source: _Optional[str] = ..., specversion: _Optional[str] = ..., type: _Optional[str] = ..., attributes: _Optional[_Mapping[str, CloudEventAttributeValue]] = ..., binary_data: _Optional[bytes] = ..., text_data: _Optional[str] = ..., time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CloudEventAttributeValue(_message.Message):
    __slots__ = ("ce_boolean", "ce_integer", "ce_string", "ce_bytes", "ce_uri", "ce_uri_reference", "ce_timestamp")
    CE_BOOLEAN_FIELD_NUMBER: _ClassVar[int]
    CE_INTEGER_FIELD_NUMBER: _ClassVar[int]
    CE_STRING_FIELD_NUMBER: _ClassVar[int]
    CE_BYTES_FIELD_NUMBER: _ClassVar[int]
    CE_URI_FIELD_NUMBER: _ClassVar[int]
    CE_URI_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    CE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ce_boolean: bool
    ce_integer: int
    ce_string: str
    ce_bytes: bytes
    ce_uri: str
    ce_uri_reference: str
    ce_timestamp: _timestamp_pb2.Timestamp
    def __init__(self, ce_boolean: _Optional[bool] = ..., ce_integer: _Optional[int] = ..., ce_string: _Optional[str] = ..., ce_bytes: _Optional[bytes] = ..., ce_uri: _Optional[str] = ..., ce_uri_reference: _Optional[str] = ..., ce_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
