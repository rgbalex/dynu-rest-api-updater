import threading, time


class CountdownThread(threading.Thread):
    def __init__(
        self,
        print,
        seconds,
        label,
        refresh_oauth_session_checkbox,
        refresh_oauth_session_command,
        logon_oauth_button,
        reset_oauth_session_command,
    ):
        super().__init__()
        self._interval = 1
        self.label = label
        self.print = print
        self.seconds = seconds
        self._kill = threading.Event()
        self.logon_oauth_button = logon_oauth_button
        self.reset_oauth_session_command = reset_oauth_session_command
        self.refresh_oauth_session_command = refresh_oauth_session_command
        self.refresh_oauth_session_checkbox = refresh_oauth_session_checkbox
        self.old_button_color = logon_oauth_button.cget("fg_color")
        self.old_button_hover_color = logon_oauth_button.cget("hover_color")

    def countdown(self, seconds):
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(seconds))
        self.label.configure(text=formatted_time)

    def refresh_oauth_session(self):
        self.logon_oauth_button.configure(
            text="Refresh OAuth Token",
            fg_color=("#530000"),
            hover_color=("#005000"),
            command=self.refresh_oauth_session,
        )
        self.refresh_oauth_session_command()
        self._kill.set()

    def run(self):
        self.logon_oauth_button.configure(
            text="Refresh OAuth Token",
            fg_color=("#005000"),
            hover_color=("#530000"),
            command=self.refresh_oauth_session,
        )
        refresh_state = self.refresh_oauth_session_checkbox.get()
        while self.seconds > 60:
            self.countdown(self.seconds)

            if refresh_state != self.refresh_oauth_session_checkbox.get():
                refresh_state = self.refresh_oauth_session_checkbox.get()
                on_off = "Enabling" if refresh_state else "Disabling"
                self.print(f"{on_off} auto refresh of OAuth session.\n")

            self.seconds -= 1
            is_killed = self._kill.wait(self._interval)
            if is_killed:
                return

        self.print("Your session will expire in 60 seconds.\n")

        while self.seconds > 10:
            self.countdown(self.seconds)

            self.seconds -= 1
            is_killed = self._kill.wait(self._interval)
            if is_killed:
                return

        if self.refresh_oauth_session_checkbox.get() == 1:
            self.print("Refreshing OAuth Session...")
            self.countdown(0)
            self.refresh_oauth_session_command()
            return
        else:
            self.print("Your session has expired. Please refresh your OAuth session.\n")
            self.logon_oauth_button.configure(
                text="Logon to Dynu API",
                fg_color=self.old_button_color,
                hover_color=self.old_button_hover_color,
                command=self.refresh_oauth_session_command,
            )
            self.reset_oauth_session_command()
            self.countdown(0)
            return

    def kill(self):
        self.logon_oauth_button.configure(
            text="Logon to Dynu API",
            fg_color=self.old_button_color,
            hover_color=self.old_button_hover_color,
            command=self.refresh_oauth_session_command,
        )
        self._kill.set()
