import threading, time


class CountdownThread(threading.Thread):
    def __init__(
        self,
        seconds,
        label,
        refresh_oauth_session_checkbox,
        refresh_oauth_session_command,
    ):
        super().__init__()
        self.seconds = seconds
        self._kill = threading.Event()
        self._interval = 1
        self.label = label
        self.refresh_oauth_session_checkbox = refresh_oauth_session_checkbox
        self.refresh_oauth_session_command = refresh_oauth_session_command

    def countdown(self, seconds):
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(seconds))
        self.label.configure(text=formatted_time)

    def run(self):
        while self.seconds > 60:
            self.countdown(self.seconds)

            # If no kill signal is set, sleep for the interval,
            # If kill signal comes in while sleeping, immediately
            #  wake up and handle
            self.seconds -= 1
            is_killed = self._kill.wait(self._interval)

            if is_killed:
                return

        print("Your session will expire in 60 seconds.")
        if self.refresh_oauth_session_checkbox.get() == 1:
            print("Refreshing OAuth Session...")
            self.countdown(0)
            self.refresh_oauth_session_command()

    def kill(self):
        self._kill.set()
