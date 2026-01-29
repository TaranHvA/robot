# gui.py
import customtkinter as ctk

class RobotlabApp(ctk.CTk):
    def __init__(self, state, stop_event):
        super().__init__()

        self.system_state = state
        self.stop_event = stop_event

        self.title("Robotlab Data Monitor")
        self.geometry("500x400")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title_label = ctk.CTkLabel(
            self, text="Robot lab", font=("Roboto", 40, "bold")
        )
        self.title_label.pack(pady=20)

        self.data_label = ctk.CTkLabel(
            self, text="Wachten op data...", font=("Consolas", 16)
        )
        self.data_label.pack(pady=20)

        self.after(100, self.update_ui)

    def update_ui(self):
        value = self.system_state.get_sensor_value()

        if value is not None:
            self.data_label.configure(text=f"Sensor: {value}")

        if not self.stop_event.is_set():
            self.after(100, self.update_ui)

    def on_closing(self):
        self.stop_event.set()
        self.destroy()
