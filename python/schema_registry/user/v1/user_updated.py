from pydantic import BaseModel

from schema_registry.user.v1 import user_pb2 as userv1


class UserUpdated(BaseModel):
    user_id: str
    user_name: str
    email: str
    age: int | None = None

    def aggregate_id(self) -> str:
        return self.user_id

    def to_protobuf(self) -> userv1.UserUpdated:
        return userv1.UserUpdated(
            user_id=self.user_id,
            user_name=self.user_name,
            email=self.email,
            age=self.age,
        )

    @classmethod
    def from_protobuf(cls, msg: userv1.UserUpdated) -> "UserUpdated":
        return cls(
            user_id=msg.user_id,
            user_name=msg.user_name,
            email=msg.email,
            age=msg.age,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "UserUpdated":
        msg = userv1.UserUpdated.FromString(data)
        return cls.from_protobuf(msg)
