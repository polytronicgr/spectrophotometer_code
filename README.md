# Raspberry Pi Spectrophotometer Code
##### This code was written to operate Danny Evans's spectrophotometer.
## Installation:
The code can be cloned from this github repository.  Running the code requires the following modules:
* numpy
* matplotlib
* PIL (including ImageTk)
To install them, run the following:
```
pip3 install numpy
pip3 install matplotlib
sudo apt-get install python3-pil python3-pil.imagetk
```
You may be prompted to enter your password; this is because of the `sudo` command.
## Usage:
1. To run the gui, open the terminal and `cd` into the directory containing the code.  Then run the command
`python3 gui.py`.
2. After building the spectrophotometer, the Pi doesn't know where the diffraction grating is
in the camera's field of view.  To find it, click "Locate the Spectrum Then Calibrate the Axes".  An image will
appear.  The bottom will contain a white rectangle; this is the slit.  Above the slit will be a rainbow-like region
that is the diffraction spectrum.  Edit the values in the window until the red line is on the spectrum.
* The y-axis points downwards; the x-axis points to the right.  So higher numbers are towards the bottom right
corner.
* The line should cover most of the spectrum.  But it shouldn't extend beyond the spectrum.
* If a diffraction spectrum isn't visible, then the hardware isn't functioning correctly.  Is the diffraction grating
in a vertical orientation?  Is the LED in line with the slit?
3. After finding the slit, it is necessary to calibrate the spectrophotometer.  This means finding which points in the
spectrum's graph correspond to which wavelengths.  This is often done by shining light with a known wavelength (i.e. a laser)
into the spectrophotometer.  Because lasers are expensive and dangerous, this spectrophotometer uses a different procedure:
* The user measures a sample with a known spectrum.  Extra virgin olive oil works well for this because its spectrum is available
online.
* The user is shown a graph of the measured spectrum, and prompted to choose the minimum and maximum values of the x-axis.  This is done
by visually comparing the measured spectrum to the known spectrum.
4. Before taking a measurement, it is necessary to take a "blank" measurement with no sample.  This is so that the software can compare
the spectrum with the sample to the spectrum without the sample.  This software requires users to measure a blank before each sample measurement.
* To measure the blank and sample, click the "Take Blank and Sample Measurement" button.
* A window will appear; when the button is clicked, the machine will measure the blank.
* Another window will appear.  Place the sample in the spectrophotometer, and close the lid.  When the button is presses, the machine
will measure the sample.
* A graph of the results will appear.  It is possible to save the graph, and to save a csv file of the data.  Click the button to do this.
##Troubleshooting
* When the spectrophotometer is used for the first time, the spectrum may not show up.  If this happens, it is necessary to adjust the device until
the issue is fixed.  Running `python3 show_video.py` will open a window with a video feed from the camera.  The window only lasts 2 minutes; if more
time is needed then re-run the code.
* The diffraction grating must be oriented vertically.  This is counter-intuitive; the printed part makes it look like it should be horizontal.
* The error `AttributeError: Unknown property labels` means that the version of matplotlib is too old.  Fix the problem by running `sudo apt-get install python3-pil python3-pil.imagetk`.
* If the same sample produces substantially different results in different runs, then the spectrophotometer may not be build rigidly enough.  The LED, slit, grating, and camera must not move relative to each other.
