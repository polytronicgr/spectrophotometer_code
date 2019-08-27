"""This code runs a GUI for Raspberry Pi spectrophotometers that use the pi camera
port.  It was written for Danny Evans's spectrophotometer.  To run the code, cd
into the directory then type "python3 gui.py".  You must be in the same directory
as the code, and you must use python 3 (not python 2).

This software is licensed under the MIT license.

"""

import shutil
import csv
import tkinter
import tkinter.filedialog

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

from loc import get_loc, set_loc
from cal import get_cal, set_cal
from get_image import get_color_image, get_bw_image

__author__ = "Daniel James Evans"
__copyright__ = "Copyright 2019, Daniel James Evans"
__license__ = "MIT"

def plot_fig(data, out_file_loc, cal, data_title):
    """Graph data and save the result as an image.

    The function takes a 1D array of y-values; it assumes that the x-values are evenly
    spaced.

    Parameters
    ----------
    data : 1D list or numpy array
        It contains the y-values of the points to be graphed.  The x-values should be
        evenly spaced points between the min and max described in cal.
    out_file_loc : string
        The path of where the image should be saved to.
    cal : dictionary
        It contains 2 keys: "min" and "max".  The values are the minimum and maximum
        values (float or int) of the x-axis.
    data_title : string
        The title of the graph.

    """

    fig = plt.figure()
    plt.title(data_title)
    xticks_locs = np.arange(0, len(data)+1, len(data)/5)
    xticks_step = (cal["max"] - cal["min"]) / 5
    xticks_labels_array = np.arange(cal["min"], cal["max"]+xticks_step, step=xticks_step)
    xticks_labels_list = []
    for label in xticks_labels_array:
        xticks_labels_list.append("%.2f" % round(label, 2))
    plt.xticks(xticks_locs, labels=xticks_labels_list)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Absorbance")
    plt.plot(data)
    fig.savefig(out_file_loc)


class MeasurementWindow(tkinter.Toplevel):
    """Window for beginning the process of blanking and measuring a sample.

    After using a MeasurementWindow, a BlankMeasWindow is created.

    Parameters
    ----------
    is_cal : bool
        True if calibrating; False if taking a measurement to save.

    """

    def __init__(self, is_cal):
        tkinter.Toplevel.__init__(self)
        self.title("Take a Measurement")
        self.is_cal = is_cal
        self.button_for_blank = tkinter.Button(self, text="\t\t\t\tMeasure Blank\t\t\t\t",
                                               command=self.move_to_blank)
        self.button_for_blank.pack()
        if is_cal:
            self.data_title = "Calibration"
        else:
            self.withdraw()
            self.toplevel_for_title = tkinter.Toplevel(self)
            self.toplevel_for_title.title("Title Selection")
            self.title_label_text = "Please enter a title for the results."
            self.title_label = tkinter.Label(self.toplevel_for_title,
                                             text=self.title_label_text)
            self.title_label.pack()
            self.title_entry = tkinter.Entry(self.toplevel_for_title)
            self.title_entry.pack()
            self.title_button = tkinter.Button(self.toplevel_for_title, text="Continue",
                                               command=self.choose_title)
            self.title_button.pack()


    def choose_title(self):
        """When the user has selected a title, re-display self."""

        self.data_title = self.title_entry.get()
        self.toplevel_for_title.destroy()
        self.deiconify()


    def move_to_blank(self):
        """Destroy the window and initialize a BlankMeasWindow.  Note that the
        BlankMeasWindow's initialization involves taking an image.

        """

        self.destroy()
        BlankMeasWindow(self.is_cal, self.data_title)


class BlankMeasWindow(tkinter.Toplevel):
    """Window for measuring a blank.

    The BlankMeasWindow is created by a MeasurementWindow.  After using a BlankMeasWindow,
    the blank is measured and a SampleMeasWindow is created.

    Parameters
    ----------
    is_cal : bool
        True if calibrating; False if taking a measurement to save.
    data_title : string
        The title of the graph to be created.

    """

    def __init__(self, is_cal, data_title):
        tkinter.Toplevel.__init__(self)
        self.title("Take a Measurement")
        self.is_cal = is_cal
        self.data_title = data_title
        self.blank_array = get_bw_image()
        loc = get_loc()
        self.blank_row = self.blank_array[loc["y"] : loc["y"]+loc["length"], loc["x"]]
        self.title("Take a Measurement")
        self.button_for_reading = tkinter.Button(self, text="\t\tMeasure Sample\t\t",
                                                 command=self.move_to_sample)
        self.button_for_reading.pack()


    def move_to_sample(self):
        """Destroy the window and initialize a SampleMeasWindow.  Note that the
        SampleMeasWindow's initialization involves taking an image.

        """

        self.destroy()
        SampleMeasWindow(self.is_cal, self.blank_row, self.data_title)


class SampleMeasWindow(tkinter.Toplevel):
    """Window for measuring a sample.

    The SampleMeasWindow is created by a BlankMeasWindow.  After using a SampleMeasWindow,
    the sample is measured and a FinishCalibrationWindow or FinishSampleWindow is created.

    Parameters
    ----------
    is_cal : bool
        True if calibrating; False if taking a measurement to save.
    blank_row : 1D list or numpy array
        The data points from when the blank was measured.
    data_title : string
        The title of the graph to be created.

    """

    def __init__(self, is_cal, blank_row, data_title):
        tkinter.Toplevel.__init__(self)
        self.title("Take a Measurement")
        sample_array = get_bw_image()
        loc = get_loc()
        sample_row = sample_array[loc["y"] : loc["y"]+loc["length"], loc["x"]]
        # I don't want to do math on uint8s.
        sample_row = sample_row.astype(np.int16)
        blank_row = blank_row.astype(np.int16)
        data = np.log10(blank_row / sample_row)
        for i in range(len(data)):
            print("blank", blank_row[i], "sample", sample_row[i], "data", data[i])
        cal = get_cal()
        plot_fig(data, "out.png", cal, data_title)
        self.destroy()
        if is_cal:
            FinishCalibrationWindow(sample_row, blank_row)
        else:
            FinishSampleWindow(data)


class FinishCalibrationWindow(tkinter.Toplevel):
    """Window for finishing the calibration process.

    The FinishCalibrationWindow is created by a SampleMeasWindow.  It displays a
    graph, and allows the user to specify the minimum and maximum points on the
    x-axis.

    Parameters
    ----------
    sample_row : 1D list or numpy array
        The data points from when the sample was measured.
    blank_row : 1D list or numpy array
        The data points from when the blank was measured.

    """

    def __init__(self, sample_row, blank_row):
        tkinter.Toplevel.__init__(self)
        self.title("Calibrate the x axis")
        self.sample_row = sample_row
        self.blank_row = blank_row
        self.cal_image_tk = ImageTk.PhotoImage(file="out.png")
        self.panel_cal = tkinter.Label(self, image=self.cal_image_tk)
        self.panel_cal.image = self.cal_image_tk # Necessary b/c of garbage collector.
        self.panel_cal.pack()
        self.cal_canvas = tkinter.Canvas(self)
        self.cal_min_label = tkinter.Label(self.cal_canvas,
                                           text="Wavelength at left edge")
        self.cal_min_label.pack()
        self.cal_min_entry = tkinter.Entry(self.cal_canvas)
        self.cal_min_entry.pack()

        self.cal_max_label = tkinter.Label(self.cal_canvas,
                                           text="Wavelength at right edge")
        self.cal_max_label.pack()
        self.cal_max_entry = tkinter.Entry(self.cal_canvas)
        self.cal_max_entry.pack()

        self.cal_min_entry.insert(0, app.cal["min"])
        self.cal_max_entry.insert(0, app.cal["max"])
        self.update()

        self.cal_button = tkinter.Button(self.cal_canvas, text="Update calibration",
                                         command=self.update_cal)
        self.cal_button.pack()
        cal_end_button_text = "The graph looks correct; end calibration."
        self.cal_end_button = tkinter.Button(self.cal_canvas, text=cal_end_button_text,
                                             command=self.destroy)
        self.cal_end_button.pack()
        self.cal_canvas.pack()


    def update_cal(self):
        """Called when the user presses the update button.  Gets and saves the new
        values for the calibration that were entered into the window.  Updates the graph
        on the screen.

        """

        min_val_entered = self.cal_min_entry.get()
        max_val_entered = self.cal_max_entry.get()
        app.update_cal(min_val_entered, max_val_entered, self.sample_row, self.blank_row)
        self.cal_image_tk = ImageTk.PhotoImage(file="out.png")
        self.panel_cal.config(image=self.cal_image_tk)
        self.panel_cal.image = self.cal_image_tk


class FinishSampleWindow(tkinter.Toplevel):
    """Window for finishing the process of measuring a sample.

    The FinishSampleWindow is created by a SampleMeasWindow.  It displays a
    graph, and allows the user to save the data if desired.

    """

    def __init__(self, data):
        self.data = data
        tkinter.Toplevel.__init__(self)
        self.title("Take a Measurement")
        self.preview_image_tk = ImageTk.PhotoImage(file="out.png")
        self.panel_preview = tkinter.Label(self, image=self.preview_image_tk)
        self.panel_preview.image = self.preview_image_tk
        self.panel_preview.pack()
        label_preview_text = "Here is the result.  Do you want to save it?"
        self.label_preview = tkinter.Label(self, text=label_preview_text)
        self.label_preview.pack()
        self.button_save_preview = tkinter.Button(self, text="Yes; Save the Result",
                                                  command=self.save_result)
        self.button_save_preview.pack()
        self.button_delete_preview = tkinter.Button(self, text="No; Delete the Result",
                                                    command=self.destroy)
        self.button_delete_preview.pack()


    def save_result(self):
        """Begin the process of saving the graph and csv file.  This function
        initializes a window containing a button; when the user presses the button,
        self.save_graph() is called.

        """

        save_graph_title = "Select Location To Save Graph"
        self.save_graph_toplevel = tkinter.Toplevel(self)
        self.save_graph_toplevel.title(save_graph_title)
        label_save_graph_text = "First, select a location to save the graph."
        self.label_save_graph = tkinter.Label(self.save_graph_toplevel,
                                              text=label_save_graph_text)
        self.label_save_graph.pack()
        self.button_save_graph = tkinter.Button(self.save_graph_toplevel,
                                                text="Select Location For Graph",
                                                command=self.save_graph)
        self.button_save_graph.pack()


    def save_graph(self):
        """Ask the user where to save the graph.  Save it, and
        call self.save_data_intro().

        """

        self.save_graph_toplevel.destroy()
        sample_graph_loc = tkinter.filedialog.asksaveasfilename()
        if sample_graph_loc != "":
            shutil.copyfile("out.png", sample_graph_loc)
            self.save_data_intro()


    def save_data_intro(self):
        """Initialize a window informing the user that it is time to save the csv file.
        When the user presses a button, call self.save_data().

        """

        save_data_title = "Select Location To Save Data"
        self.save_data_toplevel = tkinter.Toplevel(self)
        self.save_data_toplevel.title(save_data_title)
        label_save_data_text = "Next, select a location to save the data as a csv file."
        self.label_save_data = tkinter.Label(self.save_data_toplevel,
                                             text=label_save_data_text)
        self.label_save_data.pack()
        self.button_save = tkinter.Button(self.save_data_toplevel,
                                          text="Select Location For CSV",
                                          command=self.save_data)
        self.button_save.pack()


    def save_data(self):
        """Ask the user where to save the csv file.  Save the file."""

        self.save_data_toplevel.destroy()
        sample_data_loc = tkinter.filedialog.asksaveasfilename()
        if sample_data_loc != "":
            cal = get_cal()
            wavelength_step = (cal["max"] - cal["min"]) / len(self.data)
            wavelength_array = np.arange(cal["min"], cal["max"]+wavelength_step,
                                         step=wavelength_step)
            with open(sample_data_loc, mode="w") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"',
                                        quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(["Wavelength (nm)", "Absorbance"])
                for i in range(len(self.data)):
                    csv_writer.writerow([wavelength_array[i], self.data[i]])
            self.destroy()


class LocateSpectrumWindow(tkinter.Toplevel):
    """Window for locating the diffraction spectrum.

    The LocateSpectrumWindow displays an image taken by the camera.  The user
    enters the location (in pixels) of the diffraction spectrum.

    """

    def __init__(self):
        tkinter.Toplevel.__init__(self)
        self.title("Diffraction Spectrum Location")
        self.label_text = ("Find a diffraction spectrum in the image.")
        self.label = tkinter.Label(self, text=self.label_text)
        self.label.pack()
        self.image_array = get_color_image()
        self.image_tk = ImageTk.PhotoImage(image=Image.fromarray(self.image_array))
        self.panel_loc = tkinter.Label(self, image=self.image_tk)
        self.panel_loc.image = self.image_tk
        self.panel_loc.pack()
        self.move_spec_canvas = tkinter.Canvas(self)
        x_loc_label_text = "x location (less than %d)" %(self.image_array.shape[1])
        self.x_loc_label = tkinter.Label(self.move_spec_canvas, text=x_loc_label_text)
        self.x_loc_label.pack()
        self.x_loc_entry = tkinter.Entry(self.move_spec_canvas)
        self.x_loc_entry.pack()

        y_loc_label_text = "y location (less than %d)" %(self.image_array.shape[0])
        self.y_loc_label = tkinter.Label(self.move_spec_canvas, text=y_loc_label_text)
        self.y_loc_label.pack()
        self.y_loc_entry = tkinter.Entry(self.move_spec_canvas)
        self.y_loc_entry.pack()

        length_label_text = "length (y+length<%d)" %(self.image_array.shape[1])
        self.length_label = tkinter.Label(self.move_spec_canvas, text=length_label_text)
        self.length_label.pack()
        self.length_entry = tkinter.Entry(self.move_spec_canvas)
        self.length_entry.pack()

        self.move_spec_canvas.pack()
        old_loc = get_loc()
        self.x_loc_entry.insert(0, old_loc["x"])
        self.y_loc_entry.insert(0, old_loc["y"])
        self.length_entry.insert(0, old_loc["length"])
        self.update()
        self.update_loc_from_gui() # Initialize the line.

        self.menu_canvas = tkinter.Canvas(self)
        self.update_button = tkinter.Button(self.menu_canvas,
                                            command=self.update_loc_from_gui,
                                            text="Update")
        self.update_button.pack()
        self.dismiss_button = tkinter.Button(self.menu_canvas, command=self.cal_after_loc,
                                             text="Proceed to Calibration")
        self.dismiss_button.pack()
        self.menu_canvas.pack()

    def cal_after_loc(self):
        """After the user has located the spectrum, it is necessary to calibrate the
        x-axis.  Destroy the top-level and initialize a MeasurementWindow with
        is_cal=True in order to calibrate the axis.

        """

        self.destroy()
        MeasurementWindow(True)

    def update_loc_from_gui(self):
        """Called when the user enters a location of the spectrum.  The displayed
        image draws a line where the spectrum is said to be, and loc.json is updated.

        """

        try:
            new_x = int(self.x_loc_entry.get())
            new_y = int(self.y_loc_entry.get())
            new_length = int(self.length_entry.get())
            self.image_line_array = np.copy(self.image_array)
            new_x_good = (new_x < self.image_line_array.shape[1]) and (new_x > 0)
            new_y_good = new_y > 0
            new_length_good = ((new_y + new_length < self.image_line_array.shape[0]) and
                               (new_length > 0))
            if new_x_good and new_y_good and new_length_good:
                set_loc(new_x, new_y, new_length)
                line_t = new_y
                line_b = new_y + new_length
                line_l_edge = max(new_x-5, 0)
                line_r_edge = min(new_x+5, self.image_line_array.shape[1])

                # Draw a red line where the location is.
                self.image_line_array[line_t : line_b,\
                                      line_l_edge : line_r_edge] = np.array([255, 0, 0])
                image_pil = Image.fromarray(self.image_line_array)
                self.image_line_tk = ImageTk.PhotoImage(image=image_pil)
                self.panel_loc.configure(image=self.image_line_tk)
                self.panel_loc.image = self.image_line_tk
            else:
                self.complain_bad_loc_val()
        except ValueError:
            self.complain_bad_loc_val()


    def complain_bad_loc_val(self):
        """Display an error message is the user provides invalid input."""

        toplevel_for_complaint = tkinter.Toplevel(self)
        toplevel_for_complaint.title("Error: Bad Input!")
        complaint_text = ("Either a value isn't an integer, or the position goes beyond "
                          "the image size.")
        complaint_label = tkinter.Label(toplevel_for_complaint, text=complaint_text)
        complaint_label.pack()
        dismiss_button = tkinter.Button(toplevel_for_complaint,
                                        command=toplevel_for_complaint.destroy,
                                        text="Dismiss")
        dismiss_button.pack()


class SpecApp(tkinter.Tk):
    """Toplevel class that is initialized when the app starts."""
    def __init__(self):
        tkinter.Tk.__init__(self, *args, **kwargs) # Initialize tkinter.
        # Display a window when the program starts.
        self.title("Main Menu")

        loc_spec_text = "Locate the Spectrum Then Calibrate the Axes"
        self.loc_spec_button = tkinter.Button(self, command=LocateSpectrumWindow,
                                              text=loc_spec_text)
        self.loc_spec_button.pack()
        self.cal_axes_button = tkinter.Button(self,
                                              command=lambda: MeasurementWindow(True),
                                              text="Calibrate the Axes")
        self.cal_axes_button.pack()
        self.measure_button = tkinter.Button(self,
                                             command=lambda: MeasurementWindow(False),
                                             text="Take Blank and Sample Measurement")
        self.measure_button.pack()
        self.cal = get_cal()


    def update_cal(self, new_min_string, new_max_string, sample_row, blank_row):
        """Update cal.json with new calibration values.  Update the calibration
        graph at out.png.  Note that this function doesn't display the new graph.
        It is called by a FinishCalibrationWindow object that updates the window.

        """

        try:
            new_min = float(new_min_string)
            new_max = float(new_max_string)
            if new_min < new_max:
                set_cal(new_min, new_max)
                self.cal = {"min" : new_min, "max" : new_max}
                # I don't want to do math on uint8s.
                sample_row = sample_row.astype(np.int16)
                blank_row = blank_row.astype(np.int16)
                data = np.log10(blank_row / sample_row)
                out_file_loc = "out.png"
                plot_fig(data, out_file_loc, self.cal, "Calibration")
            else:
                self.complain_bad_cal_val()
        except ValueError:
            self.complain_bad_cal_val()


    def complain_bad_cal_val(self):
        """Display an error message is the user provides invalid input."""

        toplevel_for_complaint = tkinter.Toplevel(self)
        toplevel_for_complaint.title("Error: Bad Input!")
        complaint_text = ("Either a value isn't a number, or the minimum is greater than "
                          "the maximum.")
        complaint_label = tkinter.Label(toplevel_for_complaint,
                                        text=complaint_text)
        complaint_label.pack()
        dismiss_button = tkinter.Button(toplevel_for_complaint,
                                        command=toplevel_for_complaint.destroy,
                                        text="Dismiss")
        dismiss_button.pack()


app = SpecApp()
app.mainloop()
