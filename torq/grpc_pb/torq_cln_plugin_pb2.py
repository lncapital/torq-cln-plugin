# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: torq_cln_plugin.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15torq_cln_plugin.proto\"\x0e\n\x0c\x45mptyMessage\"9\n\x16TestConnectionResponse\x12\x0e\n\x06pubkey\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\"\xb7\x02\n\x1bInterceptChannelOpenRequest\x12\x12\n\nmessage_id\x18\x01 \x01(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\x01\x12\x13\n\x0bpeer_pubkey\x18\x03 \x01(\t\x12\x1a\n\x12\x66unding_amount_sat\x18\x04 \x01(\x04\x12\x18\n\x10push_amount_msat\x18\x05 \x01(\x04\x12\x17\n\x0f\x64ust_limit_msat\x18\x06 \x01(\x04\x12%\n\x1dmax_htlc_value_in_flight_msat\x18\x07 \x01(\x04\x12\x1b\n\x13\x63hannel_reserve_sat\x18\x08 \x01(\x04\x12\x16\n\x0e\x66\x65\x65rate_per_kw\x18\t \x01(\x04\x12\x15\n\rto_self_delay\x18\n \x01(\r\x12\x1a\n\x12max_accepted_htlcs\x18\x0b \x01(\r\"\x87\x01\n\x1cInterceptChannelOpenResponse\x12\x12\n\nmessage_id\x18\x01 \x01(\t\x12\x16\n\x0eorig_timestamp\x18\x02 \x01(\x01\x12\r\n\x05\x61llow\x18\x03 \x01(\x08\x12\x1a\n\rreject_reason\x18\x04 \x01(\tH\x00\x88\x01\x01\x42\x10\n\x0e_reject_reason2\xda\x01\n\rTorqCLNPlugin\x12:\n\x0eTestConnection\x12\r.EmptyMessage\x1a\x17.TestConnectionResponse\"\x00\x12G\n\x14InterceptChannelOpen\x12\r.EmptyMessage\x1a\x1c.InterceptChannelOpenRequest\"\x00\x30\x01\x12\x44\n\x12RespondChannelOpen\x12\x1d.InterceptChannelOpenResponse\x1a\r.EmptyMessage\"\x00\x42\x30Z.github.com/lncapital/torq-core/torq_cln_pluginb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'torq_cln_plugin_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z.github.com/lncapital/torq-core/torq_cln_plugin'
  _globals['_EMPTYMESSAGE']._serialized_start=25
  _globals['_EMPTYMESSAGE']._serialized_end=39
  _globals['_TESTCONNECTIONRESPONSE']._serialized_start=41
  _globals['_TESTCONNECTIONRESPONSE']._serialized_end=98
  _globals['_INTERCEPTCHANNELOPENREQUEST']._serialized_start=101
  _globals['_INTERCEPTCHANNELOPENREQUEST']._serialized_end=412
  _globals['_INTERCEPTCHANNELOPENRESPONSE']._serialized_start=415
  _globals['_INTERCEPTCHANNELOPENRESPONSE']._serialized_end=550
  _globals['_TORQCLNPLUGIN']._serialized_start=553
  _globals['_TORQCLNPLUGIN']._serialized_end=771
# @@protoc_insertion_point(module_scope)
