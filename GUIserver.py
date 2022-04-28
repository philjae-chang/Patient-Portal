    # GUIserver.py

import logging
from flask import Flask, request, jsonify
from pymodm import connect
from pymodm import errors as pymodm_errors
from pymodm import MongoModel, fields
from datetime import datetime
from tkinter import filedialog
import base64
import requests
import ssl




class Patient(MongoModel):
    patient_name = fields.CharField()
    patient_id = fields.IntegerField(primary_key=True)
    ecg_images = fields.ListField()
    medical_images = fields.ListField()
    timestamp = fields.ListField()
    heartrate = fields.ListField()


app = Flask(__name__)

#check
def init_server():
    """ Initializes server conditions
    This function can be used for any specific tasks that you would like to run
    upon initial server start-up.  Currently, it configures the logging
    functionality and it makes a connection to a MongoDB database.
    Note:  As currently written, this function does not need a unit test as
    it does not do any data manipulation itself.
    """
    logging.basicConfig(filename="GUIserver.log", level=logging.DEBUG,
                        filemode='w')
    print("Connecting to database...")
    connect("mongodb+srv://bme547classwork:eX8y9F9QFtinXDNU"
            "@bme547.nkzjd.mongodb.net/myFirstDatabase?"
            "retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
    print("Connection attempt finished")

#check
@app.route("/get_all_patient_id", methods=["GET"])
def get_all_patient_id():
    patient_id_dict, status_code = get_all_patient_id_driver()
    return patient_id_dict, 200
#check
def get_all_patient_id_driver():
    try:
        patients = Patient.objects.raw({})
    except pymodm_errors.DoesNotExist:
        return "No patients were found", 400
    patient_id_list = []
    for patient in patients:
        patient_id_list.append(patient.patient_id)
    patient_id_dict = {"ids": patient_id_list}
    return patient_id_dict, 200

@app.route("/get_patient_info/<patient_id>", methods=["GET"])
def get_patient_info_handler(patient_id):
    print('hi')
    dict, status_code = get_patient_info_driver(patient_id)
    print(type(dict))
    return dict, status_code


def get_patient_info_driver(patient_id):
    answer, status_code = validate_convert_patient_id(patient_id)
    if status_code != 200:
        return answer, status_code
    patient, status_code = get_patient_info_from_database(answer)
    print("reached driver")
    dict = make_patient_into_dict(patient)
    return dict, status_code


def validate_convert_patient_id(patient_id):
    try:
        patient_id_int = int(patient_id)
    except ValueError:
        return "Patient_id was not an integer", 400
    print("validated")
    return patient_id_int, 200


def get_patient_info_from_database(patient_id):
    try:
        patient = Patient.objects.raw({"_id": patient_id}).first()
    except pymodm_errors.DoesNotExist:
        return "Patient_id {} was not found".format(patient_id), 400
    print(type(patient))
    print(patient)
    return patient, 200

def make_patient_into_dict(patient):
    patient_dict = {"Name": patient.patient_name,
                    "Rec_No": patient.patient_id,
                    "Med_Img": patient.medical_images,
                    "ECG": patient.ecg_images,
                    "Heart_Rate": patient.heartrate,
                    "Timestamp": patient.timestamp}
    return patient_dict
    


# dictionary format: {"Name": "Phil", "Rec_No": "12345",
#                     "Med_Img":"Some String", "ECG":"Some String",
#                     "Heart_Rate": "123"}

#check
@app.route("/new_patient", methods=["POST"])
def new_patient_handler():
    # Get the data from the request
    in_data = request.get_json()
    # Call OTHER function to do the request
    answer, status_code = new_patient_driver(in_data)
    # Provide a response
    return jsonify(answer), status_code

#check
def new_patient_driver(in_data):
    answer, status_code = validate_server_input(in_data)
    answer, status_code = update_patient_info_driver(in_data, answer)
    return answer, status_code

#check
def update_patient_info_driver(in_data, validated):
    if validated == True:
        if patient_exist(in_data):
            old_patient = Patient.objects.raw({"_id": int(in_data["Rec_No"])}).first()
            answer, status_code = update_patient_info(in_data, old_patient)
            return answer, status_code
        else:
            new_patient = Patient(patient_id=in_data["Rec_No"])
            answer, status_code = update_patient_info(in_data, new_patient)
            return answer, status_code
    return validated, 400

#check
def patient_exist(in_data):
    try:
        db_item = Patient.objects.raw({"_id": int(in_data["Rec_No"])}).first()
    except pymodm_errors.DoesNotExist:
        return False
    return True
#check
def validate_server_input(in_data):
    if "Rec_No" not in in_data:
        error_message = "Patient Record Number is missing"
        return error_message, 400
    return True, 200
#check
def update_patient_info(in_data, patient):
    now = datetime.now()
    now = now.strftime("%m/%d/%Y, %H:%M:%S")
    for key in in_data:
        if key == "Name":
            patient.patient_name = in_data["Name"]
        elif key == "Med_Img":
            patient.medical_images.append(in_data["Med_Img"])
        elif key == "ECG":
            patient.ecg_images.append(in_data["ECG"])
            patient.timestamp.append(now)
        elif key == "Heart_Rate":
            patient.heartrate.append(in_data["Heart_Rate"])
    saved_patient = patient.save()
    message = "Entered Information uploaded to server @ "+now
    return message, 200


if __name__ == '__main__':
    init_server()
    app.run()
