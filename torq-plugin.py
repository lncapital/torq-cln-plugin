#!/usr/bin/env python3
"""
A plugin to add functionality to CLN needed by Torq.
"""

from const import *
from pyln.client import Plugin
from threading import Thread
import time
import os

plugin = Plugin()
plugin.dynamic = True

plugin.add_option(
    OPT_GRPC_PORT,
    DEFAULT_GRPC_PORT,
    "Port for the gRPC server.",
    "int",
)

plugin.add_option(
    OPT_CHANNEL_OPEN_DEFAULT_ACTION,
    "true",
    "Default action of the channel open interceptor in case there is no connection to Torq: 0=reject, 1=allow.",
    "bool",
)

try:
    import uuid
    import grpc
    from concurrent import futures
    from queue import Empty as QueueEmptyError, Queue

    from plugin_grpc_server import ThreadCommunicator, serve_grpc

except ImportError as e:
    # handle import error and exit the plugin gracefully
    @plugin.init()
    def init(options: dict, configuration: dict, plugin: Plugin):
        plugin.log(f"Error importing dependencies of plugin: {e}", "error")

        dir_path = os.path.dirname(os.path.realpath(__file__))

        plugin_name = os.path.join(dir_path, "torq-plugin.py")
        requirements_path = os.path.join(dir_path, "requirements.txt")

        if plugin.rpc is not None:
            plugin.log(f"Stopping plugin due to import error.", "error")

            plugin.log(
                f"Install the missing dependencies with: \npip install -r {requirements_path}\n Then restart the plugin with: \nlightning-cli plugin start {plugin_name}"
            )
            # stop self
            plugin.rpc.plugin_stop(plugin_name)

    plugin.run()
    exit(0)


# no import error, continue with the plugin


def reset_plugin_state(plugin_state: dict):
    plugin_state[CHANNEL_OPEN_INTERCEPTOR_SUB_EXISTS] = False

    return plugin_state


# the dynamic state of the plugin
plugin_state = reset_plugin_state({})

grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
tc = ThreadCommunicator(grpc_server)

grpc_server_thread = Thread(
    target=serve_grpc,
    args=(grpc_server, tc, plugin, plugin_state),
)


@plugin.method("torq_getstatus")
def torq_get_status(plugin: Plugin):
    """Get the current status of the plugin."""

    opts = {}

    for key, val in plugin.options.items():
        opts[key] = val["value"]

    status = {
        "state": plugin_state,
        "options": opts,
        "version": VERSION,
    }

    return status


def on_openchannel_internal(openchannel: dict, plugin: Plugin, version: int):

    if not plugin_state[CHANNEL_OPEN_INTERCEPTOR_SUB_EXISTS]:
        plugin.log(
            f"Channel open (v{version}) requested. The the grpc stream to Torq to handle the intercptions is not active."
        )

        if plugin.get_option(OPT_CHANNEL_OPEN_DEFAULT_ACTION):
            plugin.log(f"Default action set to allow. Allowing channel open.")
            return {"result": "continue"}

        plugin.log(f"Default action set to reject. Rejecting channel open.")
        return {
            "result": "reject",
            # Error message for the peer
            "error_message": "Internal error opening channel, please try again",
        }

    peer_pubkey = ""
    funding_amount_sat = 0
    push_amount_msat = 0
    dust_limit_msat = 0
    max_htlc_value_in_flight_msat = 0
    channel_reserve_sat = 0
    feerate_per_kw = 0
    to_self_delay = 0
    max_accepted_htlcs = 0

    try:
        peer_pubkey = str(openchannel["id"])
        if not peer_pubkey:
            raise ValueError("Peer pubkey not found in openchannel request")
        # if getting different values, handle both: openchannel and openchannel2

        if version == 1:
            funding_amount_sat = int(int(openchannel["funding_msat"]) / 1000)
            push_amount_msat = int(openchannel["push_msat"])
            channel_reserve_sat = int(int(openchannel["channel_reserve_msat"]) / 1000)
            feerate_per_kw = int(openchannel["feerate_per_kw"])
        if version == 2:
            funding_amount_sat = int(int(openchannel["their_funding_msat"]) / 1000)
            feerate_per_kw = int(openchannel["funding_feerate_per_kw"])

        dust_limit_msat = int(openchannel["dust_limit_msat"])
        max_htlc_value_in_flight_msat = int(
            openchannel["max_htlc_value_in_flight_msat"]
        )

        to_self_delay = int(openchannel["to_self_delay"])
        max_accepted_htlcs = int(openchannel["max_accepted_htlcs"])

    except:
        plugin.log(f"Error parsing openchannel {version} request")

        # the error_message is sent to the peer
        return {
            "result": "reject",
            "error_message": "Error parsing channel open request",
        }

    start_time = time.time()
    message_id = str(uuid.uuid4())

    intercepted_channel_open_msg = {
        "message_id": message_id,
        "timestamp": start_time,
        "peer_pubkey": peer_pubkey,
        "funding_amount_sat": funding_amount_sat,
        "push_amount_msat": push_amount_msat,
        "dust_limit_msat": dust_limit_msat,
        "max_htlc_value_in_flight_msat": max_htlc_value_in_flight_msat,
        "channel_reserve_sat": channel_reserve_sat,
        "feerate_per_kw": feerate_per_kw,
        "to_self_delay": to_self_delay,
        "max_accepted_htlcs": max_accepted_htlcs,
    }

    response_queue = Queue()

    # set response queue where the response will be received
    tc.intercepted_channel_open_response_queue_set(message_id, response_queue)

    # send intercepted channel open message to grpc thread
    tc.intercepted_channel_open_queue_add(intercepted_channel_open_msg)

    # block and wait for response from grpc thread, timeout to not hang indefinitely
    try:
        intercepted_channel_open_msg_resp = response_queue.get(
            timeout=CHANNEL_OPEN_TIMEOUT
        )
    except QueueEmptyError:
        # the queue clear from the response dict
        tc.intercepted_channel_open_responses_pop(message_id)

        plugin.log(
            f"Open channel received no channel open result response before timeout, rejecting."
        )

        return {
            "result": "reject",
            # Error message for the peer
            "error_message": "Internal error opening channel, please try again",
        }

    # allow
    if intercepted_channel_open_msg_resp["allow"]:
        plugin.log(f"Allowing channel open by {peer_pubkey}.")
        return {"result": "continue"}

    # reject
    err_msg = intercepted_channel_open_msg_resp["reject_reason"]
    if not err_msg:
        err_msg = "Channel open rejected"

    plugin.log(f"Rejecting channel open by {peer_pubkey}. Reason: {err_msg}")
    return {
        "result": "reject",
        "error_message": err_msg,
    }


@plugin.hook("openchannel")
def on_openchannelV1(openchannel: dict, plugin: Plugin, **kwargs):
    return on_openchannel_internal(openchannel, plugin, 1)


@plugin.hook("openchannel2")
def on_openchannelV2(openchannel2: dict, plugin: Plugin, **kwargs):
    return on_openchannel_internal(openchannel2, plugin, 2)


@plugin.subscribe("shutdown")
def on_shutdown(plugin: Plugin, **kwargs):
    plugin.log("Torq plugin shutting down")
    reset_plugin_state(plugin_state)

    tc.exit()
    if grpc_server_thread.is_alive():
        # 5 second timeout to allow for graceful shutdown
        grpc_server_thread.join(5)


@plugin.init()
def init(options: dict, configuration: dict, plugin: Plugin):
    # start grpc server thread by running serve_grpc in a separate thread

    grpc_server_thread.start()

    plugin.log("Torq plugin initialized")

    return {}


plugin.run()
