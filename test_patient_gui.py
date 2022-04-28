# test_patient_gui.py
import pytest


@pytest.mark.parametrize('entered_name, entered_id, ecg_is_uploaded, \
                          med_img_is_uploaded, med_filename, expected_keys', [
    ["Philjae Chang", "1027", True, True, "N/A", ["Name", "Rec_No"]],
    ["", "1992", True, True, "N/A", ["Rec_No"]],
    ["philjae", "122", True, False, "med.jpg", ["Rec_No", "Name", "Med_Img"]],
    ["Diana", "1234", False, True, "N/A",
        ["Rec_No", "Name", "ECG", "Heart_Rate"]]
])
def test_create_info_dict(entered_name, entered_id,
                          ecg_is_uploaded, med_img_is_uploaded,
                          med_filename, expected_keys):
    from patient_gui import create_info_dict
    dict = create_info_dict(entered_name, entered_id, ecg_is_uploaded,
                            med_img_is_uploaded, med_filename)
    assert sorted(dict.keys()) == sorted(expected_keys)


@pytest.mark.parametrize('entered_id, expected', [
    ['10407', 200],
    ['110.2', 400],
    ["", 400],
    ["two", 400],
    ["philaje", 400]
])
def test_verify_GUI_input(entered_id, expected):
    from patient_gui import verify_GUI_input
    answer, status_code = verify_GUI_input(entered_id)
    assert status_code == expected
