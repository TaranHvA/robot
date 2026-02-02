# main.py
import threading
import logging
import time
from queue import PriorityQueue

from robot_client import RobotClient
from state import SystemState
from control import control_loop
from sensor import sensor_loop
from command import command_loop
from rx import rx_loop
from protocol import HANDSHAKE
from gui import RobotlabApp

logging.basicConfig(level=logging.INFO)
ROBOT_NAMES = list(RobotClient.ROBOT_IPS.keys())


def connect_and_handshake(client):
    """Connect to the robot and perform the handshake."""
    while True:
        robot = input(
            f"Robot name [{', '.join(ROBOT_NAMES)}] or [Local]: "
        ) or "Local"
        port = input("Port custom or [5000]: ") or "5000"

        ok, msg = client.connect(robot, int(port))
        print(msg)

        if not ok:
            continue

        # Send handshake message
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

    # --- Sensor loop thread ---
    # Continuously updates sensor values in the shared state
    threading.Thread(
        target=sensor_loop,
        args=(state, stop_event),
        daemon=True
    ).start()

    # --- Control loop thread ---
    # Executes commands from the command loop or bypasses it for instant replies
    threading.Thread(
        target=control_loop,
        args=(control_q, state, client, stop_event),
        daemon=True
    ).start()

    # --- CLI command loop ---
    # Allows the terminal user to send commands and orchestrate the system
    threading.Thread(
        target=command_loop,
        args=(control_q, state, stop_event),
        daemon=True
    ).start()

    # --- RX loop thread ---
    # Listens for incoming Rapid messages and forwards instant requests
    threading.Thread(
        target=rx_loop,
        args=(client, control_q, stop_event),
        daemon=True
    ).start()

    # --- GUI ---
    app = RobotlabApp(state, stop_event)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

    # --- Shutdown ---
    stop_event.set()
    logging.info("Application stopped")


if __name__ == "__main__":
    main()
