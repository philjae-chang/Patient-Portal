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


def init_server():
    """ Initializes server conditions

    This function configures the logging functionality and establishes
    a connection to the specified MongoDB database.
    """
    logging.basicConfig(filename="cloud_server.log", level=logging.DEBUG,
                        filemode='w')
    print("Connecting to database...")
    connect("mongodb+srv://bme547classwork:eX8y9F9QFtinXDNU"
            "@bme547.nkzjd.mongodb.net/myFirstDatabase?"
            "retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
    print("Connection attempt finished")


@app.route("/get_all_patient_id", methods=["GET"])
def get_all_patient_id():
    """ Handles requests to the /get_all_patient_id route for retrieving
    all the medical record numbers (ids) of patients in the database

    This function calls another function to implement the functionality
    and receives a dictionary with key "ids" storing a value which is
    a list of all the patient record numbers, as well as a status code
    from that function, which it then returns.

    Returns:
        dict/str, str: An error message if no patients were found in the
        database or a dictionary containing a list of patient ids, plus
        a status code.
    """
    patient_id_dict, status_code = get_all_patient_id_driver()
    return patient_id_dict, 200


def get_all_patient_id_driver():
    """ Implements the /get_all_patient_id route to obtain all patient
    medical record numbers

    This function implements the /get_all_patient_id route. The function
    retrieves all patients from the database. If patients are found,
    then the function makes a list of all the patient ids, and stores
    this list in a dictionary which can be accessed as a value. The
    dictionary and status are returned. If no patients are found, the
    function returns an error message with the status.

    Returns:
        dict or str, str: An error message if no patients were found in the
        database or a dictionary containing a list of patient ids, plus
        a status code.
    """
    try:
        patients = Patient.objects.raw({})
    except pymodm_errors.DoesNotExist:
        return "No patients were found", 400
    patient_id_list = []
    for patient in patients:
        patient_id_list.append(patient.patient_id)
    patient_id_dict = {"ids": patient_id_list}
    return patient_id_dict, 200


@app.route("/new_patient", methods=["POST"])
def new_patient_handler():
    """ Handles requests to the /new_patient route for adding or updating
    a patient in the database

    The /new_patient route is a POST request that should receive, at minimum,
    a JSON-encoded string with the following format:
    {"Record_No": str}

    Other "keys" and "values" that may be included are "Name" (name of
    patient), "Med_Img" (image filename encoded in b64), "ECG" (image
    filename encoded in 64), and "Heart_Rate" (heart rate measurement).

    The function then calls a driver function that implements the
    functionality of this route and receives an "answer", "time", and
    "status_code" from this driver function. Finally, it returns the
    "answer" using jsonify and the status_code.

    Returns:
        str, int: Message including time at which patient was successfully
                  added or updated in the database with the status code. If
                  unsuccessful, an error message followed by a status code
    """
    in_data = request.get_json()
    answer, time, status_code = new_patient_driver(in_data)
    message = "Entered information uploaded to server @ " + time
    return jsonify(message), status_code


def new_patient_driver(in_data):
    """ Implements /new_patient route for adding a new patient to the
    database

    The flask handler function for the /new_patient route calls this function
    to implement the functionality.  It receives as a parameter a dictionary
    that should contain the needed information in the following format:
    {"Rec_No": str}

    The function first calls a validation function to ensure that the needed
    key/value (patient medical record number) exists in the dictionary, then
    calls a function to add the patient data to the database. The function
    then returns to the caller the patient (as a MongoDB Patient object), time
    at which the patient was added or updated, and a status code of 200. If
    there was a validation problem, the function returns an error message with
    a status code of 400.

    Args:
        in_data (any type): the input data received by the route. Ideally,
        it is a dictionary.

    Returns:
        Patient, (str), int: If successfully added to the database, the Patient
                           object, time at which the patient was added/updated,
                           and status code. If not, an error message followed
                           by a status code.
    """
    answer, status_code = validate_server_input(in_data)
    answer, time, status_code = update_patient_info_driver(in_data, answer)
    return answer, time, status_code


def validate_server_input(in_data):
    """ Validates that input data to server contains a dictionary with at least
    a patient medical record number

    Various routes for this server are POST requests that receive JSON-encoded
    strings which should contain dictionaries. To avoid server errors, this
    function checks that the input data is a dictionary that contains, at
    minimum, a patient id.

    Args:
        in_data (any type): the input data that has been deserialized from a
            JSON string.  Ideally, it is a dictionary.

    Returns:
        str or bool, int: returns True, 200 if data validation is successful.
            Returns an error message string and 400 if data validation is
            unsuccessful.
    """
    if "Rec_No" not in in_data:
        error_message = "Patient Record Number is missing"
        return error_message, 400
    return True, 200


def update_patient_info_driver(in_data, validated):
    """ Adds a new patient or updates an existing patient in the database

    This function calls another function that checks whether the patient id
    exists in the database. If the patient id exists, the function returns
    "True", this function retrieves the Patient object with the specified id
    and calls another function to update the patient information. If the
    patient id does not exist, the called function returns "False", a new
    Patient object is initialized then updated with the provided information.
    The function then returns the saved patient, the time at which the
    patient was added or updated, and a status code of 200. If there was a
    validation problem, the function returns the boolean False, followed by
    the time and status code 400.

    Args:
        in_data: the input data received by the route. Ideally,
        it is a dictionary.

    Returns:
        Patient or str, str, int: if successfully added to the database,
                                  the Patient object and if not, an error
                                  message, followed by the time at which the
                                  patient was added/updated and status code
        """
    if validated is True:
        if patient_exist(in_data):
            old_patient = Patient.objects.raw(
                {"_id": int(in_data["Rec_No"])}).first()
            answer, time, status_code = \
                update_patient_info(in_data, old_patient)
            return answer, time, status_code
        else:
            new_patient = Patient(patient_id=in_data["Rec_No"])
            answer, time, status_code = \
                update_patient_info(in_data, new_patient)
            return answer, time, status_code
    time = ''
    return validated, time, 400


def patient_exist(in_data):
    """ Checks if patient id exists in database

    This function searches the database for a Patient object which matches
    the specified patient id.

    Args:
        in_data: the input data received by the route. Ideally,
        it is a dictionary.

    Returns:
        bool: True if patient id exists in database, False if not
    """
    try:
        db_item = Patient.objects.raw({"_id": int(in_data["Rec_No"])}).first()
    except pymodm_errors.DoesNotExist:
        return False
    return True


def update_patient_info(in_data, patient):
    """ Updates the patient with the specified patient id

    This function updates and saves the Patient object with the new
    information. If a new name is provided, the name is changed. If a new
    medical image, ECG image, or heart rate is provided, it is added to the
    patient record (list). When updating the ECG record with a new image,
    a timestamp with the current time is added to the patient's timestamp
    record.

    Args:
        in_data: the input data received by the route. Ideally,
        it is a dictionary.
        patient: the existing patient (Patient object) with the specified
        patient id

    Returns:
        Patient, str, int: the Patient object, followed by the time at which
        the patient was updated and status code 200
    """
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
    return saved_patient, now, 200


@app.route("/get_patient_info/<patient_id>", methods=["GET"])
def get_patient_info_handler(patient_id):
    """ Handles requests to the /get_patient_info route for
    retrieving patient information

    This function implements a GET route with a variable URL. The
    desired patient id number is included as part of the URL. The
    function calls another function to implement the functionality
    and receives a dictionary and status code from that function,
    which it then returns.

    Args:
        patient_id (str): the patient id taken from the variable URL

    Returns:
        dict/str, int: a dictionary containing patient information or
                       an error message, plus a status code
    """
    dict, status_code = get_patient_info_driver(patient_id)
    return dict, status_code


def get_patient_info_driver(patient_id):
    """ Implements the /get_patient_info route to obtain all patient
    information

    This function implements the /get_patient_info route. The function
    first calls a validation function to ensure that the specified patient
    id is a number, then calls another function to retrieve the patient
    (as a MongoDB Patient object) from the database. Then, another function
    is called to extract information from the Patient object and store it
    in a dictionary format.

    The function then returns to the caller the dictionary containing the
    patient information and a status code of 200. If there was a validation
    problem, the function returns an error message with a status code of 400.

    Args:
        patient_id (str): the patient id taken from the variable URL

    Returns:
        dict or str, str: An error message if there was a validation problem
        or a dictionary containing patient information, plus a status code.
    """
    answer, status_code = validate_convert_patient_id(patient_id)
    if status_code != 200:
        return answer, status_code
    patient, status_code = get_patient_info_from_database(answer)
    dict = make_patient_into_dict(patient)
    return dict, status_code


def validate_convert_patient_id(patient_id):
    """ Validates that the input patient id is a number

    To avoid server errors, this function checks that the specified patient id
    is a number.

    Args:
        patient_id (str): the patient id taken from the variable URL

    Returns:
        int or str: returns patient id with a status code of 200 if data
                    validation is successful. Returns an error message string
                    and 400 if data validation is unsuccessful.
    """
    try:
        patient_id_int = int(patient_id)
    except ValueError:
        return "Patient_id was not an integer", 400
    return patient_id_int, 200


def get_patient_info_from_database(patient_id):
    """ Searches for and retrieves Patient object associated with the
    specified patient id

    The function retrieves the patient with the specified id. If patient
    is found, then the function returns the Patient object with a status
    code of 200. If the patient id is not found, the function returns an
    error message with a status code of 400.

    Args:
        patient_id (str): the patient id taken from the variable URL

    Returns:
        Patient or str, int: returns Patient object with a status code of
                             200 if patient id is found in the database.
                             Returns an error message string and 400 if
                             patient id is not found.
    """
    try:
        patient = Patient.objects.raw({"_id": patient_id}).first()
    except pymodm_errors.DoesNotExist:
        return "Patient_id {} was not found".format(patient_id), 400
    return patient, 200


def make_patient_into_dict(patient):
    """ Extracts and stores information from Patient object in a
    dictionary

    The function retrieves the patient (as a Patient object) with the
    specified id, extracts the information associated with the object,
    and stores this data in a dictionary format.

    Args:
        patient (Patient object): the patient corresponding to
                                  patient id taken from the variable URL

    Returns:
        dict: returns dictionary containing patient information
    """
    patient_dict = {"Name": patient.patient_name,
                    "Rec_No": patient.patient_id,
                    "Med_Img": patient.medical_images,
                    "ECG": patient.ecg_images,
                    "Heart_Rate": patient.heartrate,
                    "Timestamp": patient.timestamp}
    return patient_dict


if __name__ == "__main__":
    init_server()
    app.run(host="0.0.0.0")
