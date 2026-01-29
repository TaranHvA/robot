# robot_client.py
import socket
import threading
import queue
import logging

log = logging.getLogger("robot")

class RobotClient:
    ROBOT_IPS = {
        "Green": "10.0.0.10",
        "Yellow": "10.0.0.11",
        "Pink": "10.0.0.12",
        "Blue": "10.0.0.13",
        "Red": "10.0.0.14",
        "Purple": "10.0.0.15",
        "Gold": "10.0.0.16",
        "Local": "127.0.0.1"
    }

    def __init__(self):
        self.sock = None
        self.seq = 0
        self.running = False

        self.tx_q = queue.PriorityQueue()
        self.rx_q = queue.Queue()

    def connect(self, robot_name: str, port: int):
        robot = robot_name.strip().capitalize()

        if robot not in self.ROBOT_IPS:
            return False, f"Invalid robot '{robot}'. Options: {list(self.ROBOT_IPS)}"

        ip = self.ROBOT_IPS[robot]

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10.0)
            self.sock.connect((ip, port))

            self.running = True
            threading.Thread(target=self._tx_loop, daemon=True).start()
            threading.Thread(target=self._rx_loop, daemon=True).start()

            return True, f"Connected to {robot} ({ip}:{port})"

        except Exception as e:
            return False, f"Connection to {robot} failed: {e}"

    def send(self, target, msg_type, value, prio=10):
        self.seq += 1
        msg = f"{target},{msg_type},{value},{self.seq}"
        self.tx_q.put((prio, msg))
        log.info(f"TX queued → {msg}")

    def _tx_loop(self):
        while self.running:
            try:
                _, msg = self.tx_q.get(timeout=0.1)
                self.sock.sendall(msg.encode("ascii"))
            except queue.Empty:
                pass

    def _rx_loop(self):
        while self.running:
            try:
                data = self.sock.recv(1024).decode("utf-8")
                if data:
                    self.rx_q.put(data.strip())
            except socket.timeout:
                pass

    def get_rx(self, timeout=0.1):
        try:
            return self.rx_q.get(timeout=timeout)
        except queue.Empty:
            return None
