import pytest
import logging
from pymodm import connect
from pymodm import errors as pymodm_errors
from pymodm import MongoModel, fields
from freezegun import freeze_time
import datetime
import ssl

connect("mongodb+srv://bme547classwork:eX8y9F9QFtinXDNU"
        "@bme547.nkzjd.mongodb.net/myTestDatabase?"
        "retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)


class Patient(MongoModel):
    patient_name = fields.CharField()
    patient_id = fields.IntegerField(primary_key=True)
    ecg_images = fields.ListField()
    medical_images = fields.ListField()
    timestamp = fields.ListField()
    heartrate = fields.ListField()


@pytest.mark.parametrize("in_data, expected", [
                            [[{"Name": "Phil", "Rec_No": "12345"},
                              {"Name": "Diana", "Rec_No": "54321"}],
                             [12345, 54321]]
                            ])
def test_get_all_patient_id_driver(in_data, expected):
    from cloud_server import get_all_patient_id_driver, new_patient_driver
    for patient in in_data:
        new_patient_driver(patient)
    (patients, status_code) = get_all_patient_id_driver()
    # print(patients)
    patient1 = Patient.objects.raw({"_id": 12345})
    patient1.delete()
    patient2 = Patient.objects.raw({"_id": 54321})
    patient2.delete()
    assert sorted(patients["ids"]) == expected


@pytest.mark.parametrize("in_data, expected", [
                            [{"Name": "Phil", "Rec_No": "12345",
                              "Med_Img": "Img3", "ECG": "Img4",
                              "Heart_Rate": "123"},
                             Patient(patient_name="Phil", patient_id="12345",
                                     ecg_images=["Img4"],
                                     medical_images=["Img3"],
                                     heartrate=["123"])]])
def test_new_patient_driver(in_data, expected):
    from cloud_server import new_patient_driver
    saved_patient, time, status_code = new_patient_driver(in_data)
    patient1 = Patient.objects.raw({"_id": 12345})
    patient1.delete()
    assert saved_patient.patient_name == expected.patient_name
    assert saved_patient.patient_id == expected.patient_id
    assert saved_patient.ecg_images[0] == expected.ecg_images[0]
    assert saved_patient.medical_images[0] == expected.medical_images[0]
    assert saved_patient.heartrate[0] == expected.heartrate[0]


def test_get_patient_info_driver():
    from cloud_server import get_patient_info_driver, new_patient_driver
    in_data = {"Name": "Phil",
               "Rec_No": "12345",
               "Med_Img": "Img3",
               "ECG": "Img4",
               "Heart_Rate": "123"}
    expected = {"Name": "Phil",
                "Rec_No": "12345",
                "Med_Img": "Img3",
                "ECG": "Img4",
                "Heart_Rate": "123",
                "Timestamp": "04/13/2022, 15:02:45"}
    initial_datetime = datetime.datetime(year=2022, month=4, day=13,
                                         hour=15, minute=2, second=45)
    freezer = freeze_time(initial_datetime)
    new_patient_driver(in_data)
    dict, status_code = get_patient_info_driver(12345)
    patient1 = Patient.objects.raw({"_id": 12345})
    patient1.delete()
    assert sorted(dict) == sorted(expected)


@pytest.mark.parametrize("patient_id, expected", [
    ["12345", 200],
    ["two", 400]
])
def test_validate_convert_patient_id(patient_id, expected):
    from cloud_server import validate_convert_patient_id
    answer, status_code = validate_convert_patient_id(patient_id)
    assert status_code == expected


# testing for cases when the patient exist in database
def test_get_patient_info_from_database_1():
    from cloud_server import get_patient_info_from_database, new_patient_driver
    in_data = {"Name": "Phil",
               "Rec_No": "12345",
               "Med_Img": "Img3",
               "ECG": "Img4",
               "Heart_Rate": "123"}
    expected = Patient(patient_name="Phil",
                       patient_id="12345",
                       ecg_images=["Img4"],
                       medical_images=["Img3"],
                       heartrate=["123"])
    new_patient_driver(in_data)
    saved_patient, status_code = get_patient_info_from_database(12345)
    patient1 = Patient.objects.raw({"_id": 12345})
    patient1.delete()
    assert saved_patient.patient_name == expected.patient_name
    assert saved_patient.patient_id == expected.patient_id
    assert saved_patient.ecg_images[0] == expected.ecg_images[0]
    assert saved_patient.medical_images[0] == expected.medical_images[0]
    assert saved_patient.heartrate[0] == expected.heartrate[0]


# testing for cases when the patient does not exist in database
def test_get_patient_info_from_database_2():
    from cloud_server import get_patient_info_from_database, new_patient_driver
    in_data = {"Name": "Phil",
               "Rec_No": "12345",
               "Med_Img": "Img3",
               "ECG": "Img4",
               "Heart_Rate": "123"}
    expected = 400
    new_patient_driver(in_data)
    saved_patient, status_code = get_patient_info_from_database(12346)
    patient1 = Patient.objects.raw({"_id": 12345})
    patient1.delete()
    assert status_code == expected


def test_make_patient_info_dict():
    from cloud_server import make_patient_into_dict
    patient = Patient(patient_name="Phil",
                      patient_id="12345",
                      ecg_images=["Img4"],
                      medical_images=["Img3"],
                      timestamp=["04/13/2022, 15:02:45"],
                      heartrate=["123"])
    expected = {"Name": "Phil",
                "Rec_No": "12345",
                "Med_Img": ["Img3"],
                "ECG": ["Img4"],
                "Heart_Rate": ["123"],
                "Timestamp": ["04/13/2022, 15:02:45"]}
    dict = make_patient_into_dict(patient)
    assert sorted(dict) == sorted(expected)


@pytest.mark.parametrize("in_data, validated, expected",
                         [({"Name": "Phil", "Rec_No": "12345",
                            "Med_Img": ["Img3"], "ECG": ["Img4"],
                            "Heart_Rate": ["123"]}, True, 200)])
def test_update_patient_info_driver(in_data, validated, expected):
    from cloud_server import update_patient_info_driver, new_patient_driver
    patient = {"Name": "Phil", "Rec_No": "12345",
               "Med_Img": ["Img1"], "ECG": ["Img2"],
               "Heart_Rate": ["150"]}
    new_patient_driver(patient)
    hello, time, status_code = update_patient_info_driver(in_data, validated)
    patient1 = Patient.objects.raw({"_id": 12345})
    patient1.delete()
    assert status_code == expected


@pytest.mark.parametrize("in_data, query, expected",
                         [({"Name": "Phil", "Rec_No": "12345",
                            "Heart_Rate": "123"},
                           {"Name": "Phil", "Rec_No": "12345"},
                           True),
                          ({"Name": "Phil", "Rec_No": "12345",
                            "Heart_Rate": "123"},
                           {"Name": "Diana", "Rec_No": "54321"},
                           False)])
def test_patient_exist(in_data, query, expected):
    from cloud_server import patient_exist, new_patient_driver
    new_patient_driver(in_data)
    patient_status = patient_exist(query)
    patient1 = Patient.objects.raw({"_id": 12345})
    patient1.delete()
    assert patient_status == expected


@pytest.mark.parametrize("in_data, expected",
                         [({"Name": "Phil", "Rec_No": "12345"}, 200),
                          ({"Name": "Diana"}, 400)
                          ])
def test_validate_server_input(in_data, expected):
    from cloud_server import validate_server_input, new_patient_driver
    new_patient_driver(in_data)
    (message, status_code) = validate_server_input(in_data)
    assert status_code == expected


@pytest.mark.parametrize("in_data, patient, expected",
                         [(Patient(patient_name="Phil",
                                   patient_id="12345",
                                   ecg_images=["Img3"],
                                   medical_images=["Img4"],
                                   heartrate=["123"]),
                           Patient(patient_name="Phil",
                                   patient_id="12345",
                                   ecg_images=["Img1"],
                                   medical_images=["Img2"],
                                   timestamp=["01/14/2012, 03:21:34"],
                                   heartrate=["150"]),
                           Patient(patient_name="Phil", patient_id="12345",
                                   ecg_images=["Img1", "Img3"],
                                   medical_images=["Img2", "Img4"],
                                   timestamp=["01/14/2012, 03:21:34",
                                              "04/12/2022, 17:17:15"],
                                   heartrate=["150", "123"]))])
def test_update_patient_info(in_data, patient, expected):
    from cloud_server import update_patient_info, new_patient_driver
    # set time
    initial_datetime = datetime.datetime(year=2022, month=4, day=12,
                                         hour=17, minute=17, second=15)
    freezer = freeze_time(initial_datetime)
    new_patient_driver(patient)
    saved_patient, now, status_code = update_patient_info(in_data, patient)
    patient1 = Patient.objects.raw({"_id": 12345}).first()
    patient1.delete()
    assert saved_patient == expected
