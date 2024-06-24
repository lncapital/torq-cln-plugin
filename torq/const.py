# version of the plugin
VERSION = "1.0"

# plugin options
OPT_GRPC_PORT = "torq-grpc-port"
OPT_CHANNEL_OPEN_DEFAULT_ACTION = "torq-channel-open-default-action"

# defaults
DEFAULT_GRPC_PORT = "50053"

# timeout in seconds
CHANNEL_OPEN_TIMEOUT = 15

# state keys

# is there an active grpc subscription to the channel interceptor, only 1 can exist at a time
CHANNEL_OPEN_INTERCEPTOR_SUB_EXISTS = "ChannelOpenInterceptorSubExists"
