from typing import Any

from google.protobuf.message import Message

from schema_registry.registry.v1 import envelope_pb2 as registryv1


def get_event_type(message: Any) -> str:
    """
    Retrieves the event type from a Protobuf message descriptor.
    """
    # 1. Ensure we are dealing with a generated Protobuf message instance
    if not isinstance(message, Message):
        raise TypeError(f"Expected Protobuf Message, got {type(message).__name__}")

    options = message.DESCRIPTOR.GetOptions()

    # 2. Check if the extension is actually set on this message
    # In Editions, checking for extension presence is standard
    if not options.HasExtension(registryv1.event_type):  # type: ignore
        raise ValueError(f"Message '{message.DESCRIPTOR.full_name}' is missing the registry.v1.event_type option.")

    event_type = options.Extensions[registryv1.event_type]  # type: ignore

    # 3. Ensure the string isn't just whitespace or empty
    if not event_type or not event_type.strip():
        raise ValueError(f"Detail type for '{message.DESCRIPTOR.full_name}' cannot be empty.")

    return str(event_type)
