import threading, time

import requests


class AutoUpdateIPThread(threading.Thread):
    def __init__(
        self,
        minutes,
        label,
        refresh_ip_addr_checkbox,
        refresh_ip_address_command,
    ):
        super().__init__()
        self.minutes = minutes
        self._kill = threading.Event()
        self._interval = 1
        self.label = label
        self.ip_address = None
        self.refresh_ip_addr_checkbox = refresh_ip_addr_checkbox
        self.refresh_ip_address_command = refresh_ip_address_command

    def get_ip_address(self):
        ip_addr = requests.get("https://api.ipify.org").text
        if ip_addr == "":
            raise Exception("Failed to get IP address")
        self.ip_address = ip_addr

    def run(self):
        current_address = "0.0.0.0"
        while True:
            self.get_ip_address()

            if self.ip_address != current_address:
                self.refresh_ip_address_command()
            
            # If no kill signal is set, sleep for the interval,
            # If kill signal comes in while sleeping, immediately
            #  wake up and handle
            is_killed = self._kill.wait(self.minutes * 60)

            if is_killed:
                return

    def kill(self):
        self._kill.set()
