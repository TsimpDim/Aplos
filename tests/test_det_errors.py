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

def test_det_errors_empty():

    FILE_NAME = 'empty.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)
    with pytest.raises(exceptions.EmptyLPException):
        errors = parser.detect_errors()

def test_det_errors_normal():

    FILE_NAME = 'error_lp_2.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    with pytest.warns(RuntimeWarning):
        errors = parser.detect_errors()

        expected_errs = []
        expected_errs.append('Min/Max is not specified for object function')
        expected_errs.append("Constraint initializer 's.t' or similar is missing")

        assert errors == expected_errs

def test_det_errors_no_end():
    
    FILE_NAME = 'error_lp_1.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    with pytest.warns(RuntimeWarning):
        errors = parser.detect_errors(print_msg=True)

        expected_errs = []
        expected_errs.append('Min/Max is not specified for object function')
        expected_errs.append('No END statement found')
        expected_errs.append('Constraint type missing from some constraints')
        expected_errs.append('Right side argument missing from some constraints')

        assert errors == expected_errs