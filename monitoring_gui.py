import tkinter as tk
from tkinter import ttk, filedialog
import base64
import requests
import json
from PIL import Image, ImageTk
from gui_client import *

info_requested = False


def get_selected_med_64(med_of_interest_timestamp, patient):
    """ Gets the medical associated with the selected timestamp

    This function finds the medical image associated with the
    selected timestamp from the medical image data dropdown menu.
    The index of the timestamp in the list of medical image
    timestamps is used to retrieve the corresponding medical
    image from the medical image record.

    Args:
        med_of_interest_timestamp: selected timestamp from dropdown
        patient: dictionary containing patient information

    Returns:
        str: medical image file encoded in b64-format
    """
    time_idx = patient["Timestamp"].index(med_of_interest_timestamp)
    selected_med_file_64 = patient["Med_Img"][time_idx]
    return selected_med_file_64


def get_selected_ecg_64(ecg_of_interest_timestamp, patient):
    """ Gets the medical associated with the selected timestamp

    This function finds the ECG image associated with the
    selected timestamp from the ECG data dropdown menu. The
    index of the timestamp in the list of ECG image timestamps
    is used to retrieve the corresponding ECG image from the
    ECG data record.

    Args:
        ecg_of_interest_timestamp: selected timestamp from dropdown
        patient: dictionary containing patient information

    Returns:
        str: ECG image file encoded in b64-format
    """
    time_idx = patient["Timestamp"].index(ecg_of_interest_timestamp)
    selected_ecg_file_64 = patient["ECG"][time_idx]
    return selected_ecg_file_64


def main_window():
    """Creates and runs a GUI for the monitoring station GUI client

    This function creates a window that allows a user to view
    information about a patient in the database server. When a patient
    id is selected, the user can retrieve the patient name and data on
    the patient's ECG/heart rate measurements, medical images, and the
    date/time at which each record was uploaded.
    """
    patient = {}
    selected_med_file_64 = ''
    selected_ecg_file_64 = ''

    def cancel_cmd():
        """ Closes GUI upon click of "Cancel" button

        When the user clicks on the "Cancel" button, this function is run
        which closes the main root GUI window.
        """
        root.destroy()

    def clear_cmd():
        """ Clears displayed patient information

        When the user clicks on the "CLear All" button, this function is
        run which clears any patient information currently displayed.
        """
        ecg_latest_label.configure(image=blank_image)
        med_img_label.configure(image=blank_image)
        ecg_selected_label.configure(image=blank_image)
        mrn_label.configure(text="Patient medical record number:")
        name_label.configure(text="Patient name:")
        hr_label.configure(text="Latest heart rate:")
        timestamp_label.configure(text="Timestamp of latest heart "
                                       "rate measurement:")
        return

    def manual_clear_cmd():
        ecg_latest_label.configure(image=blank_image)
        med_img_label.configure(image=blank_image)
        ecg_selected_label.configure(image=blank_image)
        mrn_label.configure(text="Patient medical record number:")
        name_label.configure(text="Patient name:")
        hr_label.configure(text="Latest heart rate:")
        timestamp_label.configure(text="Timestamp of latest heart "
                                       "rate measurement:")
        patient_dropdown.set('')
        med_dropdown.set('')
        ecg_dropdown.set('')
        return

    def patient_record_driver():
        """ Obtains the ids of all patients in the server database

        This function calls other functions to retrieve all patient ids
        in the server. A list of patient ids is returned, which is
        accessible as options in a dropdown menu for selecting the
        patient of interest in the GUI.

        Returns:
            list: a list of ids of all patients in the server database
        """
        all_patients = retrieve_all_patients_driver()
        all_patients_IDs = get_all_patient_IDs(all_patients)
        return all_patients_IDs

    def retrieve_all_patients_driver():
        """ Obtains the ids of all patients in the server database

        This function calls a GET request to retrieve all patient ids
        in the server.

        Returns:
            dict: a dictionary containing a key "ids" and a list of
                  patient ids as the corresponding value
        """
        all_patients = json.loads(retrieve_all_patients())
        return all_patients

    def get_all_patient_IDs(all_patients):
        """ Extracts patient ids from a dictionary

        This function extracts the list of patient ids from the...

        Args:
            all_patients: a dictionary with key "ids" and a list of
                          patient ids as the corresponding value

        Returns:
            list: a list of all patient ids
        """
        all_patient_IDs = all_patients["ids"]
        return all_patient_IDs

    def request_info_cmd():
        """ Retrieves the latest information of patient with the
        selected patient id upon click of "Request info" button

        When the user clicks on the "Request info" button, this
        function is run which displays latest patient information.
        """
        global info_requested
        clear_cmd()
        info_requested = True
        refresh_fields()
        update_latest_med_img_driver()

    def refresher():
        """ Makes periodic requests every 30 seconds to the server
        to check for any updated information of the currently selected
        patient

        This function calls other functions to update the displayed
        patient information. If the "Request Info" button is clicked,
        the GUI displays the information of the selected patient. If
        the button is not clicked, the patient information currently
        displayed is automatically refreshed to provide the most
        up-to-date information.
        """
        global info_requested
        update_patient_record()
        if info_requested is True:
            refresh_fields()
        root.after(30000, refresher)

    def refresh_fields():
        """ Updates to show information for the selected patient

        This function calls other functions to retrieve information of
        the currently selected patient and update the medical record
        number, name, the latest heart rate, and timestamp corresponding
        to this heart rate. The latest ECG image and medical image are
        also displayed.

        Note: The information displayed depends on which types of
        information were uploaded for the patient (the minimum
        requirement for uploading a patient is the medical record number).
        """
        global patient
        current_patient_ID = selected_patientID.get()
        patient = json.loads(
            retrieve_patient_data_from_server(current_patient_ID))
        mrn_label.configure(text="Patient medical record number: {}"
                            .format(patient["Rec_No"]))
        if patient["Name"] != "":
            name_label.configure(text="Patient name: {}"
                                 .format(patient["Name"]))
        if len(patient["Heart_Rate"]) != 0:
            hr_label.configure(text="Latest heart rate: {}"
                               .format(patient["Heart_Rate"][-1]))
            timestamp_label.configure(text="Most recent measurement: {}"
                                      .format(patient["Timestamp"][-1]))
            ecg_dropdown["values"] = patient["Timestamp"]
            latest_ecg_64 = patient["ECG"][-1]
            update_latest_ecg_img(latest_ecg_64)
        if len(patient["Med_Img"]) != 0:
            drop_list = list(range(len(patient["Med_Img"])))
            drop_list = [i+1 for i in drop_list]
            med_dropdown["values"] = drop_list
        return

    def update_latest_med_img_driver():
        global patient
        if len(patient["Med_Img"]) != 0:
            latest_med_64 = patient["Med_Img"][-1]
            update_latest_med_img(latest_med_64)
        return

    def update_latest_med_img(med_64):
        """ Configures the latest medical image

        This function calls another function to decode a b64-string.
        The decoded image file is opened, resized, and assigned to
        the medical image label.

        Args:
            med_64: medical image file encoded in b64-format
        """
        if med_64 == "":
            return
        convert_b64_string_to_file(med_64, "patient_med.jpg")
        pil_image_raw = Image.open("patient_med.jpg")
        pil_image = pil_image_raw.resize((200, 150))
        new_image = ImageTk.PhotoImage(pil_image)
        med_img_label.configure(image=new_image)
        med_img_label.x123 = new_image
        return

    def load_med_cmd():
        """ Loads and displays the selected medical image

        When the user clicks on the "Load Medical Image" button, this
        function is run which loads the medical image corresponding
        to the selected timestamp.
        """
        global selected_med_file_64
        global patient
        med_idx = int(selected_med.get())-1
        selected_med_file_64 = patient["Med_Img"][med_idx]
        update_selected_med_img(selected_med_file_64)
        return

    def update_selected_med_img(med_filename):
        """ Configures the selected medical image

        This function calls another function to decode a b64-string.
        The decoded image file is opened, resized, and assigned to
        the medical image label.

        Args:
            med_filename: medical image file encoded in b64-format
        """
        if med_filename == "":
            return
        convert_b64_string_to_file(med_filename, "patient_med.jpg")
        pil_image_raw = Image.open("patient_med.jpg")
        pil_image = pil_image_raw.resize((200, 150))
        new_image = ImageTk.PhotoImage(pil_image)
        med_img_label.configure(image=new_image)
        med_img_label.x123 = new_image
        return

    def load_ecg_cmd():
        """ Loads and displays the selected ECG image

        When the user clicks on the "Load ECG Image" button, this
        function is run which loads the ECG image corresponding
        to the selected timestamp.
        """
        global patient
        global selected_ecg_file_64
        ecg_of_interest_timestamp = selected_ecg.get()
        selected_ecg_file_64 = get_selected_ecg_64(
            ecg_of_interest_timestamp, patient)
        update_selected_ecg_img(selected_ecg_file_64)
        return

    def update_selected_ecg_img(ecg_filename):
        """ Configures the selected ECG image

        This function calls another function to decode a b64-string.
        The decoded image file is opened, resized, and assigned to
        the medical image label.

        Args:
            ecg_filename: ECG image file encoded in b64-format
        """
        if ecg_filename == "":
            return
        convert_b64_string_to_file(ecg_filename, "patient_ecg.jpg")
        pil_image_raw = Image.open("patient_ecg.jpg")
        pil_image = pil_image_raw.resize((200, 150))
        new_image = ImageTk.PhotoImage(pil_image)
        ecg_selected_label.configure(image=new_image)
        ecg_selected_label.x123 = new_image
        return

    def update_latest_ecg_img(ecg_filename):
        """ Configures the latest medical image

        This function calls another function to decode a b64-string.
        The decoded image file is opened, resized, and assigned to
        the medical image label.

        Args:
            ecg_filename: ECG image file encoded in b64-format
        """
        if ecg_filename == "":
            return
        convert_b64_string_to_file(ecg_filename, "patient_ecg.jpg")
        pil_image_raw = Image.open("patient_ecg.jpg")
        pil_image = pil_image_raw.resize((200, 150))
        new_image = ImageTk.PhotoImage(pil_image)
        ecg_latest_label.configure(image=new_image)
        ecg_latest_label.x123 = new_image
        return

    def save_med_img_cmd():
        """ Downloads selected medical image to a file on local computer

        When the user clicks on the "Save Selected Medical Image" button,
        this function is run which downloads the selected medical image.
        """
        global selected_med_file_64
        filename = filedialog.asksaveasfilename()
        image_bytes = base64.b64decode(selected_med_file_64)
        with open(filename, "wb") as out_file:
            out_file.write(image_bytes)
        return

    def save_ecg_img_cmd():
        """ Downloads selected ECG image to a file on local computer

        When the user clicks on the "Save Selected ECG Image" button,
        this function is run which downloads the selected ECG image.
        """
        global selected_ecg_file_64
        filename = filedialog.asksaveasfilename()
        image_bytes = base64.b64decode(selected_ecg_file_64)
        with open(filename, "wb") as out_file:
            out_file.write(image_bytes)
        return

    def update_patient_record():
        """ Updates the ids of all patients in the server database

        This function calls another function to retrieve all patient ids
        in the server. This function is called when making requests to
        check for any updated information of the currently selected
        patient.
        """
        patient_dropdown["values"] = patient_record_driver()

    root = tk.Tk()
    root.title("Patient Monitor")
    root.geometry("1400x350")
    ttk.Label(root, text="").grid(
        column=0, row=0, columnspan=2, sticky='w')

    # Select patient record number
    ttk.Label(root, text="Select patient record number:").grid(
        column=0, row=1, sticky=tk.W)
    selected_patientID = tk.StringVar()
    patient_dropdown = ttk.Combobox(root, textvariable=selected_patientID)
    patient_dropdown.grid(column=1, row=1, sticky=tk.W)
    patient_dropdown["values"] = patient_record_driver()
    patient_dropdown.state(['readonly'])

    # Select ECG image from record
    ttk.Label(root, text="Select ECG data from patient record").grid(
        column=4, row=1, sticky=tk.W)
    selected_ecg = tk.StringVar()
    ecg_dropdown = ttk.Combobox(root, textvariable=selected_ecg)
    ecg_dropdown.grid(column=5, row=1, sticky=tk.W)
    ecg_dropdown.state(['readonly'])

    # Select medical image from record
    ttk.Label(root, text="Select Medical Image from patient record").grid(
        column=4, row=2, sticky=tk.W)
    selected_med = tk.StringVar()
    med_dropdown = ttk.Combobox(root, textvariable=selected_med)
    med_dropdown.grid(column=5, row=2, sticky=tk.W)
    med_dropdown.state(['readonly'])

    # Display patient information
    mrn_label = ttk.Label(root, text="Patient medical record number:")
    mrn_label.grid(column=0, row=2, sticky=tk.W)
    name_label = ttk.Label(root, text="Patient name:")
    name_label.grid(column=0, row=3, sticky=tk.W)
    hr_label = ttk.Label(root, text="Latest heart rate:")
    hr_label.grid(column=0, row=4, sticky=tk.W)
    timestamp_label = ttk.Label(root, text="Most recent measurement:")
    timestamp_label.grid(column=0, row=5, sticky=tk.W)

    # Initialize blank latest ecg image
    pil_image_raw = Image.open("blank.jpg")
    pil_image = pil_image_raw.resize((200, 150))
    blank_image = ImageTk.PhotoImage(pil_image)
    ecg_latest_label = ttk.Label(root, image=blank_image)
    ecg_latest_label.grid(column=4, row=10, rowspan=10)

    # Initialize blank selected ecg image
    ecg_selected_label = ttk.Label(root, image=blank_image)
    ecg_selected_label.grid(column=5, row=10, rowspan=10)

    # Initialize blank medical image
    med_img_label = ttk.Label(root, image=blank_image)
    med_img_label.grid(column=6, row=10, rowspan=10)

    # Buttons
    ttk.Button(root, text="Request info", command=request_info_cmd).grid(
        column=3, row=1)
    ttk.Button(root, text="Clear All", command=manual_clear_cmd)\
        .grid(column=2, row=20)
    ttk.Button(root, text="Exit Program", command=cancel_cmd).grid(
        column=1, row=20)
    ttk.Button(root, text="Load ECG image", command=load_ecg_cmd).grid(
        column=6, row=1)
    ttk.Button(root, text="Load Medical image", command=load_med_cmd).grid(
        column=6, row=2)
    ttk.Button(root, text="Save Selected Medical Image",
               command=save_med_img_cmd).grid(
        column=6, row=20)
    ttk.Button(root, text="Save Selected ECG Image",
               command=save_ecg_img_cmd).grid(column=5, row=20)

    root.after(30000, refresher)
    root.mainloop()


if __name__ == "__main__":
    main_window()
