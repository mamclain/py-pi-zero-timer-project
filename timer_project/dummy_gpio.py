"""
A class to emulate RPi.GPIO on windows
"""


class DummyGPIO(object):
    """
    A class to emulate RPi.GPIO on windows
    """

    # from RPi.GPIO
    MODE_UNKNOWN = -1
    BOARD = 10
    BCM = 11
    SERIAL = 40
    SPI = 41
    I2C = 42
    PWM = 43
    SETUP_OK = 0
    SETUP_DEVMEM_FAIL = 1
    SETUP_MALLOC_FAIL = 2
    SETUP_MMAP_FAIL = 3
    SETUP_CPUINFO_FAIL = 4
    SETUP_NOT_RPI_FAIL = 5
    INPUT = 1
    OUTPUT = 0
    ALT0 = 4
    HIGH = 1
    LOW = 0
    PUD_OFF = 0
    PUD_DOWN = 1
    PUD_UP = 2
    OUT = OUTPUT  # did not look this up in source (seems like it should be output)

    def __init__(self) -> None:
        """
        A class to emulate RPi.GPIO on windows
        """
        pass

    @staticmethod
    def setmode(value) -> None:
        """ set the GPIO Mode

        :param value:
        :return:
        """
        pass

    @staticmethod
    def setup(value, state) -> None:
        pass

    @staticmethod
    def output(port, value) -> None:
        print("Output State is %s" % value)
        pass
