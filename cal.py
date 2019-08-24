import json

def set_cal(new_min, new_max):
    dict_cal = {"min" : new_min, "max" : new_max}
    with open("cal.json", "w") as cal_file:
        cal_file.truncate()
        json.dump(dict_cal, cal_file)

def get_cal():
    with open("cal.json", "r") as cal_file:
        dict_cal = json.load(cal_file)
        return dict_cal
