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
    __slots__ = ["message_id", "timestamp", "peer_pubkey", "funding_amount_sat", "push_amount_msat", "dust_limit_msat", "max_htlc_value_in_flight_msat", "channel_reserve_sat", "feerate_per_kw", "to_self_delay", "max_accepted_htlcs"]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PEER_PUBKEY_FIELD_NUMBER: _ClassVar[int]
    FUNDING_AMOUNT_SAT_FIELD_NUMBER: _ClassVar[int]
    PUSH_AMOUNT_MSAT_FIELD_NUMBER: _ClassVar[int]
    DUST_LIMIT_MSAT_FIELD_NUMBER: _ClassVar[int]
    MAX_HTLC_VALUE_IN_FLIGHT_MSAT_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_RESERVE_SAT_FIELD_NUMBER: _ClassVar[int]
    FEERATE_PER_KW_FIELD_NUMBER: _ClassVar[int]
    TO_SELF_DELAY_FIELD_NUMBER: _ClassVar[int]
    MAX_ACCEPTED_HTLCS_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    timestamp: float
    peer_pubkey: str
    funding_amount_sat: int
    push_amount_msat: int
    dust_limit_msat: int
    max_htlc_value_in_flight_msat: int
    channel_reserve_sat: int
    feerate_per_kw: int
    to_self_delay: int
    max_accepted_htlcs: int
    def __init__(self, message_id: _Optional[str] = ..., timestamp: _Optional[float] = ..., peer_pubkey: _Optional[str] = ..., funding_amount_sat: _Optional[int] = ..., push_amount_msat: _Optional[int] = ..., dust_limit_msat: _Optional[int] = ..., max_htlc_value_in_flight_msat: _Optional[int] = ..., channel_reserve_sat: _Optional[int] = ..., feerate_per_kw: _Optional[int] = ..., to_self_delay: _Optional[int] = ..., max_accepted_htlcs: _Optional[int] = ...) -> None: ...

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
