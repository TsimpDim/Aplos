from Aplos import AplosParser, exceptions
import os
import pytest    

def test_get_vars_normal_first_line():
    
    FILE_NAME = 'main_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    variables = parser.get_vars(line_idx=0)

    expected = {"existing":['x1','x2'], "extended":['x1','x2']}

    assert variables == expected

def test_get_vars_normal_second_line():
    
    FILE_NAME = 'secondary_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)

    variables = parser.get_vars(line_idx=1)

    expected = {"existing":['x1','x2','x3','x5','x6'], "extended":['x1','x2','x3','x4','x5','x6']}

    assert variables == expected

def test_get_vars_empty_lines():
    
    FILE_NAME = 'empty.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)    
    
    with pytest.raises(IndexError), pytest.warns(RuntimeWarning):
        parser = AplosParser(filename=test_file)

        variables = parser.get_vars(line_idx=0)

def test_get_vars_one_var():

    text_lp = " Min 3x1 | st 2x1 | END"

    parser = AplosParser(text=text_lp, delimeter='|')

    variables = parser.get_vars(line_idx=0)
    expected = {"existing":['x1'], "extended":['x1']}

    assert variables == expected

def test_get_vars_no_idx():
    
    FILE_NAME = 'secondary_lp.txt'
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(CUR_DIR, 'files/'+FILE_NAME)

    parser = AplosParser(filename=test_file)
    variables = parser.get_vars()

    expected = ['x1','x2','x3','x4','x5','x6']

    assert variables == expected

def test_get_vars_no_idx_empty():

    with pytest.warns(RuntimeWarning):
        parser = AplosParser(text=' ')
        variables = parser.get_vars()

        expected = []

        assert variables == expected