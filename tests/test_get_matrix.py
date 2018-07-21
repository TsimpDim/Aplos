from Aplos import AplosParser, exceptions
import os
import pytest


def test_get_matrix_empty():

    with pytest.warns(RuntimeWarning):
        parser = AplosParser(text='')

        with pytest.raises(exceptions.EmptyLPException):
            if not parser.detect_errors():
                A = parser.get_matrix('A')

def test_get_matrix_no_arg():
    
    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)
    if not parser.detect_errors():

        with pytest.raises(exceptions.MissingArgumentsException):
            A = parser.get_matrix()

def test_get_matrix_errors():
    FILE_NAME = 'error_lp_1.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)
    with pytest.raises(exceptions.LPErrorException):
        A = parser.get_matrix('A')

def test_get_matrix():

    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)
    if not parser.detect_errors():
        A = parser.get_matrix('A')
        b = parser.get_matrix('b')
        c = parser.get_matrix('c')
        Eqin = parser.get_matrix('EQin')
        minmax = parser.get_matrix('minMAX')

        expected_A = [[1,2],[2,5]]
        expected_b = [9,4]
        expected_c = [3,2]
        expected_Eqin = [-1, -1]
        expected_minmax = [1]

        assert A == expected_A and \
               b == expected_b and \
               c == expected_c and \
               Eqin == expected_Eqin and \
               minmax == expected_minmax

