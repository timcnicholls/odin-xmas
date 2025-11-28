import logging
from concurrent import futures
from time import sleep
import random

from colorzero import Color, Hue
from odin.adapters.parameter_tree import ParameterTree
from tornado.concurrent import run_on_executor

from .rgb_pixel_array import RGBPixelArray


class XmasController:

    def __init__(self):
        brightness = 0.25

        array_params = {
            "tree": { 
                "mosi_pin": 12, "miso_pin":  9, "clock_pin": 25, "select_pin":  8,
                "reverse_pixel_mode":False 
            },
            "house": { 
                "mosi_pin": 23, "miso_pin": 11, "clock_pin": 24, "select_pin": 10,
                "reverse_pixel_mode":True 
            },
        }

        executor = futures.ThreadPoolExecutor(max_workers=len(array_params))

        self.arrays = {}
        param_tree = {
            "modes": XmasLightArray.MODES,
            "led_colours": XmasLightArray.LED_COLOURS,
        }

        for name, params in array_params.items():
            self.arrays[name] = XmasLightArray(
                name=name, brightness=brightness, executor=executor, **params
            )
            param_tree[name] = self.arrays[name].param_tree

        self.param_tree = ParameterTree(param_tree)

    def initialize(self):
        for array in self.arrays.values():
            try:
                array.background_task()
            except Exception as e:
                print(e)

    def cleanup(self):
        for array in self.arrays.values():
            array.stop_background_task()
            array.off()
            array.close()

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

class XmasLightArray:

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

    def __init__(self, name, brightness, executor, **array_params):

        self.name = name.capitalize()
        self.brightness = brightness
        self.executor = executor

        self._led_colour = "white"
        self._mode = "static"

        self.array = RGBPixelArray(brightness = self.brightness, **array_params)

        self.param_tree = ParameterTree(
            {
                "led_colour": (lambda: self._led_colour, self.set_led_colour),
                "brightness": (lambda: self.array.brightness, self.set_brightness),
                "mode": (lambda: self._mode, self.set_mode),
            }
        )

        self._run_background_task = True

    def set_enable(self, value):
        value = bool(value)
        if value:
            self.array.color = Color(self._led_colour)
        else:
            self.array.off()

    def set_led_colour(self, colour):
        if colour in self.LED_COLOURS:
            self._led_colour = colour
        if self._mode == 'static':
            self.array.color = Color(self._led_colour)

    def set_brightness(self, brightness):
        if 0.0 <= brightness <= 1.0:
            self.array.brightness = brightness

    def set_mode(self, mode):
        if mode in self.MODES:
            self._mode = mode

    def off(self):
        self.array.off()

    def close(self):
        self.array.close()

    @run_on_executor(executor="executor")
    def background_task(self):

        logging.debug(f"{self.name} starting background task")
        while self._run_background_task:
            getattr(self, f"{self._mode}_task")()

        logging.debug(f"{self.name} ending background task")

    def stop_background_task(self):

        self._run_background_task = False

    def off_task(self):
        logging.debug(f"{self.name} entering off mode")
        self.set_enable(False)
        while self._mode == 'off' and self._run_background_task:
            sleep(0.1)
        logging.debug(f"{self.name} exiting off mode")

    def static_task(self):
        logging.debug(f"{self.name} entering static mode")
        self.set_enable(True)
        self.set_led_colour(self._led_colour)
        while self._mode == 'static' and self._run_background_task:
            sleep(0.1)
        logging.debug(f"{self.name} exiting static mode")

    def sparkle_task(self):
        logging.debug(f"{self.name} entering sparkle mode")
        self.set_enable(True)

        def random_colour():
            r = random.random()
            g = random.random()
            b = random.random()
            return (r, g, b)

        while self._mode == 'sparkle' and self._run_background_task:
            pixel = random.choice(self.array)
            pixel.color = random_colour()

        logging.debug(f"{self.name} exiting sparkle mode")

    def random_task(self):
        logging.debug(f"{self.name} entering random mode")
        self.set_enable(True)

        while self._mode == 'random' and self._run_background_task:
            self.array.color = Color(random.choice(self.LED_COLOURS))
            sleep(0.5)
        logging.debug(f"{self.name} exiting random mode")

    def cycle_task(self):
        logging.debug(f"{self.name} entering cycle mode")
        self.set_enable(True)

        self.array.color = Color('red')
        while self._mode == 'cycle' and self._run_background_task:
            self.array.color += Hue(deg=1)
        logging.debug(f"{self.name} exiting cycle mode")
