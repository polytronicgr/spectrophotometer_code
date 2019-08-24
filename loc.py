import json

def set_loc(new_x, new_y, new_length):
    dict_loc = {"x" : new_x, "y" : new_y, "length" : new_length}
    with open("loc.json", "w") as loc_file:
        loc_file.truncate()
        json.dump(dict_loc, loc_file)

def get_loc():
    with open("loc.json", "r") as loc_file:
        dict_loc = json.load(loc_file)
        return dict_loc
