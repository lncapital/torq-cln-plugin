## Torq CLN plugin

A plugin for CLN to add some features to Torq with CLN nodes. Only use with Torq!

Supported Torq version: x.x.x (TODO add version)

The plugin uses it's own separate gRPC server to communicate with Torq. Note: The separate gRPC is currently unauthenticated and unencrypted(!), so if Torq is communicating to CLN over the internet, using this plugin is highly discouraged! Use on local networks only. Also be sure that the port of the plugin's gRPC server is not open to the internet.

#### Installation

Once the plugin is added to the CLN plugins repository, it can be installed with:

    reckless install torq

#### CLN configuration options added by the plugin

- `torq-grpc-port`: the port that the plugin's own gRPC server will listen on. Default: 50053
- `torq-channel-open-default-action`: the default action to take (if there is no connection to Torq) when a channel open is requested. boolean. true = allow, false = reject. Default: allow

#### Features enabled by the plugin

- Intercept channel opens: Torq can dynamically filter on which channels are allowed to open to the node.

#### Development

To run in development mode, install the depenedencies with (change path if necessary):

```
pip install -r /usr/local/libexec/c-lightning/plugins/torq/requirements.txt
```

Then run the plugin with (change path if necessary):

```
lightning-cli --regtest plugin start /usr/local/libexec/c-lightning/plugins/torq/torq.py
```

To update the protoc definintions to correspond the protofile, run:

```
python -m grpc_tools.protoc -I. --python_out=./grpc_pb --pyi_out=./grpc_pb --grpc_python_out=./grpc_pb ./torq_cln_plugin.proto
```
