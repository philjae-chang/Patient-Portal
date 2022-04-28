import pytest


def test_get_selected_ecg_64():
    from monitoring_gui import get_selected_ecg_64
    patient = {"Timestamp": ["2019-10-27 12:12:12",
                             "2018-10-12 12:12:12"],
               "ECG": ["ECG 1", "ECG 2"]}
    ecg_of_interest_timestamp = "2019-10-27 12:12:12"
    answer = get_selected_ecg_64(ecg_of_interest_timestamp, patient)
    expected = "ECG 1"
    assert answer == expected
