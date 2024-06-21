import threading, requests


class AutoUpdateIPThread(threading.Thread):
    def __init__(
        self,
        print,
        minutes,
        refresh_ip_addr_checkbox,
        refresh_ip_address_command,
    ):
        super().__init__()
        self.print = print
        self.minutes = None
        if (minutes is None) | (minutes == ""):
            minutes = 1
        try:
            minutes = int(minutes)
            self.minutes = minutes
            self.print(f"Updating every {self.minutes}minutes. \n")
        except ValueError:
            self.print("Invalid input for update frequency. Defaulting to 1 minute.")
            minutes = 1

        self.minutes = minutes
        self.ip_address = None
        self._kill = threading.Event()
        self.refresh_ip_addr_checkbox = refresh_ip_addr_checkbox
        self.refresh_ip_address_command = refresh_ip_address_command

    def get_ip_address(self):
        try:
            return requests.get("https://api.ipify.org").text
        except requests.RequestException:
            self.print("Failed to get IP Address. \n")
            return "0.0.0.0"

    def run(self):
        current_ip_address = "0.0.0.0"
        while True:
            new_ip_address = self.get_ip_address()
            if new_ip_address != current_ip_address:
                current_ip_address = new_ip_address
                self.print(f"IP Address updated to {current_ip_address} \n")
                self.refresh_ip_address_command(current_ip_address)
            else:
                self.print("IP Address is up to date. \n")

            if self.refresh_ip_addr_checkbox.get() == 0:
                self.print("Auto IP Update Stopped. \n")
                return

            is_killed = self._kill.wait(self.minutes)

            if is_killed:
                return

    def kill(self):
        self._kill.set()
