# SKU Image Namer
A utility to manage image and file renaming by identifier 

---
#### Problem Statement 
When photographing many hundreds of subjects, a common problem is naming the files according to their identifier, or SKU. 
Renaming after the fact is labor intensive, requires intimate subject knowledge, and is error prone.

Take for example taking school portraits where each student has an ID that will later be mapped to a special parent login where they can order images.
If you miss your chance to name the files, you are left with no way to map images to a student without the help of the school, where there's not usually one person who knows all the students!

#### Other Solutions 
One option is using a tethering program and updating information in the software before each subject. 
The need to be tied to software with a comparable camera, the problems that often come with this, and the time it takes from photography makes this not ideally suited for many environments.
 
Other automated solutions involve photographing a special pre-printed QR code, and renaming files later with the help of 3rd party paid software. 

#### This Projects Solution 
This project seeks to solve all of these problems by implementing a solution where documenting what subject you are working with is 
completely untethered and unobtrusive to the photography workflow. The image renaming is done as a second automated step.

This is accomplished by following this simple workflow:
 1. Before working with each subject, scan or enter an ID using a barcode scanner or your keyboard. This will create a log file with the id and timestamp for each subject.
 2. Photograph your subject using any device.
 3. Load the files to be renamed onto your computer.
 4. Use the log file created by step 1 to rename all images automatically. This is done by identifying the timestamp in the photo and matching it to the logfile.

The advantages of this method is both the speed you can work at, and the 100% unobtrusive nature of the method, leaving the photography workflow alone.

---
### Usage Instructions 
##### Requirements:
- Python 3.6 or later
##### Setup
- Download or clone this repo.
- Add the required packages with `pip install -r requirements.txt`
- Run `python3 sku_namer.py --help` for the help file.

---
Future improvement ideas:
- Allow an optional tethered solution for renaming on the fly.
- Allow input using logs from as outside source, allowing more flexibility for entering subject info.
- Allow the input of a time offset to handle time differences between the logging device and camera.
- Include tooling to calculate the offset needed.
- Add reporting functionality for data on how long products took to photograph (can be helpful for billing).
- Add additional functionality to track deeper levels of information such as picture angles.