from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EmptyMessage(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class TestConnectionResponse(_message.Message):
    __slots__ = ["pubkey", "version"]
    PUBKEY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    pubkey: str
    version: str
    def __init__(self, pubkey: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class InterceptChannelOpenRequest(_message.Message):
    __slots__ = ["message_id", "timestamp", "peer_pubkey"]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PEER_PUBKEY_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    timestamp: float
    peer_pubkey: str
    def __init__(self, message_id: _Optional[str] = ..., timestamp: _Optional[float] = ..., peer_pubkey: _Optional[str] = ...) -> None: ...

class InterceptChannelOpenResponse(_message.Message):
    __slots__ = ["message_id", "orig_timestamp", "allow", "reject_reason"]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    ORIG_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ALLOW_FIELD_NUMBER: _ClassVar[int]
    REJECT_REASON_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    orig_timestamp: float
    allow: bool
    reject_reason: str
    def __init__(self, message_id: _Optional[str] = ..., orig_timestamp: _Optional[float] = ..., allow: bool = ..., reject_reason: _Optional[str] = ...) -> None: ...
