from Aplos import AplosParser, exceptions
import os
import pytest

def test_det_errors_no_errors():

    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    errors = parser.detect_errors()

    assert errors == []

def test_det_errors_normal():
    
    FILE_NAME = 'error_lp_2.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    with pytest.warns(RuntimeWarning):
        parser = AplosParser(filename=test_file)
        errors = parser.detect_errors()   

        expected = []
        expected.append('Min/Max is not specified for object function') 
        expected.append("Constraint initializer 's.t' or similar is missing")

    assert errors == expected

def test_det_errors_empty():

    with pytest.warns(RuntimeWarning), pytest.raises(exceptions.EmptyLPException):
        parser = AplosParser(text=' ')
        errors = parser.detect_errors()

def test_det_errors_no_end():

    FILE_NAME = 'error_lp_1.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    with pytest.warns(RuntimeWarning):
        parser = AplosParser(filename=test_file)
        errors = parser.detect_errors(print_msg=True)   

        expected = []
        expected.append('Min/Max is not specified for object function') 
        expected.append('No END statement found')
        expected.append('Constraint type missing from some constraints')
        expected.append('Right side argument missing from some constraints')

    assert errors == expected
