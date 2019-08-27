"""This code turns on the LED and displays a video feed
from the camera.  The video feed only lasts 2 minutes.
Usage: "python3 show_video.py".

"""

import time

__author__ = "Daniel James Evans"
__copyright__ = "Copyright 2019, Daniel James Evans"
__license__ = "MIT"

from picamera.array import PiRGBArray
from picamera import PiCamera


from gpiozero import LED

led = LED(4)
led.on()



camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
camera.start_preview()
time.sleep(120)
