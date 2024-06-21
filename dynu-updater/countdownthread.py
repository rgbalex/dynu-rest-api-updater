import threading, time


class CountdownThread(threading.Thread):
    def __init__(self, seconds, label):
        super().__init__()
        self.seconds = seconds
        self._kill = threading.Event()
        self._interval = 1
        self.label = label

    def countdown(self):
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(self.seconds))
        self.label.configure(text=formatted_time)

    def run(self):
        while self.seconds > 0:
            self.countdown()

            # If no kill signal is set, sleep for the interval,
            # If kill signal comes in while sleeping, immediately
            #  wake up and handle
            self.seconds -= 1
            is_killed = self._kill.wait(self._interval)

            if is_killed:
                break

    def kill(self):
        self._kill.set()
