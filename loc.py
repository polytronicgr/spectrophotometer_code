"""This code contains functions called by gui.py.

This software is licensed under the MIT license.

"""

import json

__author__ = "Daniel James Evans"
__copyright__ = "Copyright 2019, Daniel James Evans"
__license__ = "MIT"

def set_loc(new_x, new_y, new_length):
    """Update loc.json with new values."""
    dict_loc = {"x" : new_x, "y" : new_y, "length" : new_length}
    with open("loc.json", "w") as loc_file:
        loc_file.truncate()
        json.dump(dict_loc, loc_file)

def get_loc():
    """Read loc.json, and return its contents as a dictionary."""
    with open("loc.json", "r") as loc_file:
        dict_loc = json.load(loc_file)
        return dict_loc
