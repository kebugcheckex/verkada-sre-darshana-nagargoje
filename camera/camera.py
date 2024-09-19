import os

import requests

from common.utils.logging_utils import logger
import events


_API_BASE_URL = os.environ['API_BASE_URL']


class Camera:
    """
    Implements a video camera that can be asked to send logs to a client
    on demand without opening any ports, via HTTP long-polling.
    """
    def __init__(self):
        self._events = events.EventSystem()

    def _poll_for_command(self):
        """
        Makes the poll_for_command request to the API via HTTP long
        polling.  

        Returns the command returned by the API, if any.
        """
        logger.debug("Polling for command...")
        # Request the command from the server (long-poll)
        resp = requests.get(f"{_API_BASE_URL}/poll_for_command", timeout=60)
        resp.raise_for_status()
        return resp.json()

    def _respond_to_command(self, command):
        """
        Responds to the API's command to send logs.
        """
        logger.warning(f"got command {command}")
        if command.get("action") != "send_logs":
            # ONly support send_logs at this time
            return

        logs = self._events.get_logs()

        resp = requests.post(
            f"{_API_BASE_URL}/send_logs",
            json={
                "rid": command["rid"],
                "logs": logs
            }
        )
        resp.raise_for_status()
    
    def run(self):
        """
        Runs camera in an infinite loop, generating logs and waiting for
        commands from the API.
        """
        while True:
            try:
                command = self._poll_for_command()
            except Exception as e:
                logger.error(
                    "Camera error on wait for command request attempt: %s",
                    str(e)
                )
                continue
            try:
                self._respond_to_command(command)
            except Exception as e:
                logger.error(
                    "Camera error on command response: %s",
                    str(e)
                )


def main():
    camera = Camera()
    camera.run()


if __name__ == "__main__":
    main()
