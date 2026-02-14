from pydantic import BaseModel

from schema_registry.user.v1 import user_pb2 as userv1


class UserCreated(BaseModel):
    user_id: str
    user_name: str
    email: str
    age: int | None = None

    def event_type(self) -> str:
        return "user.v1.created"

    def aggregate_id(self) -> str:
        return self.user_id

    def to_protobuf(self) -> userv1.UserCreated:
        return userv1.UserCreated(
            user_id=self.user_id,
            user_name=self.user_name,
            email=self.email,
            age=self.age,
        )

    @classmethod
    def from_protobuf(cls, msg: userv1.UserCreated) -> "UserCreated":
        return cls(
            user_id=msg.user_id,
            user_name=msg.user_name,
            email=msg.email,
            age=msg.age,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "UserCreated":
        msg = userv1.UserCreated.FromString(data)
        return cls.from_protobuf(msg)
