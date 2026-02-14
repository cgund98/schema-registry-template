import pytest

from schema_registry.registry.v1.envelope import get_event_type
from schema_registry.registry.v1.envelope_pb2 import Envelope as EnvelopeProto
from schema_registry.user.v1 import user_pb2 as userv1


def test_get_event_type() -> None:
    assert get_event_type(userv1.UserCreated()) == "user.v1.created"


def test_get_event_type_invalid_message() -> None:
    with pytest.raises(TypeError, match="Expected Protobuf Message, got str"):
        get_event_type("not a protobuf message")


def test_get_event_type_message_without_event_type() -> None:
    with pytest.raises(
        ValueError, match="Message 'registry.v1.Envelope' is missing the registry.v1.event_type option."
    ):
        get_event_type(EnvelopeProto())
