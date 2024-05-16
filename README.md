## Torq CLN plugin

A plugin for CLN to add some features to Torq with CLN nodes. Only use with Torq!

Supported Torq version: x.x.x (TODO add version)

The plugin uses rpc-passthrough (https://docs.corelightning.org/docs/json-rpc-passthrough) commands as well as it's own separate gRPC server to communicate with Torq. Note: The separate gRPC is currently unauthenticated and unencrypted(!), so if Torq is communicating to CLN over the internet, using this plugin is not recommended.

#### Installation

TODO

#### New CLN configuration options added by the plugin

- `torq-grpc-port`: the port that the plugin's own gRPC server will listen on. Default: 50053
- `torq-channel-open-default-action`: the default action to take (if there is no connection to Torq) when a channel open is requested. boolean. true = allow, false = reject. Default: false

#### Features enabled by the plugin

- Intercept channel opens: Torq can dynamically filter on which channels are allowed to open to the node.
