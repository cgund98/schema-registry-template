import uuid

from schema_registry.registry.v1 import Envelope
from schema_registry.user.v1.user_created import UserCreated


def test_create_event() -> None:
    detail = UserCreated(
        user_id="123",
        user_name="John Doe",
        email="john.doe@example.com",
        age=30,
    )
    envelope = Envelope.build(
        data_message=detail.to_protobuf(), source="test-source", extensions={"correlation_id": "123"}
    )

    assert envelope.id is not None
    assert isinstance(envelope.id, str)
    assert uuid.UUID(envelope.id) is not None
    assert envelope.type == "user.v1.created"
    assert envelope.time is not None
    assert envelope.data is not None
    assert envelope.specversion == "1.0"
    assert envelope.extensions == {"correlation_id": "123"}


def test_deserialize_event() -> None:
    detail = UserCreated(
        user_id="123",
        user_name="John Doe",
        email="john.doe@example.com",
        age=30,
    )
    envelope = Envelope.build(
        data_message=detail.to_protobuf(), source="test-source", extensions={"correlation_id": "123"}
    )

    deserialized_envelope = Envelope.from_protobuf(envelope.to_protobuf())
    assert deserialized_envelope.id == envelope.id
    assert deserialized_envelope.type == envelope.type
    assert deserialized_envelope.time == envelope.time
    assert deserialized_envelope.data == envelope.data
    assert deserialized_envelope.source == envelope.source
    assert deserialized_envelope.specversion == envelope.specversion
    assert deserialized_envelope.extensions == envelope.extensions
