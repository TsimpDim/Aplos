# coding=utf-8

from .exceptions import *
import warnings
import re as r

class AplosParser:
    lp_lines = []
    error_list = []
    constr_end_idx = -1
    m = 0
    n = 0

    def __read_file_lines(self, filename):
        '''Reads text file line by line'''

        with open(filename, 'r') as lp_file:
            text_lines = [''.join(line.split()) for line in lp_file.readlines()] # Remove whitespace
            text_lines = list(filter(None, text_lines)) # Filter empty lines

            return text_lines

    def __read_text_lines(self, text, delimeter):
            '''Processes text to desired format'''

            text_lines = text.replace(' ','').split(delimeter) # Remove whitespace
            text_lines = list(filter(None, text_lines)) # Filter empty lines

            return text_lines

    def __process_factors(self, matrix, line, line_idx=None):
        '''Τhis function is in charge of returning a list with the 
            factors from the given line. 
            
            Firstly, it finds the variables that 
            have 'hiden' factors, like 'x1' the hidden factor of which is 1,
            and it adds those missing factors back.
            
            It then finds the factors and the index of the variables they belong
            with two regex searches. 

                i.e '1x1 + 3x3 - 2x4' 
                    -> factor = [1,+3,-2]
                    -> factor_pos = [1,3,4]
            
            After all that is said and done it fills up the given matrix
            with the factors and returns it.

            ! The function is built to run both for 1D and 2D lists.
        '''

        # Add missing factors
        prob_fact = r.findall(r'(?<!\d)x\d+', line)
        for fac in prob_fact:
            line = line.replace(fac, '1' + fac)
            
        factors = r.findall(r'([-–+]?\d+)(?=x\d+)', line) # Different hyphens
        factor_pos = r.findall(r'(?<=x)\d+', line) # Indices of variables

        # Set values
        for i,fact in enumerate(factors):
            fac_pos = int(factor_pos[i]) - 1
            number = int(fact.replace('+', '').replace('–', '-')) # Replace em-dash with en-dash

            if isinstance(matrix[0], list):
                matrix[line_idx][fac_pos] = number
            else:
                matrix[fac_pos] = number
        
        if isinstance(matrix[0], list):
            for i,row in enumerate(matrix):
                matrix[i] = [0 if el is None else el for el in row]
        else:
            matrix = [0 if el is None else el for el in matrix]

        return matrix

    def __init__(self, filename=None, text=None, delimeter='\n'):

        if filename and not text:
            self.lp_lines = self.__read_file_lines(filename=filename)
        elif not filename and (text or text == ''):
            # We check for an empty string here because we want
            # to raise a warning instead of raising an exception.
            # If we used 'not filename and text' an exception would
            # be thrown on an empty string

            self.lp_lines = self.__read_text_lines(text,delimeter)
        else:
            raise MissingArgumentsException('No \'text\' or \'filename\' argument specified for initialization')

        if not self.lp_lines:
            warnings.warn('LP lines are empty, no data is available', RuntimeWarning)

    def get_vars(self, line_idx=None):
        '''This function if not given an index returns the full list of variables 
           present in the LP.

                i.e for 'min 3x1 + 2x4 - x6 , st 3x1 + 2x2 <= 4 , 5x3 - 4x6 >= 3, END'

                it returns ['x1','x2','x3','x4','x5','x6']
        
        
            Otherwise, if given an index, it returns a dict with the variables 
            in the given line.
            
                i.e if line 0 is 'min 3x1 + 4x3 - 6x4'

                then 
                >variables = get_vars(0) 
                
                returns the following dict:

                {"existing":['x1','x3','x4'], "extended":['x1','x2','x3','x4']}   
        '''


        if line_idx == None:

            maxim = []
            
            # We ignore the last line because it should contain 'END'.
            # If we don't ignore it we will get an IndexError later on
            # since there'd be no regex matches for us to access.
            for idx,line in enumerate(self.lp_lines[:-1]):
                variables = self.get_vars(line_idx=idx)['extended']
                if len(variables) > len(maxim):
                    maxim = variables
            
            return maxim

        else:

            if line_idx > len(self.lp_lines) : raise IndexError()

            # 'Max' in the first line causes a problem since
            # the regex will then count 'Max 3x2' as two matches
            # of 'x3' and 'x2'
            line = self.lp_lines[line_idx].lower().replace('max', '')

            var_list = r.findall(r'x\d+', line)
            extended_list = []

            # Add missing variables
            # If the list is empty that means there are no variables
            # in the given line, hence the LP is faulty.
            if var_list != []:
                last_idx = int(var_list[-1][1:])
                for i in range(1, last_idx+1):
                    extended_list.append('x' + str(i))


            return {"existing":var_list, "extended":extended_list}

    def detect_errors(self, print_msg=False):
        '''This function collects the many possible errors in the syntax 
            of the given LP. 
            
            It returns the error_list which contains
            messages with the errors
            
            An exception is thrown if the LP contains no lines
            and a warning is raised if there are errors in the LP.
        '''
        
        self.error_list = [] # Reset error_list

        if not self.lp_lines:
            raise EmptyLPException("Given LP is empty. Can't detect errors")

        # Min/Max not specified
        if all(i not in self.lp_lines[0].lower() for i in ['min', 'max']):
            self.error_list.append('Min/Max is not specified for object function')

        # Both Min & Max specified
        if all(i in self.lp_lines[0].lower() for i in ['min', 'max']):
            self.error_list.append('Optimization way is ambiguous. Use either min or max.')

        # No constraint initializer
        if all(i not in self.lp_lines[1].lower() for i in ['s.t.', 's.t', 'st', 'subjectto']):
            self.error_list.append("Constraint initializer 's.t' or similar is missing")

        # Check for 'END' statement
        # and remove the lines after it.
        for i,line in enumerate(self.lp_lines[1:]):
            if 'end' == line.lower():
                self.constr_end_idx = i + 1 # Since we start the loop from the 2nd element
                self.lp_lines[:] = self.lp_lines[:self.constr_end_idx] # Remove every line after (and including) the one containing the END statement
                break
        else: # If for loop doesn't break
            self.error_list.append('No END statement found')    
        
        # Missing constraint types
        for line in self.lp_lines[1:]:
            if all(i not in line for i in ['=','<=','>=']):
                self.error_list.append('Constraint type missing from some constraints')
                break

        # Missing right side arguments
        for line in self.lp_lines[1:]:
            right_side = r.findall(r'=\d+', line)
            if not right_side:
                self.error_list.append('Right side argument missing from some constraints')
                break

        # Missing signs from factors
        for idx,line in enumerate(self.lp_lines):

            variables = len(self.get_vars(idx)["existing"])
            signs = len(r.findall(r'[-,+]', line))

            if not signs <= variables <= signs + 1:
                self.error_list.append('Sign missing from some factors')
                break
        
        # Print message containing the error messages (if any)
        if print_msg:
            print('-' * 10)
            print("[{0}] errors detected".format(len(self.error_list)))
            if self.error_list:
                print('\n'.join(['-' + er for er in self.error_list]))
            print('\n')
        
        if len(self.error_list) > 0:
            warnings.warn('Given LP contains syntax problems.', RuntimeWarning)

        return self.error_list

    def get_dimensions(self):
        '''This function returns the dimensions of the problem
           where m = the number of constraints and 
           n = the number of variables.
           
           It returns a dict containing those two values.
        ''' 

        if not self.lp_lines:
            raise EmptyLPException("Given LP is empty. Can't get dimensions")

        # By checking if constr_end_idx != -1 we can be sure that the user has 
        # ran detect_errors() first.
        if not self.error_list and self.constr_end_idx != -1:

            # We subtract 1 from m because
            # we don't want to count the object function.
            # We DON'T care about the 'END' line because
            # we can be sure that it will be removed from detect_errors()
            self.m = len(self.lp_lines) - 1
            self.n = len(self.get_vars())

            return {'m':self.m, 'n':self.n}

        elif not self.error_list and self.constr_end_idx == -1:
            raise LPErrorException("Given LP may contain errors. Search for errors first.")

        else:
            raise LPErrorException("Given LP contains errors. Can't get dimensions")

    def get_matrix(self, matrix=None):
        '''This function returns the LP matrix corresponding
            to the given matrix argument given.

            i.e get_matrix(matrix='A') returns the matrix 'A' and so on

            Eqin -- '<=': -1 | '>=' : 1 | '=' : 0
            MinMax -- 'max':1 | 'min':-1
        '''

        # Make sure the problem can be parsed with our mind
        # at ease about errors.
        if not matrix:
            raise MissingArgumentsException("Cannot calculate default 'None' matrix.\
             Desired matrix must be specified via the 'matrix' keyword.")

        if not self.lp_lines:
            raise EmptyLPException("Given LP is empty. Can't calculate matrices.")

        if not self.error_list and self.constr_end_idx == -1:
            raise LPErrorException("Given LP may contain errors. Search for errors first.")
        
        elif self.error_list and self.constr_end_idx != -1:
            raise LPErrorException("Given LP contains errors. Can't get dimensions")
       
        else:
            # Make sure m & n are assigned to the parser object
            if not self.m or not self.n : self.get_dimensions()

            if matrix.lower() == 'a':
                A = [[None]*self.n for _ in range(self.m)]
                for i,line in enumerate(self.lp_lines[1:]):
                    A = self.__process_factors(A, line, i)
                
                return A
            
            elif matrix.lower() == 'b':
                b = [None]*self.m
                for i,line in enumerate(self.lp_lines[1:]):
                    b[i] = int(r.findall(r'(?<==)(\d+)', line)[0])

                return b
            
            elif matrix.lower() == 'c':
                c = [None]*self.n
                line_to_proc = self.lp_lines[0].lower().replace('max', '').replace('min', '')
                c = self.__process_factors(c, line_to_proc)

                return c
            
            elif matrix.lower() == 'eqin':
                Eqin = [None]*self.m
                con_vals = {'<=': -1, '>=' : 1, '=' : 0}

                for i,line in enumerate(self.lp_lines[1:]):
                    con_type = r.findall(r'[><]?=', line)[0]
                    Eqin[i] = con_vals[con_type]
                
                return Eqin

            elif matrix.lower() == 'minmax':
                MinMax = []
                if 'min' in self.lp_lines[0].lower():
                    MinMax.append(-1)
                elif 'max' in self.lp_lines[0].lower():
                    MinMax.append(1) 

                return MinMax            

    def get_matrices(self):
        '''This function returns a dict containing each and every
            matrix available from get_matrix. 

            No tests are run for get_matrices() since it is covered but
            the tests on get_matrix().
        '''

        if not self.lp_lines:
            raise EmptyLPException("Given LP is empty. Can't calculate matrices.")

        if not self.error_list and self.constr_end_idx == -1:
            raise LPErrorException("Given LP may contain errors. Search for errors first.")
        
        elif self.error_list and self.constr_end_idx != -1:
            raise LPErrorException("Given LP contains errors. Can't get dimensions")
       
        else:
            m_A = self.get_matrix(matrix='a')
            m_b = self.get_matrix(matrix='b')
            m_c = self.get_matrix(matrix='c')
            m_Eqin = self.get_matrix(matrix='Eqin')
            m_minMax = self.get_matrix(matrix='minmax')

            return {'A':m_A, 'b':m_b, 'c':m_c, 'Eqin':m_Eqin, 'MinMax':m_minMax}