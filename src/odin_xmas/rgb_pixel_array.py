from gpiozero import SPIDevice, SourceMixin
from colorzero import Color, Hue
from statistics import mean
from time import sleep


class Pixel:
    def __init__(self, parent, index):
        self.parent = parent
        self.index = index

    @property
    def value(self):
        return self.parent.value[self.index]

    @value.setter
    def value(self, value):
        new_parent_value = list(self.parent.value)
        new_parent_value[self.index] = value
        self.parent.value = tuple(new_parent_value)

    @property
    def color(self):
        return Color(*self.value)

    @color.setter
    def color(self, c):
        r, g, b = c
        self.value = (r, g, b)

    def on(self):
        self.value = (1, 1, 1)

    def off(self):
        self.value = (0, 0, 0)


class RGBPixelArray(SourceMixin, SPIDevice):
    def __init__(
        self, pixels=26, brightness=0.5, 
        mosi_pin=23, miso_pin=9, clock_pin=24, select_pin=8, reverse_pixel_mode=False,
        *args, **kwargs
    ):
        super(RGBPixelArray, self).__init__(
            mosi_pin=mosi_pin, miso_pin=miso_pin, clock_pin=clock_pin, select_pin=select_pin, 
            *args, **kwargs
        )
        self.reverse_pixel_mode = reverse_pixel_mode
        self._all = [Pixel(parent=self, index=i) for i in range(pixels)]
        self._value = [(0, 0, 0)] * pixels
        self.brightness = brightness
        self.off()

    def __len__(self):
        return len(self._all)

    def __getitem__(self, index):
        return self._all[index]

    def __iter__(self):
        return iter(self._all)

    @property
    def color(self):
        average_r = mean(pixel.color[0] for pixel in self)
        average_g = mean(pixel.color[1] for pixel in self)
        average_b = mean(pixel.color[2] for pixel in self)
        return Color(average_r, average_g, average_b)

    @color.setter
    def color(self, c):
        r, g, b = c
        self.value = ((r, g, b),) * len(self)

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        max_brightness = 31
        self._brightness_bits = int(brightness * max_brightness)
        self._brightness = brightness
        self.value = self.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        start_of_frame = [0]*4
        end_of_frame = [0]*5
                     # SSSBBBBB (start, brightness)
        brightness = 0b11100000 | self._brightness_bits
        pixels = [[int(255*v) for v in p] for p in value]
        if self.reverse_pixel_mode:
            pixels = [[brightness, r, b, g] for r, g, b in pixels]
        else:
            pixels = [[brightness, b, g, r] for r, g, b in pixels]

        pixels = [i for p in pixels for i in p]
        data = start_of_frame + pixels + end_of_frame
        self._spi.transfer(data)
        self._value = value

    def on(self):
        self.value = ((1, 1, 1),) * len(self)

    def off(self):
        self.value = ((0, 0, 0),) * len(self)

    def close(self):
        super(RGBPixelArray, self).close()


if __name__ == '__main__':
    tree = RGBPixelArray()
    
    tree.on()
