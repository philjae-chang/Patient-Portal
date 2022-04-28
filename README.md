# Patient Portal & Monitoring GUI
 
## Authors: Philjae Chang and Diana Koo
 
## Purpose
The purpose of this project is to build a Patient Monitoring System which can upload and store patient data in a server, as well as retrieve the stored data for continuous monitoring of the patients. The system consists of 1)  the patient portal, which allows the user to upload their patient information to the server, 2) the patient monitor, which allows the user to access the latest patient information, and 3) the server/database. The patient portal and patient monitor are two different graphic user interfaces (GUIs). 
 
## How to run
1. Download ZIP from this repository. 
2. Open the zip folder and locate the folder in your terminal.
3. Run `pip install -r requirements.txt`
4. In order to open the patient portal, run `python patient_gui.py`. In order to open the patient monitor, run `python monitoring_gui`.
5. To learn about how to use these programs, watch the video below. 
(Here’s the link: https://duke.box.com/s/51b7pu082p5oz9tko4tgr3vqq56b9ikp)
 
## Specifications
 
### Patient Portal
- The user can enter a patient name and a patient medical record number. Patient medical record number is the unique identifier of a patient object stored in the database. Any relevant patient information except for medical record number can be updated after the initial upload.
- The user can select and display a medical image from the local computer.
- The user can also select an ECG data file in csv. The GUI will analyze the data and show the ECG plot and heart rate in beats per minute. 
- The user can upload the patient information entered above. Not all items need to be selected or added. When additional information is entered after an upload, the sequential upload will  upload only the updated information. 
-  The user can clear the information by clicking “Clear All”, and one can also exit the window by clicking “Exit Program”. 
 
### Patient Monitor
- The user can select a patient's medical record number from a list. 
- For the selected patient, the user can request information to display the selected patient’s medical record number, name,  the latest measured heart rate, ECG image, and the timestamp of ECG measurement. 
- The user can select from historical ECG images and medical images and display them. 
- All information in the GUI will refresh itself every 30 seconds. If additional information is entered from the patient portal, it will show on the monitor within 30 seconds. Also, the list of patient medical record numbers will alway be up-to-date. 
 
## Server APIs

 
`“/get_all_patient_id” route [GET]`


This route retrieves all the medical record numbers (or ids) of patients in the database.
 
`“/get_patient_info/<patient_id>” route [GET]`


This route retrieves patient information associated with the specified medical record number (patient id).
 
`“/new_patient” route [POST]`


This route allows you to add a new patient to the server/database. The associated POST data should look like this in JSON (although the minimum required information for uploading a new patient is the “Rec_No”:
 
{<br>
“Name”: “Diana Koo”,<br>
“Rec_No”: “2222”,<br>
“ECG”: ["b64-string", "b64-string"],<br>
“Heart_Rate”: [122, 98],<br>
“Med_Img”: ["b64-string"],<br>
}
 
## Virtual machine
 
The server is currently running on
`http://vcm-25859.vm.duke.edu:5000`
 
## Software license
MIT License
Copyright (c) [2022] [Diana Koo, Philjae Chang]
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 
 
 
 

