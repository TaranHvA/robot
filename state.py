# state.py
import threading

class SystemState:
    def __init__(self):
        self._lock = threading.Lock()
        self._stop = False
        self._sensor_value = 0

    def request_stop(self):
        with self._lock:
            self._stop = True

    def is_stopped(self):
        with self._lock:
            return self._stop

    def set_sensor_value(self, value):
        with self._lock:
            self._sensor_value = value

    def get_sensor_value(self):
        with self._lock:
            return self._sensor_value
