import datetime
import uuid

from pydantic import AwareDatetime, BaseModel, ConfigDict

from schema_registry.registry.v1.envelope_pb2 import Envelope as EnvelopeProto
from schema_registry.registry.v1.event_type import get_event_type
from schema_registry.registry.v1.message import ProtobufMessage


class Envelope(BaseModel):
    """
    CloudEvents-compatible envelope DTO.
    """

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: str
    type: str
    time: AwareDatetime
    data: bytes
    source: str
    specversion: str = "1.0"

    extensions: dict[str, str]

    def to_protobuf(self) -> EnvelopeProto:
        """
        Serialize the Envelope to a protobuf message.
        """
        proto = EnvelopeProto(
            id=self.id,
            type=self.type,
            source=self.source,
            time=self.time,
            specversion=self.specversion,
        )

        proto.binary_data = self.data

        # CloudEvents specifies extensions as a map in Protobuf
        for key, value in self.extensions.items():
            proto.attributes[key].ce_string = value

        proto.time.FromDatetime(self.time)
        return proto

    @classmethod
    def from_protobuf(cls, envelope: EnvelopeProto) -> "Envelope":
        """
        Deserialize the Envelope from a protobuf message.
        """
        return cls(
            id=envelope.id,
            type=envelope.type,
            time=envelope.time.ToDatetime(datetime.UTC),
            data=envelope.binary_data,
            source=envelope.source,
            specversion=envelope.specversion,
            extensions={key: value.ce_string for key, value in envelope.attributes.items()},
        )

    @classmethod
    def build(
        cls, *, data_message: ProtobufMessage, source: str, extensions: dict[str, str] | None = None
    ) -> "Envelope":
        """
        Build an Envelope from a data message and source.
        """
        if extensions is None:
            extensions = {}

        return cls(
            id=uuid.uuid4().hex,
            type=get_event_type(data_message),
            time=datetime.datetime.now(datetime.UTC),
            data=data_message.SerializeToString(),
            source=source,
            extensions=extensions,
        )
