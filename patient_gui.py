# patient side GUI
from distutils.log import error
from ftplib import error_temp
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from PIL import Image, ImageTk
from ecg import calc_hr
import pandas as pd
import matplotlib.pyplot as plt
from gui_client import *

bpm = 'N/A'
ecg_filename = 'N/A'
med_filename = 'N/A'
ecg_is_uploaded = True
med_img_is_uploaded = True


# need test
def create_info_dict(entered_name, entered_id, ecg_is_uploaded,
                     med_img_is_uploaded, med_filename):
    """Creates patient information dictionary from the input data

    create_info_dict accepts patient name, id, ecg string, medical
    image string, and creates a python dictionary that contains
    the input patient information

    Args:
        entered_name (str): patient name
        entered_id (int): patient id
        ecg_is_uploaded (bool): whether ecg img is uploaded
        med_img_is_uploaded (bool): whether med img is uploaded
        med_filename (str): filename of medical image

    Returns:
        dict: patient information
    """
    global bpm
    global ecg_filename
    # initialize a dictionary that will be sent to server
    patient_info = {"Rec_No": entered_id}

    # add patient info to dictionary only when it is updated
    if entered_name != "":
        patient_info.update({"Name": entered_name})
    if ecg_is_uploaded is False:
        selected_ECG_image = convert_file_to_b64_string('ecg.jpg')
        patient_info.update({"ECG": selected_ECG_image})
        patient_info.update({"Heart_Rate": bpm})
        ecg_is_uploaded = True
    if med_img_is_uploaded is False:
        selected_medical_image = convert_file_to_b64_string(med_filename)
        patient_info.update({"Med_Img": selected_medical_image})
        med_img_is_uploaded = True
    return patient_info


def verify_GUI_input(entered_id):
    '''verifies whehter the input is an integer string

    verifiy_GUI_input checks whehter the entered patient ID is
    an integer in string format. It also returns an error message
    if the input string is empty.

    Args:
        entered_id (int): patient ID entered in GUI

    Returns:
        bool: whether the ID is a number in acceptable format
        int: status code

    '''
    if entered_id == "":
        error_message = "There is no patient ID entered"
        return error_message, 400
    if entered_id.isdigit() is False:
        error_message = "Entered medical record number is not a number"
        return error_message, 400
    return True, 200


def main_window():

    """Creates and runs a GUI for the patient portal

    This function creates a window that allows a user to enter patient
    information for eventual upload to a patient database server.
    Patient info includes patient name, patient id number, ECG, heart
    rate, and medical image.
    """

    def cancel_cmd():
        """ Closes GUI window upon click of "Exit" button

        When the user clicks on the "Exit" button, this function is run
        which closes the main root GUI window.
        """
        root.destroy()

    def clear_cmd():
        ''' Clears the entered patient information in main window

        When clear_cmd is called by a user clicking "Clear All"
        button, it clears the entered patient information in main
        window into default values.
        '''

        global bpm
        global med_filename
        global ecg_is_uploaded
        global med_img_is_uploaded
        global ecg_filename
        name_input.delete(0, 'end')
        id_input.delete(0, 'end')
        hr_label.configure(text="Patient heart rate (bpm): ")
        ecg_filename = 'N/A'
        med_filename = 'N/A'
        bpm = 'N/A'
        ecg_is_uploaded = True
        med_img_is_uploaded = True
        ecg_label.configure(image=blank_image)
        medical_label.configure(image=blank_image)
        status_label.configure(text="Enter Patient Info")
        return

    def upload_cmd():
        """ Obtains data from window and uploads to server

        This function runs when the user clicks on the "Upload" button.
        It gets the entered data from the interface and uploads it
        to the server.
        """
        global ecg_is_uploaded
        global med_img_is_uploaded
        global med_filename
        # verify GUI input
        entered_id = id_entry.get()
        answer, status_code = verify_GUI_input(entered_id)
        status_label.configure(text=answer)
        if answer is not True:
            return answer

        # Get Data from Interface
        entered_name = name_entry.get()
        entered_id = id_entry.get()

        # create a patient data dictionary
        patient_info = create_info_dict(entered_name, entered_id,
                                        ecg_is_uploaded, med_img_is_uploaded,
                                        med_filename)

        # upload patient data to server and updatae status label
        message = upload_patient_data_to_server(patient_info)
        status_label.configure(text=message)

    def image_cmd():
        """ displays the selected medical image

        image_cmd reads the medical file selected by the user,
        resizes it to fit the display window, and displays it in GUI.
        """
        global med_filename
        global med_img_is_uploaded
        med_filename = filedialog.askopenfilename()
        if med_filename == "":
            return
        pil_image_raw = Image.open(med_filename)
        pil_image = pil_image_raw.resize((200, 150))
        new_image = ImageTk.PhotoImage(pil_image)
        medical_label.configure(image=new_image)
        medical_label.x123 = new_image
        med_img_is_uploaded = False
        return

    def ECG_cmd():
        """ displays the selected ecg image

        image_cmd reads the ecg file selected by the user, analyzes it,
        and make it into a plot. Then it resizes the plot to fit the display
        window, and displays it in GUI. It also displays the calculated bpm
        in GUI.

        returns:
            int: beats per minute
        """
        global bpm
        global ecg_is_uploaded
        global ecg_filename
        ecg_filename = filedialog.askopenfilename()
        time, voltage = read_ECG(ecg_filename)
        plot_ECG(time, voltage)
        bpm = calc_hr(time, voltage)
        replace_ECG()
        # Display Heart Rate
        hr_label.configure(text="Patient heart rate (bpm): {}".format(bpm))
        hr_label.grid(column=3, row=19)
        ecg_is_uploaded = False
        return bpm

    def read_ECG(filename):
        """ reads the input ecg file in csv format

        read_ECG is called when ECG_cmd is running. It reads the csv file
        selected by the user and returns time and volate in list format.

        args:
            filename (str): the user selected filename

        returns:
            list: the time array
            list: the voltage array
        """
        data = pd.read_csv(filename, header=None, names=['time', 'voltage'])
        time = list(data['time'])
        voltage = list(data['voltage'])
        return time, voltage

    def plot_ECG(time, voltage):
        ''' plots the ECG data

        plot_ECG receives time and voltage arrays and plot them
        using matplotlib.pyplot functions. Then it saves the plot
        with the name "ecg.jpg".

        args:
            time (list): time array
            voltage (list): voltage array
        '''
        plt.clf()
        plt.plot(time, voltage)
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (mV)')
        plt.savefig('ecg.jpg')

    def replace_ECG():
        ''' replaces the ecg image in GUI with the selected image

        replace_ECG is called when the user wants to replace the ecg
        image shown in GUI already. It searches for the filename "ecg.jpg"
        then resizes it, and displays it in GUI.
        '''
        filename = 'ecg.jpg'
        pil_image_raw = Image.open(filename)
        pil_image = pil_image_raw.resize((200, 150))
        new_image = ImageTk.PhotoImage(pil_image)
        ecg_label.configure(image=new_image)
        ecg_label.x123 = new_image

    # initialize window
    root = tk.Tk()
    root.title("Patient Portal")
    root.geometry("900x350")

    # Patient Name Entry
    ttk.Label(root, text="Name:").grid(column=0, row=1, sticky=tk.E)
    name_entry = tk.StringVar()
    name_input = ttk.Entry(root, width=20, textvariable=name_entry)
    name_input.grid(column=1, row=1, sticky=tk.W)

    # Patient Medical Record Number Entry
    mrn_label = ttk.Label(root, text="Medical Record Number:")
    mrn_label.grid(column=0, row=2, sticky=tk.E)
    id_entry = tk.StringVar()
    id_input = ttk.Entry(root, width=20, textvariable=id_entry)
    id_input.grid(column=1, row=2, sticky=tk.W)

    # Status label
    status_label = ttk.Label(root, text="Enter Patient Info")
    status_label.grid(column=0, row=3, columnspan=4)

    # Heartrate label
    hr_label = ttk.Label(root, text="Patient heart rate (bpm): ")

    # medical image initialize
    pil_image_raw = Image.open("blank.jpg")
    pil_image = pil_image_raw.resize((200, 150))
    blank_image = ImageTk.PhotoImage(pil_image)
    medical_label = ttk.Label(root, image=blank_image)
    medical_label.grid(column=4, row=0, rowspan=10)

    # Ecg image initialize
    ecg_label = ttk.Label(root, image=blank_image)
    ecg_label.grid(column=4, row=10, rowspan=10)

    # Buttons
    ttk.Button(root, text="Select medical image...", command=image_cmd).grid(
        column=3, row=1)
    ttk.Button(root, text="Select ECG file to analyze...",
               command=ECG_cmd).grid(column=3, row=10)
    ttk.Button(root, text="Upload", command=upload_cmd).grid(column=1, row=20)
    ttk.Button(root, text="Clear All",
               command=clear_cmd).grid(column=4, row=20)
    ttk.Button(root, text="Exit Program", command=cancel_cmd).grid(
        column=3, row=20)

    root.mainloop()


if __name__ == "__main__":
    main_window()
