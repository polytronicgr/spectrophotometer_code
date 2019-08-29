"""This code contains functions called by gui.py.

This software is licensed under the MIT license.

"""

import time

from picamera.array import PiRGBArray
from picamera import PiCamera
from gpiozero import LED

import numpy as np
from PIL import Image

__author__ = "Daniel James Evans"
__copyright__ = "Copyright 2019, Daniel James Evans"
__license__ = "MIT"

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
time.sleep(0.5)


def get_color_image():
    """Take a color image using the camera.  Return as a numpy array."""

    led = LED(4)
    led.on()

    output = np.empty((480, 640, 3), dtype=np.uint8)
    camera.capture(output, "rgb")
    led.off()
    return output

def get_bw_image():
    """Return a numpy array of a grayscale image from the camera.
    I couldn't figure out the proper way
    to do this, so the function saves the image as bw.png.

    The function takes 3 pictures and averages the values from
    each picture.  This is done to reduce noise."""

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
    image_arr_1 = np.array(image_pil)

    time.sleep(0.1)
    camera.capture("bw.png")
    image_pil = Image.open("bw.png")
    image_arr_2 = np.array(image_pil)
    
    time.sleep(0.1)
    camera.capture("bw.png")
    image_pil = Image.open("bw.png")
    image_arr_3 = np.array(image_pil)

    image_arr = (image_arr_1.astype(np.int16) + image_arr_2.astype(np.int16) + image_arr_3.astype(np.int16)) / 3
    image_arr = image_arr.astype(np.uint8)

    camera.color_effects = None
    led.off()

    # Each pixel has 3 values (plus a 4th).
    # But the values are identical
    # (+/- 1) because of camera.color_effects.
    return image_arr[:, :, 1]
