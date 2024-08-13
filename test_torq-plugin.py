import os
import grpc
import threading

from pyln.testing.fixtures import *  # type: ignore

from const import *

sys.path.append(os.path.join(os.path.dirname(__file__), "grpc_pb"))

from grpc_pb import torq_cln_plugin_pb2, torq_cln_plugin_pb2_grpc

plugin_path = os.path.join(os.path.dirname(__file__), "torq-plugin.py")
pluginopt = {"plugin": plugin_path}


def get_grpc_client():
    channel = grpc.insecure_channel("localhost:" + DEFAULT_GRPC_PORT)
    stub = torq_cln_plugin_pb2_grpc.TorqCLNPluginStub(channel)
    return stub


def join_nodes_ignore_exception(node_factory, node1, node2):
    try:
        node_factory.join_nodes([node1, node2], wait_for_announce=True)
    except Exception as e:
        print(f"Join_nodes exception ignored: {e}")


def join_nodes_for_version_23(node_factory, node1, node2):
    initial_channel_amount = len(
        node2.rpc.listchannels(source=node1.info["id"])["channels"]
    )

    open_channel_thread = threading.Thread(
        join_nodes_ignore_exception(node_factory, node1, node2)
    )
    open_channel_thread.start()

    # 10 seconds timeout to wait for channel open
    for _ in range(10):
        if (
            len(node2.rpc.listchannels(source=node1.info["id"])["channels"])
            == initial_channel_amount + 1
        ):
            break
        time.sleep(1)

    # force the thread to stop since the join_nodes hangs for version 23
    open_channel_thread.join(1)


def test_start_stop_plugin(node_factory):
    node = node_factory.get_node(options=pluginopt)

    node.rpc.plugin_stop(plugin_path)
    node.daemon.wait_for_log("Torq plugin shutting down")
    node.rpc.plugin_start(plugin_path)
    node.daemon.wait_for_log("Torq plugin initialized")
    node.stop()


def test_TestConnection(node_factory):
    node = node_factory.get_node(options=pluginopt)

    resp = get_grpc_client().TestConnection(torq_cln_plugin_pb2.EmptyMessage())

    assert resp == torq_cln_plugin_pb2.TestConnectionResponse(
        pubkey=node.info["id"], version=VERSION
    )


def test_InterceptChannelOpen(node_factory):
    node = node_factory.get_node(options=pluginopt)
    ext_node = node_factory.get_node()

    node_version = node.rpc.getinfo()["version"]

    # for version 23, must do tricks because node_factory.join_nodes doesn't work for that version
    node_v_23 = "v23" in node_version

    # By default allow channel open because by default torq-channel-open-default-action is true
    if node_v_23:
        join_nodes_for_version_23(node_factory, ext_node, node)
    else:
        node_factory.join_nodes([ext_node, node], wait_for_announce=True)

    # channel opened
    assert len(node.rpc.listchannels(source=ext_node.info["id"])["channels"]) == 1

    interception_data = {}

    def listen_to_channel_open(should_fail_on_exhausted=False):
        responses = get_grpc_client().InterceptChannelOpen(
            torq_cln_plugin_pb2.EmptyMessage()
        )

        rpc_error = ""

        try:
            for response in responses:
                print(f"\nReceived channel open interception: {response}\n")

                get_grpc_client().RespondChannelOpen(
                    torq_cln_plugin_pb2.InterceptChannelOpenResponse(
                        message_id=response.message_id,
                        allow=interception_data["allow"]
                        == True,  # allow depending on the test
                        orig_timestamp=response.timestamp,
                    )
                )
        except grpc.RpcError as e:
            rpc_error = str(e)
            print(f"InterceptChannelOpen streaming error: {e}")

        if should_fail_on_exhausted:
            assert "StatusCode.RESOURCE_EXHAUSTED" in rpc_error

    stream_thread = threading.Thread(target=listen_to_channel_open)
    stream_thread.start()

    time.sleep(1)

    # One stream already active, can't open a new one
    listen_to_channel_open(should_fail_on_exhausted=True)

    # Try to open a new channel, should reject
    interception_data["allow"] = False
    ext_node2 = node_factory.get_node()
    exception_on_channel_open = ""
    try:
        node_factory.join_nodes([ext_node2, node], wait_for_announce=True)
    except Exception as e:
        exception_on_channel_open = str(e)

    # channel not opened
    assert "They sent ERROR" in exception_on_channel_open
    assert len(node.rpc.listchannels(source=ext_node2.info["id"])["channels"]) == 0

    # Try to open a new channel, should allow
    interception_data["allow"] = True

    if node_v_23:
        join_nodes_for_version_23(node_factory, ext_node2, node)
    else:
        node_factory.join_nodes([ext_node2, node], wait_for_announce=True)

    # channel opened
    assert len(node.rpc.listchannels(source=ext_node2.info["id"])["channels"]) == 1

    # Close the stream
    stream_thread.join(1)


def test_block_channel_open_by_default(node_factory):
    pluginopt_mod = pluginopt.copy()
    pluginopt_mod["torq-channel-open-default-action"] = "false"
    node = node_factory.get_node(options=pluginopt_mod)
    ext_node = node_factory.get_node()

    channel_open_failed = False

    try:
        # Block channel open because torq-channel-open-default-action is set to false
        node_factory.join_nodes([ext_node, node], wait_for_announce=True)
    except Exception as e:
        assert "They sent ERROR" in repr(e)
        channel_open_failed = True

    assert channel_open_failed
    assert len(node.rpc.listchannels()["channels"]) == 0
