# sensor.py
import time
import serial
import logging
import re

PORT = "COM4"
BAUD = 9600

TEMP_REGEX = re.compile(r"([-+]?\d*\.?\d+)")

def sensor_loop(system_state, stop_event):
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)
        logging.info(f"Sensor verbonden op {PORT}")

        while not stop_event.is_set():
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").strip()

                match = TEMP_REGEX.search(line)
                if match:
                    value = float(match.group(1))
                    system_state.set_sensor_value(value)
                else:
                    logging.warning(f"Ongeldige sensorwaarde: {line}")

            time.sleep(0.01)

    except Exception as e:
        logging.error(f"Sensor fout: {e}")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
