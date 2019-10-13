"""
    Simplistic timer engine to allow time feedback
"""
import time
from threading import Timer
from typing import Any, Callable, Union


class FeedbackTimer(Timer):
    """
        Simplistic timer engine to allow remote feedback
    """

    def __init__(self, interval: Union[float, int], function: Callable, args: Any = None, kwargs: Any = None) -> None:
        """ Timer constructor

        :param interval: in seconds
        :param function: the callback function
        :param args: args
        :param kwargs: kwargs
        """
        #  call class constructor
        Timer.__init__(self, interval, function, args, kwargs)
        #  init the start time
        self.start_time = None

    def start(self) -> None:
        """ Start the timer

        :return:
        """
        # Set the time
        self.start_time = time.time()
        # kick off the time event
        super().start()

    def elapsed(self) -> Union[float, None]:
        """ get the time that has elapsed between the start time and the current time

        :return:
        """
        if self.is_alive():
            return time.time() - self.start_time
        else:
            return None

    def remaining(self) -> Union[float, None]:
        """ get the time that "should be" left on the Timer, this will be off by some cycles but its good for our needs

        :return:
        """
        if self.is_alive():
            # noinspection PyUnresolvedReferences
            return self.interval - self.elapsed()
        else:
            return None
