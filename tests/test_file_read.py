from Aplos import AplosParser, exceptions
import os
import pytest

def test_open_file_exists():

    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    res = []
    res.append('Max3x1+2x2')
    res.append('s.t.x1+2x2<=9')
    res.append('2x1+5x2<=4')
    res.append('End')


    assert parser.lp_lines == res

def test_open_file_not_exists():

    FILE_NAME = 'NOT_EXISTS.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    with pytest.raises(IOError):
        parser = AplosParser(filename=test_file)

def test_open_file_no_lines():

    FILE_NAME = 'empty.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    with pytest.warns(RuntimeWarning):
        parser = AplosParser(filename=test_file)

    res = []

    assert parser.lp_lines == res

def test_open_file_no_arguments():

    with pytest.raises(exceptions.MissingArgumentsException):
        parser = AplosParser()
