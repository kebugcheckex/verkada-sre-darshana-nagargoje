from enum import Enum
import random
from random import randint, randrange
import time
from threading import Event, Thread


class CameraEvents(Enum):
    motion_detected = 'motion_detected'
    user_started_viewing = 'user_started_viewing_live_video'
    brightness_adjusted = 'brightness_adjusted'


_LOG_PERIOD = 2
_EVENT_LIST = [e for e in CameraEvents]


class EventSystem:
    """
    Generates camera events and exposes them as logs.
    """
    def __init__(self):
        # Get the same data every run by using the same seed
        random.seed(1)
        self._logs = []
        self._stop = Event()
        self._generate_logs_thread = None

        self._generate_logs_thread = Thread(target=self._generate_logs)
        self._generate_logs_thread.start()

    def __del__(self):
        # Clean up the log generation thread.
        # First tell it to stop.
        self._stop.set()
        # Then wait for the thread to complete.
        if self._generate_logs_thread:
            self._generate_logs_thread.join()

    def _generate_log(self):
        """
        Randomly generates one log entry, which includes UTC timestamp
        and event (string).
        """
        log = {"timestamp": time.time()}
        event = _EVENT_LIST[randrange(len(CameraEvents))]
        log["event"] = event.value
        if event == CameraEvents.motion_detected:
            log["intensity"] = randint(1, 10)
        if event == CameraEvents.brightness_adjusted:
            log["adjustment"] = randrange(-10, 11)
        return log

    def _generate_logs(self, iterations=None):
        """
        Generates a new log entry every _LOG_PERIOD until the EventSystem object is
        destroyed (iterations is for testing).
        """
        i = 0
        while (not self._stop.is_set()
               and (iterations is None or i < iterations)):
            log = self._generate_log()
            log["idx"] = i
            self._logs.append(log)
            i += 1
            time.sleep(_LOG_PERIOD)

    def get_logs(self):
        """
        Returns a copy of the list of logs
        """
        return self._logs[:]
