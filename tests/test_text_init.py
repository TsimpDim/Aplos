from Aplos import AplosParser, exceptions
import os
import pytest


def test_normal_text():
    text = '''Max 3x1 +2x2

              s.t. x1+2x2<=9

              2x1+5x2<=4

              End'''

    parser = AplosParser(text=text)

    res = []
    res.append('Max3x1+2x2')
    res.append('s.t.x1+2x2<=9')
    res.append('2x1+5x2<=4')
    res.append('End')

    assert parser.lp_lines == res

def test_empty_text():

    with pytest.warns(RuntimeWarning):
        parser = AplosParser(text='')

def test_text_no_arguments():

    with pytest.raises(exceptions.MissingArgumentsException):
        parser = AplosParser()    

def test_text_custom_delimeter_comma():
    text = '''Max 3x1 +2x2,s.t. x1+2x2<=9,2x1+5x2<=4,End'''

    parser = AplosParser(text=text, delimeter=',')

    res = []
    res.append('Max3x1+2x2')
    res.append('s.t.x1+2x2<=9')
    res.append('2x1+5x2<=4')
    res.append('End')

    assert parser.lp_lines == res 

def test_text_custom_delimeter_line():
    text = '''Max 3x1 +2x2|          s.t. x1+2x2<=9       |2 x1+5x2<=4|End'''

    parser = AplosParser(text=text, delimeter='|')

    res = []
    res.append('Max3x1+2x2')
    res.append('s.t.x1+2x2<=9')
    res.append('2x1+5x2<=4')
    res.append('End')

    assert parser.lp_lines == res 

def test_text_wrong_delimeter():
    text = '''Max 3x1 +2x2|          s.t. x1+2x2<=9       |2 x1+5x2<=4|End'''

    parser = AplosParser(text=text, delimeter='.')

    res = []
    res.append('Max3x1+2x2|s')
    res.append('t')
    res.append('x1+2x2<=9|2x1+5x2<=4|End')

    assert parser.lp_lines == res 