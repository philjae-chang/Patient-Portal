from tkinter import filedialog
import base64
import requests

server = "http://vcm-25859.vm.duke.edu:5000"


def retrieve_all_patients():
    r = requests.get(server + "/get_all_patient_id")
    return r.text


def retrieve_patient_data_from_server(patient_id):
    r = requests.get(server + "/get_patient_info/" + patient_id)
    return r.text


def convert_file_to_b64_string(filename):
    with open(filename, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string


def convert_b64_string_to_file(b64_string, savename):
    image_bytes = base64.b64decode(b64_string)
    with open(savename, "wb") as out_file:
        out_file.write(image_bytes)
    return


def upload_patient_data_to_server(patient_info):
    r = requests.post(server + "/new_patient", json=patient_info)
    return r.text
