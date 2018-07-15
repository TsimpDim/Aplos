from Aplos import AplosParser, exceptions
import os
import pytest

def test_det_errors_no_errors():

    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)
    errors = parser.detect_errors()

    expected_err = []

    assert errors == expected_err