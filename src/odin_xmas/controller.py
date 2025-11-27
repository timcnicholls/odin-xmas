import logging
from concurrent import futures
from time import sleep
import random

from colorzero import Color, Hue
from odin.adapters.parameter_tree import ParameterTree
from tornado.concurrent import run_on_executor

from .tree import RGBXmasTree


class XmasController:
    LED_COLOURS = [
        "red",
        "orange",
        "yellow",
        "green",
        "blue",
        "indigo",
        "violet",
        "white",
    ]
    MODES = ["off", "static", "sparkle", "random", "cycle"]

    executor = futures.ThreadPoolExecutor(max_workers=1)

    def __init__(self):
        self._led_colour = "white"
        self._mode = "static"
        brightness = 0.25

        self.tree = RGBXmasTree(brightness=brightness)

        self.param_tree = ParameterTree(
            {
                "led_colour": (lambda: self._led_colour, self.set_led_colour),
                "brightness": (lambda: self.tree.brightness, self.set_brightness),
                "mode": (lambda: self._mode, self.set_mode),
                "modes": self.MODES,
                "led_colours": self.LED_COLOURS,
            }
        )

        self._run_background_task = True

    def initialize(self):
        self.background_task()

    def cleanup(self):
        self._run_background_task = False
        self.tree.off()
        self.tree.close()

    def get(self, path):
        """Get values from the parameter tree.

        This method returns values from parameter tree to the adapter.

        :param path: path to retrieve from tree
        """
        return self.param_tree.get(path)

    def set(self, path, data):
        """Set values in the parameter tree.

        This method sets values in the parameter tree.

        :param path: path of data to set in the tree
        :param data: data to set in tree
        """
        # Update values in the tree at the specified path
        self.param_tree.set(path, data)

        # Return updated values from the tree
        return self.param_tree.get(path)

    def set_enable(self, value):
        value = bool(value)
        if value:
            self.tree.color = Color(self._led_colour)
        else:
            self.tree.off()

    def set_led_colour(self, colour):
        if colour in self.LED_COLOURS:
            self._led_colour = colour
        if self._mode == 'static':
            self.tree.color = Color(self._led_colour)

    def set_brightness(self, brightness):
        if 0.0 <= brightness <= 1.0:
            self.tree.brightness = brightness

    def set_mode(self, mode):
        if mode in self.MODES:
            self._mode = mode

    @run_on_executor
    def background_task(self):

        logging.debug("Starting background task")
        while self._run_background_task:
            getattr(self, f"{self._mode}_task")()

        logging.debug("Ending background task")

    def off_task(self):
        logging.debug("Entering off mode")
        self.set_enable(False)
        while self._mode == 'off' and self._run_background_task:
            sleep(0.1)
        logging.debug("Exiting off mode")

    def static_task(self):
        logging.debug("Entering static mode")
        self.set_enable(True)
        self.set_led_colour(self._led_colour)
        while self._mode == 'static' and self._run_background_task:
            sleep(0.1)
        logging.debug("Exiting static mode")

    def sparkle_task(self):
        logging.debug("Entering sparkle mode")
        self.set_enable(True)

        def random_colour():
            r = random.random()
            g = random.random()
            b = random.random()
            return (r, g, b)

        while self._mode == 'sparkle' and self._run_background_task:
            pixel = random.choice(self.tree)
            pixel.color = random_colour()
        logging.debug("Exiting sparkle mode")

    def random_task(self):
        logging.debug("Entering random mode")
        self.set_enable(True)

        while self._mode == 'random' and self._run_background_task:
            self.tree.color = Color(random.choice(self.LED_COLOURS))
            sleep(1.0)
        logging.debug("Exiting random mode")

    def cycle_task(self):
        logging.debug("Entering cycle mode")
        self.set_enable(True)

        self.tree.color = Color('red')
        while self._mode == 'cycle' and self._run_background_task:
            self.tree.color += Hue(deg=1)
        logging.debug("Exiting cycle mode")
