# main.py
import threading
import logging
import time
from queue import PriorityQueue

from robot_client import RobotClient
from state import SystemState
from control import control_loop
from sensor import sensor_loop
from protocol import HANDSHAKE
from gui import RobotlabApp

logging.basicConfig(level=logging.INFO)


def connect_and_handshake(client):
    while True:
        robot = input("Robot name [Local]: ") or "Local"
        port = input("Port [5000]: ") or "5000"

        ok, msg = client.connect(robot, int(port))
        print(msg)

        if not ok:
            continue

        client.send(1, HANDSHAKE, 0, prio=0)

        time.sleep(0.5)
        rx = client.get_rx(timeout=2.0)

        if rx:
            print("Handshake RX:", rx)
            return
        else:
            print("No handshake response, retrying...")


def main():
    stop_event = threading.Event()
    control_q = PriorityQueue()

    state = SystemState()
    client = RobotClient()

    # --- Connect & handshake ---
    connect_and_handshake(client)

    # --- Control loop thread ---
    threading.Thread(
        target=control_loop,
        args=(control_q, state, client, stop_event),
        daemon=True
    ).start()

    # --- Sensor loop thread ---
    threading.Thread(
        target=sensor_loop,
        args=(state, stop_event),
        daemon=True
    ).start()

    # --- GUI (MOET in main thread) ---
    app = RobotlabApp(state, stop_event)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

    # --- Shutdown ---
    stop_event.set()
    logging.info("Application stopped")


if __name__ == "__main__":
    main()
