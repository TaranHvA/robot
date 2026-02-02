# rx.py (of gewoon in main.py als je wilt)
import logging
from protocol import RAPID_GET_HEAT_SENSOR, SENSOR


def rx_loop(client, control_q, stop_event):
    """
    Continuously reads RX messages from the robot and forwards
    Rapid requests directly to the control loop for instant replies.
    """
    while not stop_event.is_set():
        rx = client.get_rx(timeout=0.1)
        if not rx:
            continue

        try:
            target, msg_type, value, seq = rx.split(",")
            target = int(target)
            msg_type = int(msg_type)
        except ValueError:
            logging.warning(f"Malformed RX message: {rx}")
            continue

        if target == SENSOR:
            # Rapid requests sensor value
            if msg_type == RAPID_GET_HEAT_SENSOR:
                # Forward directly to control loop
                control_q.put((
                    0,                     # highest priority
                    "RAPID_REQUEST",
                    "GET_SENSOR"
                ))
