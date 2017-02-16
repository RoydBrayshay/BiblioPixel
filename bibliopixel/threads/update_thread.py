import threading, time
from .. import log
from . import compose_events, threads


class UpdateDriverThread(threads.Loop):

    def __init__(self, driver):
        super().__init__()
        self.setDaemon(True)
        self._wait = threading.Event()
        self._reading = threading.Event()
        self._reading.set()
        self._updating = threading.Event()
        self._driver = driver

    def update_colors(self):
        self._reading.wait()
        self._reading.clear()
        self._wait.set()

    def sync(self):
        self._updating.wait()
        self._driver.sync()

    def sending(self):
        return self._wait.isSet()

    def loop(self):
        self._wait.wait()
        self._updating.clear()
        self._driver.update_colors()
        self._wait.clear()
        self._reading.set()
        self._updating.set()


class UpdateThread(threads.Loop):

    def __init__(self, drivers):
        super().__init__()
        self.setDaemon(True)
        self._wait = threading.Event()
        self._reading = threading.Event()
        self._reading.set()
        self._drivers = drivers
        for d in self._drivers:
            t = UpdateDriverThread(d)
            t.start()
            d._thread = t

        events = (d._thread._updating for d in self._drivers)
        self._updated = compose_events.compose_events(events)

    def update_colors(self):
        self._reading.wait()
        for d in self._drivers:
            d._thread.update_colors()
        self._reading.clear()
        self._wait.set()

    def loop(self):
        self._wait.wait()
        self._updated.wait()

        for d in self._drivers:
            d._thread.sync()

        self._updated.clear()
        self._wait.clear()
        self._reading.set()


class UpdateThreading(object):
    """
    UpdateThreading handles threading - and eventually multiprocessing - for
    LEDBase.
    """

    def __init__(self, use_update_thread, led):
        self.use_update_thread = use_update_thread
        self.led = led

        if use_update_thread:
            self.update_thread = UpdateThread(led.drivers)
            self.update_thread.start()

    def update_colors(self):
        if self.use_update_thread:
            self.update_thread.update_colors()
        else:
            for d in self.led.drivers:
                d.update_colors()
            for d in self.led.drivers:
                d.sync()

    def wait_for_update(self):
        if self.use_update_thread:
            while all([d._thread.sending() for d in self.led.drivers]):
                time.sleep(0.000001)

    def push_to_driver(self):
        """Push the current pixel state to the driver"""
        self.wait_for_update()
        self.update_colors()
