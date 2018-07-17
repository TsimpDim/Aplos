from Aplos import AplosParser, exceptions
import os
import pytest

def test_dim_empty():

    with pytest.warns(RuntimeWarning):
        parser = AplosParser(text=' ')

    with pytest.raises(exceptions.EmptyLPException):
        parser.get_dimensions()

def test_dim_errors():

    FILE_NAME = 'error_lp_1.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    with pytest.warns(RuntimeWarning):
        parser.detect_errors()
    
    with pytest.raises(exceptions.LPErrorException):
        parser.get_dimensions()

def test_dim_normal():

    FILE_NAME = 'secondary_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    if not parser.detect_errors():
        dims = parser.get_dimensions()
        expected = {'m':2, 'n':6}

        assert dims == expected

def test_dim_no_detect_errors():

    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    with pytest.raises(exceptions.LPErrorException):
        parser.get_dimensions()


