"""This code contains functions called by gui.py.

This software is licensed under the MIT license.

"""


import json

__author__ = "Daniel James Evans"
__copyright__ = "Copyright 2019, Daniel James Evans"
__license__ = "MIT"

def set_cal(new_min, new_max):
    """Update cal.json with new values."""
    dict_cal = {"min" : new_min, "max" : new_max}
    with open("cal.json", "w") as cal_file:
        cal_file.truncate()
        json.dump(dict_cal, cal_file)

def get_cal():
    """Read cal.json, and return its contents as a dictionary."""
    with open("cal.json", "r") as cal_file:
        dict_cal = json.load(cal_file)
        return dict_cal
