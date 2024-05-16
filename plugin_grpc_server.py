import json
import sys
import os
from queue import Queue, Empty as QueueEmptyError
import threading
import grpc
import time

from pyln.client import Plugin

from const import *

sys.path.append(os.path.join(os.path.dirname(__file__), "grpc_pb"))

from grpc_pb import torq_cln_plugin_pb2, torq_cln_plugin_pb2_grpc


class ThreadSafeDict:
    def __init__(self):
        self.dict = {}
        self.lock = threading.Lock()

    def set(self, key, value):
        with self.lock:
            self.dict[key] = value

    def get(self, key):
        with self.lock:
            return self.dict.get(key)

    def pop(self, key):
        with self.lock:
            try:
                return self.dict.pop(key)
            except KeyError:
                return None


class ThreadCommunicator:
    """Handles communication between grpc server and plugin threads."""

    def __init__(self, grpc_server: grpc.Server):
        # the grpc server, so that it can be stopped
        self.grpc_server = grpc_server

        # init by clearing
        self.clear()

    def clear(self):
        # dict to store the intercepted channel open requests
        self.intercepted_channel_open_resonses = ThreadSafeDict()

        # queue to send channel open to send channel open to grpc subscription
        self.intercepted_channel_open_queue = Queue()

    def intercepted_channel_open_response_queue_set(self, key: str, value: Queue):
        """Set the queue that waits for the allow/reject response to the channel open"""
        self.intercepted_channel_open_resonses.set(key, value)

    def intercepted_channel_open_responses_pop(self, key):
        """Get and remove the queue that waits for the allow/reject response to the channel open"""
        return self.intercepted_channel_open_resonses.pop(key)

    def intercepted_channel_open_respond(self, value):
        """Send the response to the channel open request to the channel open hook."""
        key = value["message_id"]
        queue = self.intercepted_channel_open_responses_pop(key)
        if queue != None and type(queue) == Queue:
            queue.put(value)

    def intercepted_channel_open_queue_add(self, value):
        """Send a new channel open interception to the grpc subscription."""
        self.intercepted_channel_open_queue.put(value)

    def intercepted_channel_open_queue_get_block(self, timeout=0):
        """Wait for the intercepted channel open in the grpc subscription."""
        return self.intercepted_channel_open_queue.get(timeout=timeout)

    def exit(self):
        # clean the queues
        self.clear()

        self.grpc_server.stop(3)


class TorqCLNPlugin(torq_cln_plugin_pb2_grpc.TorqCLNPluginServicer):
    """Wraps the grpc server methods."""

    def __init__(self, tc: ThreadCommunicator, plugin: Plugin, plugin_state: dict):
        self.tc = tc
        self.plugin = plugin
        self.plugin_state = plugin_state

    def TestConnection(
        self,
        request: torq_cln_plugin_pb2.EmptyMessage,
        context: grpc.ServicerContext,
    ):
        """Test connection to the plugin."""
        self.plugin.log("Plugin connection test received via gRPC.", "debug")

        pubkey = ""
        if self.plugin.rpc is not None:
            info = self.plugin.rpc.getinfo()
            # getinfo gives dict, eventough the type hint is str
            if type(info) == dict:
                pubkey = str(info["id"])
            else:
                self.plugin.log("RPC getinfo not returning dict", "debug")
        else:
            self.plugin.log("RPC not available in test connection", "debug")

        return torq_cln_plugin_pb2.TestConnectionResponse(
            pubkey=pubkey, version=VERSION
        )

    def InterceptChannelOpen(
        self,
        request: torq_cln_plugin_pb2.EmptyMessage,
        context: grpc.ServicerContext,
    ):
        """Forward intercepted channel open to Torq."""

        # only 1 interceptor can exist at a time
        if self.plugin_state[CHANNEL_OPEN_INTERCEPTOR_SUB_EXISTS]:
            self.plugin.log(
                "Tried to open channel interceptor stream, but one already exists."
            )
            context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
            context.set_details("Interceptor already exists")
            return  # Exiting the function stops the stream

        self.plugin.log("Opening channel open interceptor stream.", "debug")

        self.plugin_state[CHANNEL_OPEN_INTERCEPTOR_SUB_EXISTS] = True

        try:
            while context.is_active():
                try:
                    # wait for intercepted channel open from CLN
                    # every second check if the subscription is still active
                    channel_intercepted_msg = (
                        self.tc.intercepted_channel_open_queue_get_block(timeout=1)
                    )
                except QueueEmptyError:
                    continue

                # TODO add more data to the request
                yield torq_cln_plugin_pb2.InterceptChannelOpenRequest(
                    message_id=str(channel_intercepted_msg["message_id"]),
                    timestamp=channel_intercepted_msg["timestamp"],
                    peer_pubkey=channel_intercepted_msg["peer_pubkey"],
                )
        except Exception as e:
            self.plugin.log(f"Channel open interceptor stream error: {e}")
        finally:
            self.plugin.log("Channel open interceptor stream closed.")
            self.plugin_state[CHANNEL_OPEN_INTERCEPTOR_SUB_EXISTS] = False

    def RespondChannelOpen(
        self,
        request: torq_cln_plugin_pb2.InterceptChannelOpenResponse,
        context: grpc.ServicerContext,
    ):
        """Response to channel open requests from Torq."""

        # if timeout reached, don't respond
        if time.time() - request.orig_timestamp > CHANNEL_OPEN_TIMEOUT:
            self.plugin.log(
                "Got response to channel open request, but timeout reached. Ignoring.",
                "debug",
            )
            # clear from the dict
            self.tc.intercepted_channel_open_responses_pop(request.message_id)

            return torq_cln_plugin_pb2.EmptyMessage()

        self.plugin.log(
            "Got response to channel open request. Forwarding to the hook.", "debug"
        )

        # send the response to the channel open hook
        self.tc.intercepted_channel_open_respond(
            {
                "message_id": request.message_id,
                "timestamp": request.orig_timestamp,
                "allow": request.allow,
                "reject_reason": request.reject_reason,
            }
        )

        return torq_cln_plugin_pb2.EmptyMessage()


def serve_grpc(
    server: grpc.Server, tc: ThreadCommunicator, plugin: Plugin, plugin_state: dict
):
    port = plugin.get_option(OPT_GRPC_PORT)
    if not port:
        plugin.log(f"Invalid port {port}")
        tc.exit()
        return

    torq_cln_plugin_pb2_grpc.add_TorqCLNPluginServicer_to_server(
        TorqCLNPlugin(tc, plugin, plugin_state), server
    )

    server.add_insecure_port(f"[::]:{port}")
    server.start()
    plugin.log(f"grpc server started on port {port}")
    server.wait_for_termination()
