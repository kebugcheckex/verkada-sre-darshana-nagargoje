# Built-ins
import json
import queue
from threading import Event
from uuid import uuid4

# Flask imports
from flask import Flask, request
from flask.json import jsonify

from common.utils.logging_utils import logger

app = Flask(__name__)
request_queue = queue.Queue()
results = {}

command_send = False

@app.route("/logs")
def get_logs():
    """
    The user calls this endpoint to fetch logs from the camera.

    Todo: query parameters:
      - start_ts: (float) Fetch logs with timestamp >= this parameter.
      - end_ts: (float) Fetch logs with timestamp <= this parameter.

    Response (JSON):
    - logs: list of log objects, containing camera logs.
    """

    rid = str(uuid4())
    req = {
        "rid": rid,
        "action": "send_logs",
    }
    event = Event()

    results[rid] = {"event": event}

    # Queue the request. The poll_for_command handler will respond to the
    # camera with this request
    logger.debug(f"queueing {req}")
    request_queue.put(req)

    # Wait for the camera to send_logs
    event.wait()
    logger.debug(f"event fired for rid: {rid}")

    result = results.pop(rid)
    resp_payload = {"logs": result["logs"]}
    return jsonify(resp_payload)

@app.route("/send_logs", methods=["POST"])
def send_logs():
    """
    This endpoint allows the camera to send logs back to the API server.

    Request payload (JSON):
    - logs: (array of log objects) the logs being sent from the camera.
    """
    req_payload = request.get_json()
    logger.debug(f'received logs for rid: {req_payload["rid"]}')

    results[req_payload["rid"]]["logs"] = req_payload["logs"]
    results[req_payload["rid"]]["event"].set()
    return jsonify({})


@app.route("/poll_for_command")
def poll_for_command():
    """
    This is the endpoint that implements long polling.
    
    The camera calls this endpoint to be notified when the api server wants
    event logs.  (i.e., when the api server gets a /logs GET request from the user).

    Conceivably, it could be used to poll for other command besides "get logs",
    but here we will only be implementing that command.

    Feel free to structure the response payload however you see fit.
    """
    req = {"action": "noop"}
    try:
        req = request_queue.get(timeout=30)
        logger.debug(f"sending command {req}")
    except queue.Empty:
        logger.debug("poll timeout")

    return jsonify(req)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
