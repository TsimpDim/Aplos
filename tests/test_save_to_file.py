from Aplos import AplosParser, exceptions
import os
import pytest


def test_save_to_file_normal():

    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    if not parser.detect_errors():
        output_file = os.path.join(CUR_DIR, 'files/output_tests/output.txt')
        expected_file = os.path.join(CUR_DIR, 'files/matrices_file.txt')
        parser.write_matrices_to_file(output_file)
        
        with open(output_file, 'r') as of, open(expected_file, 'r') as ef:
            assert of.read() == ef.read()

def test_save_to_file_errors():
    
    FILE_NAME = 'error_lp_1.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    with pytest.raises(exceptions.LPErrorException):
        output_file = os.path.join(CUR_DIR, 'files/output_tests/output.txt')

        parser.write_matrices_to_file(output_file)

def test_save_to_file_empty():
    
    with pytest.warns(RuntimeWarning):
        parser = AplosParser(text='')

    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(CUR_DIR, 'files/output_tests/output.txt')

    with pytest.raises(exceptions.EmptyLPException):
        parser.write_matrices_to_file(output_file)

def test_save_to_file_dual():

    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    if not parser.detect_errors():
        output_file = os.path.join(CUR_DIR, 'files/output_tests/output_dual.txt')
        expected_file = os.path.join(CUR_DIR, 'files/matrices_file_dual.txt')
        parser.write_matrices_to_file(output_file, dual=True)
        
        with open(output_file, 'r') as of, open(expected_file, 'r') as ef:
            assert of.read() == ef.read()