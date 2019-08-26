import time

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
