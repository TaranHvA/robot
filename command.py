# command.py
import time

def command_loop(control_q, state, stop_event):
    time.sleep(3)

    while not stop_event.is_set():
        try:
            print("Type: run <id>, stop, status, exit(to exit the program)")
            cmd = input("> ")
        except EOFError:
            break

        if cmd == "exit":
            stop_event.set()
            break

        elif cmd == "stop":
            control_q.put((0, "STOP", None))

        elif cmd.startswith("run"):
            try:
                _, pid = cmd.split()
                control_q.put((5, "RUN_PATH", int(pid)))
            except ValueError:
                print("Usage: run <id>")

        elif cmd == "status":
            print("Sensor:", state.get_sensor_value())
