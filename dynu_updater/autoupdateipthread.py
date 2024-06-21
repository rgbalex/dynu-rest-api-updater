import threading, requests


class AutoUpdateIPThread(threading.Thread):
    def __init__(
        self,
        print,
        seconds,
        refresh_ip_addr_checkbox,
        refresh_ip_address_command,
        request_ip_update_button,
        request_ip_update_command,
        update_interval_entry,
    ):
        super().__init__()
        self.print = print
        self.seconds = None
        try:
            self.seconds = int(seconds)
            if self.seconds < 1:
                raise ValueError
            if self.seconds > 9999:
                raise ValueError
            self.print(f"Updating every {self.seconds} seconds. \n")
        except ValueError:
            self.print("Invalid input for update frequency.\n", "WARN")
            return

        self.ip_address = None
        self._kill = threading.Event()
        self.update_interval_entry = update_interval_entry
        self.refresh_ip_addr_checkbox = refresh_ip_addr_checkbox
        self.request_ip_update_button = request_ip_update_button
        self.request_ip_update_command = request_ip_update_command
        self.refresh_ip_address_command = refresh_ip_address_command
        self.old_button_color = request_ip_update_button.cget("fg_color")
        self.old_button_hover_color = request_ip_update_button.cget("hover_color")

    def get_ip_address(self):
        try:
            return requests.get("https://api.ipify.org").text
        except requests.RequestException:
            self.print("Failed to get IP Address.\n", "CRIT")
            return "0.0.0.0"

    def run(self):
        current_ip_address = "0.0.0.0"
        self.request_ip_update_button.configure(
            text="Stop Auto Update",
            fg_color=("#6f0000"),
            hover_color=("#530000"),
            command=self.kill,
        )
        self.update_interval_entry.configure(state="disabled")
        while True:
            new_ip_address = self.get_ip_address()
            if new_ip_address != current_ip_address:
                current_ip_address = new_ip_address
                self.print(f"IP Address updated to {current_ip_address}\n")
                try:
                    self.refresh_ip_address_command(current_ip_address)
                except requests.RequestException as e:
                    self.print(f"Failed to update IP Address. {e}\n", "CRIT")
                    self.kill()
            else:
                self.print("IP Address is up to date.\n")

            if self.refresh_ip_addr_checkbox.get() == 0:
                self.print("Auto IP Update Stopped.\n")
                self.request_ip_update_button.configure(
                    text="Request IP Update",
                    fg_color=self.old_button_color,
                    hover_color=self.old_button_hover_color,
                    command=self.request_ip_update_command,
                )
                self.update_interval_entry.configure(state="normal")
                return

            is_killed = self._kill.wait(self.seconds)

            if is_killed:
                return

    def kill(self):
        self.print("Auto IP Update Stopped.\n")
        self.request_ip_update_button.configure(
            text="Request IP Update",
            fg_color=self.old_button_color,
            hover_color=self.old_button_hover_color,
            command=self.request_ip_update_command,
        )
        self.update_interval_entry.configure(state="normal")
        self._kill.set()
