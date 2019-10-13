"""
Simplistic Python Project to Provide a Web GUI Controlled Timer for a Pi Zero with a Rely HAT

"""

# import for annotation support
import json
import threading
import time
from threading import Lock
from typing import Union

# noinspection PyPackageRequirements
from werkzeug.datastructures import ImmutableMultiDict

from timer_project import EasyFlask, json_ok, json_error, FeedbackTimer, POST

# RPi.GPIO is not supported on windows dev, so for windows use a overload class to emulate
try:
    import RPi.GPIO as GPIO
except ImportError:
    from timer_project import DummyGPIO as GPIO

# define the GPIO CLOCK_PULSE
CLOCK_PULSE = 12


def square_wave_generator():
    """ function to generate a square wave

    :return:
    """
    t = threading.currentThread()
    while getattr(t, "generator_running", True):
        # toggle high
        GPIO.output(CLOCK_PULSE, GPIO.HIGH)
        time.sleep(1)
        # check for abort mid cycle
        if not getattr(t, "generator_running", True):
            break
        # toggle low
        GPIO.output(CLOCK_PULSE, GPIO.LOW)
        time.sleep(1)

    # on shutdown force port to low
    GPIO.output(CLOCK_PULSE, GPIO.LOW)


class WebControlledTimer(EasyFlask):
    """
    Create a web controlled timer
    """

    def __init__(self):
        """
        Create a web controlled timer
        """
        super().__init__("Simplistic Web Timer")
        self.app_lock = Lock()
        self.app_time = None
        self.generator_lock = Lock()
        self.generator = None

        # setup the GPIO Here
        GPIO.setmode(GPIO.BOARD)

        # GPIO pins for the Zero are:
        #
        # {GPIO # | Pin #}
        #
        # { 0 |   } { 1 |   } { 2 |  3} { 3 |  5} { 4 |  7}
        # { 5 | 29} { 6 | 31} { 7 | 26} { 8 | 24} { 9 | 21}
        # {10 | 19} {11 | 23} {12 | 32} {13 | 33} {14 |  8}
        # {15 | 10} {16 | 36} {17 | 11} {18 | 12} {19 | 35}
        # {20 | 38} {21 | 40} {22 | 15} {23 | 16} {24 | 18}
        # {25 | 22} {26 | 37} {27 |   } {28 |   } {29 |   }
        #
        # ID_SD | ID_SC
        # {27   |   28}
        #
        # Ground
        # {6, 9, 14, 20, 25, 30, 34, 39}
        #
        # 3.3 V
        # {1, 17}
        #
        # 5.0 V
        # {2, 4, 14, 20 ,30 ,34}
        #

        # Sensor Input Definition
        clock_pulse = 12

        # Configuring GPIO for sensor inputs
        GPIO.setup(clock_pulse, GPIO.OUT)

    @POST
    def ajax_get_status(
            self,
            posted_data: Union[ImmutableMultiDict, None],
            user_request: Union[str, None],
            value: Union[str, None]) -> str:
        """ get the time status

        :param posted_data: data sent via html post
        :param user_request: the url of the request if get
        :param value: the value of the request if get
        :return: JSON string
        """
        time_state = False
        time_left = 0
        with self.app_lock:
            if self.app_time is not None:
                if self.app_time.is_alive():
                    time_state = True
                    time_left = self.app_time.remaining()
                else:
                    self.app_time = None

        return json.dumps(
            {
                "Error": False,
                "Message": "",
                "Status": time_state,
                "Left": time_left
            }
        )

    @POST
    def ajax_stop_event(
            self,
            posted_data: Union[ImmutableMultiDict, None],
            user_request: Union[str, None],
            value: Union[str, None]) -> str:
        """ stop the time event

        :param posted_data: data sent via html post
        :param user_request: the url of the request if get
        :param value: the value of the request if get
        :return: JSON string
        """
        with self.app_lock:
            if self.app_time is not None:
                if self.app_time.is_alive():
                    self.app_time.cancel()
                    self.app_time = None
                    # timer abort action here
                else:
                    self.app_time = None

        with self.generator_lock:
            if self.generator is not None:
                self.generator.generator_running = False
                self.generator.join()
                self.generator = None

        return json_ok("Ok")

    @POST
    def ajax_start_event(
            self,
            posted_data: Union[ImmutableMultiDict, None],
            user_request: Union[str, None],
            value: Union[str, None]) -> str:
        """ start the time event

        :param posted_data: data sent via html post
        :param user_request: the url of the request if get
        :param value: the value of the request if get
        :return: JSON string
        """

        hours = posted_data.get("hours", 0)
        minutes = posted_data.get("minutes", 0)
        seconds = posted_data.get("seconds", 0)

        if hours == "":
            hours = 0

        if minutes == "":
            minutes = 0

        if seconds == "":
            seconds = 0

        try:
            hours = float(hours)
            minutes = float(minutes)
            seconds = float(seconds)
        except ValueError:
            return json_error("Non numeric value of time provided...")

        run_time = 0
        run_time += hours * 60.0 * 60.0
        run_time += minutes * 60.0
        run_time += seconds

        if run_time <= 0:
            return json_error("Time provided below threshold...")

        with self.app_lock:
            if self.app_time is not None:
                if self.app_time.is_alive():
                    return json_error("Timer Already Running...")
                else:
                    self.app_time = None

            self.app_time = FeedbackTimer(interval=run_time, function=self.event_after_timer_done)
            with self.generator_lock:
                if self.generator is not None:
                    self.generator.generator_running = False
                    self.generator.join()
                    self.generator = None
                self.generator = threading.Thread(target=square_wave_generator)
                self.generator.start()
            self.app_time.start()

        return json_ok("Ok")

    def event_after_timer_done(self):
        """

        :return:
        """
        with self.generator_lock:
            if self.generator is not None:
                self.generator.generator_running = False
                self.generator.join()
                self.generator = None
        print("Done")


if __name__ == '__main__':
    app = WebControlledTimer()
    app.app.run(host="0.0.0.0", debug=False, port=5000)  # run app in debug mode on port 5000
