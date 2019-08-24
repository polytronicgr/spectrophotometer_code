import time

from picamera.array import PiRGBArray
from picamera import PiCamera
from gpiozero import LED

import numpy as np
from PIL import Image


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
time.sleep(0.5)


def get_color_image():
    led = LED(4)
    led.on()

    output = np.empty((480, 640, 3), dtype=np.uint8)
    camera.capture(output, "rgb")
    led.off()
    return output

def get_bw_image():
    led = LED(4)
    led.on()

    # I couldn't find a way for the
    # camera to pass a grayscale
    # image directly to numpy.  So
    # the code saves a grayscale
    # image file then reads it.
    camera.color_effects = (128, 128)
    camera.capture("bw.png")
    image_pil = Image.open("bw.png")
    image_arr = np.array(image_pil)

    camera.color_effects = None
    led.off()

    # Each pixel has 3 values (plus a 4th).
    # But the values are identical
    # (+/- 1) because of camera.color_effects.
    return image_arr[:, :, 1]

