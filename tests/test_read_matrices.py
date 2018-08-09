from Aplos import AplosParser, exceptions
import os
import pytest

def test_open_file_normal():

    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)
    output_file = os.path.join(CUR_DIR, 'files/output_tests/output.txt')

    parser = AplosParser(filename=test_file)
    matrices = parser.read_matrices_from_file(output_file)

    ex_A = [[1,2],[2,5]]
    ex_b = [9,4]
    ex_c = [3,2]
    ex_Eqin = [-1, -1]
    ex_minmax = [1]

    ex = {'A':ex_A, 'b':ex_b, 'c':ex_c, "Eqin":ex_Eqin, 'MinMax':ex_minmax}

    assert ex == matrices

def test_open_file_non_existing():
    
    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    with pytest.raises(IOError):
        matrices = parser.read_matrices_from_file('a_path')

def test_open_file_error():
    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)
    output_file = os.path.join(CUR_DIR, 'files/output_tests/output_wrong.txt')

    parser = AplosParser(filename=test_file)

    with pytest.raises(exceptions.LPReadException):
        matrices = parser.read_matrices_from_file(output_file)

def test_open_file_dual():
    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)
    output_file = os.path.join(CUR_DIR, 'files/output_tests/output_dual.txt')

    parser = AplosParser(filename=test_file)
    matrices = parser.read_matrices_from_file(output_file, dual=True)

    ex_A = [[1,2],[2,5]]
    ex_b = [3,2]
    ex_c = [9,4]
    ex_Eqin = [1, 1]
    ex_minmax = [-1]
    ex_varconstr = [1, 1]

    ex = {'A':ex_A, 'b':ex_b, 'c':ex_c, "Eqin":ex_Eqin, 'MinMax':ex_minmax, 'VarConstr':ex_varconstr}

    assert ex == matrices