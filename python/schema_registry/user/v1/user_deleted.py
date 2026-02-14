from pydantic import BaseModel

from schema_registry.user.v1 import user_pb2 as userv1


class UserDeleted(BaseModel):
    user_id: str

    def event_type(self) -> str:
        return "user.v1.deleted"

    def aggregate_id(self) -> str:
        return self.user_id

    def to_protobuf(self) -> userv1.UserDeleted:
        return userv1.UserDeleted(
            user_id=self.user_id,
        )

    @classmethod
    def from_protobuf(cls, msg: userv1.UserDeleted) -> "UserDeleted":
        return cls(
            user_id=msg.user_id,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "UserDeleted":
        msg = userv1.UserDeleted.FromString(data)
        return cls.from_protobuf(msg)
