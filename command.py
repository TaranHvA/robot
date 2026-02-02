# command.py
import time

def command_loop(control_q, state, stop_event):
    time.sleep(3)  # Give other threads/processes time to start

    while not stop_event.is_set():
        try:
            print("Type: run <id>, start, stop, val_sensor, exit (to exit the program)")
            cmd = input("> ")
        except EOFError:
            break

        if cmd == "exit":
            # Stops the Python program
            stop_event.set()
            break

        elif cmd == "start":
            # Starts the Rapid code (not yet implemented on the Rapid side)
            control_q.put((0, "START", None))

        elif cmd == "stop":
            # Stops the Rapid code (not yet implemented on the Rapid side)
            control_q.put((0, "STOP", None))

        elif cmd.startswith("run"):
            # Run a path by ID (temporary implementation, may be reworked later)
            try:
                _, pid = cmd.split()
                control_q.put((5, "RUN_PATH", int(pid)))
            except ValueError:
                print("Usage: run <id>")

        elif cmd == "val_sensor":
            # Print sensor value to the terminal
            print("Sensor:", state.get_sensor_value())
