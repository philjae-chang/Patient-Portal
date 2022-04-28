import pytest


def test_convert_b64_string_to_file():
    from gui_client import convert_b64_string_to_file
    from gui_client import convert_file_to_b64_string
    import filecmp
    import os
    b64str = convert_file_to_b64_string("test_image.jpg")
    convert_b64_string_to_file(b64str, "test_image_output.jpg")
    answer = filecmp.cmp("test_image.jpg",
                         "test_image_output.jpg")
    os.remove("test_image_output.jpg")
    assert answer is True


def test_convert_file_to_b64_string():
    from gui_client import convert_file_to_b64_string
    b64str = convert_file_to_b64_string("test_image.jpg")
    assert b64str[0:20] == "/9j/4AAQSkZJRgABAQEA"
