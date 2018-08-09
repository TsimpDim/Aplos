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

            i.e get_matrix('A') returns the matrix 'A' and so on

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
            m_A = self.get_matrix('a')
            m_b = self.get_matrix('b')
            m_c = self.get_matrix('c')
            m_Eqin = self.get_matrix('Eqin')
            m_minMax = self.get_matrix('minmax')

            return {'A':m_A, 'b':m_b, 'c':m_c, 'Eqin':m_Eqin, 'MinMax':m_minMax}

    def write_matrices_to_file(self, path, dual=False):
        '''This function uses the nested function format_string()
           to turn all available matrices into strings and then
           save them to the specified `path`.

           To save the dual matrices set dual=True.
        '''

        def format_string(name, matrix):
            '''format_string() turns the given matrix into a string.

               `name` is the name of the given matrix and 
               `matrix` is the matrix itself.

               `name` is used to label the matrix.

               This function is built to work with both 1D and 2D lists/matrices.
            '''
            
            matrix_string = name +'=['
            if isinstance(matrix, list):
                for i,el in enumerate(matrix):
                    if i == len(matrix) - 1:
                        matrix_string += str(el)
                    else:
                        matrix_string += str(el) + '\n'
            else:
                for row in matrix:
                    row_string = ' '.join(str(el) for el in row)
                    if row == matrix[-1]:
                        matrix_string += row_string
                    else:
                        matrix_string += row_string + '\n'

            matrix_string += ']\n\n'
            return matrix_string

        if not self.lp_lines:
            raise EmptyLPException("Given LP is empty. Can't calculate matrices.")

        if not self.error_list and self.constr_end_idx == -1:
            raise LPErrorException("Given LP may contain errors. Search for errors first.")
        
        elif self.error_list and self.constr_end_idx != -1:
            raise LPErrorException("Given LP contains errors. Can't calculate matrices.")
        

        with open(path, 'w') as lp2f:

            if dual: m = self.get_dual_matrices()
            else : m = self.get_matrices()

            A_string = format_string('A', m['A'])
            lp2f.write(A_string)

            b_string = format_string('b', m['b'])
            lp2f.write(b_string)
            
            c_string = format_string('c', m['c'])
            lp2f.write(c_string)

            eqin_string = format_string('Eqin', m['Eqin'])
            lp2f.write(eqin_string)

            lp2f.write(format_string('MinMax', m['MinMax']))

            if dual:
                constr = {0:'free', 1:'>= 0', -1:'<= 0'}

                for i,el in enumerate(m['VarConstr']):
                    lp2f.write("w_{0} {1}\n".format(i+1, constr[int(el)]))
                        
    def get_dual_matrix(self, matrix=None):
        '''This function calculates and returns the specified matrix
           of the dual form of the LP.

           Rules:
            * A gets transposed
            * b & c get swapped
            * min becomes max
            * from min to max, if x(i)>=0 : constraint(i)<=0 and vice versa
            * if constraint(i) is '='  : w(i) is 'free'
              if constraint(i) is '>=' : w(i) is '>= 0'
              if constraint(i) is '<=' : w(i) is '<= 0'
        '''

        if not matrix:
            raise MissingArgumentsException("Cannot calculate default 'None' matrix.\
             Desired matrix must be specified via the 'matrix' keyword.")

        if not self.lp_lines:
            raise EmptyLPException("Given LP is empty. Can't calculate matrices.")

        if not self.error_list and self.constr_end_idx == -1:
            raise LPErrorException("Given LP may contain errors. Search for errors first.")
        
        elif self.error_list and self.constr_end_idx != -1:
            raise LPErrorException("Given LP contains errors. Can't calculate matrices.")
       
        else:

            if matrix.lower() == 'a':
                return [list(i) for i in zip(*self.get_matrix('A'))]
            
            elif matrix.lower() == 'b':
                return self.get_matrix('c')
            elif matrix.lower() == 'c':
                return self.get_matrix('b')
            
            elif matrix.lower() == 'minmax':
                if self.get_matrix('minmax') == [1] : return [-1]
                else: return [1]

            elif matrix.lower() == 'eqin':
                # Build Eqin assuming that x(i) >= 0 for every i
                if self.get_matrix('minmax')[0] == '-1':
                    # Every constraint will be <=
                    base_str = '-1, ' * len(self.get_matrix('a')[0])

                    # [:-2] -> We ignore the last element since it will 
                    # always be empty due to the way base_str is built
                    new_eqin = base_str[:-2].split(',') 
                    new_eqin = [int(i) for i in new_eqin]

                else:
                    # Every constraint will be >=
                    base_str = '1, ' * len(self.get_matrix('a')[0])
                    new_eqin = base_str[:-2].split(',') 
                    new_eqin = [int(i) for i in new_eqin]

                return new_eqin
            
            elif matrix.lower() == 'var_constr':
                # Find new variable restrictions
                var_constr = []
                if self.get_matrix('minmax')[0] == '1':
                    for constr in self.get_matrix('eqin'): # For every constraint
                        if constr == '0':
                            var_constr.append('0')
                        elif constr == '-1':
                            var_constr.append('1')
                        else:
                            var_constr.append('-1')
                else:
                    for constr in self.get_matrix('eqin'):
                        if constr == '0':
                            var_constr.append('0')
                        elif constr == '-1':
                            var_constr.append('-1')
                        else:
                            var_constr.append('1')

                return [int(i) for i in var_constr]

    def get_dual_matrices(self):
        '''This function works the same way as get_matrices().
           Similarly, it returns all the dual matrices in a dict.
        '''

        d_A = self.get_dual_matrix('a')
        d_b = self.get_dual_matrix('b')
        d_c = self.get_dual_matrix('c')
        d_Eqin = self.get_dual_matrix('Eqin')
        d_minMax = self.get_dual_matrix('minmax')
        d_var_cons = self.get_dual_matrix('var_constr')


        return {'A':d_A, 'b':d_b, 'c':d_c, 'Eqin':d_Eqin, 'MinMax':d_minMax, 'VarConstr': d_var_cons}

    def read_matrices_from_file(self, path, dual=False):
        def extract_one_dim_matrix(regex, matrix):
            """This inner function returns a 1D matrix read from the specified
               path.

               It uses a unique regex for every matrix to get a string which
               contains the matrix in raw form. 
               
               Then, to get only the contents of
               the matrix, it finds the first (min) possible break points (next_x)
               and if the current element in the loop is a number it appends it to the
               matrix - which will then be returned.
            """

            factor_string = r.findall(regex, text, flags=r.S)
            if not factor_string:
                raise LPReadException ("Aplos couldn't read the matrices correctly.")

            factor_string = factor_string[0]

            i = 0
            while i < len(factor_string):
                char = factor_string[i]
                next_newline = factor_string.find('\n', i)
                next_bracket = factor_string.find(']', i)

                end_of_el = min(next_bracket, next_newline) - 1

                if char == '-' or char.isdigit(): # If char is number
                    matrix.append(int(factor_string[i:end_of_el + 1]))
                    i = end_of_el + 1
                
                i += 1
        
        def read_file(path):
            with open(path, 'r') as lp_file:
                return lp_file.read()
        

        text = read_file(path)

        # Extract 'A' matrix
        # The code here is almost exactly the same
        # as extract_one_dim_matrix() but the differences were enough
        # to not make it an extra case in the function.
        factor_string = r.findall(r'A=.*?\]\]\n', text, flags=r.S)
        if not factor_string:
            raise LPReadException ("Aplos couldn't read the matrices correctly.")
        factor_string = factor_string[0]

        row_amount = factor_string.count('\n')
        A = [[] for _ in range(row_amount)] # Initialize with appropriate rows
        cur_row = 0
        i = 0
        while i < len(factor_string):
            char = factor_string[i]
            next_comma = factor_string.find(',', i)
            next_bracket = factor_string.find(']', i)
            next_space = factor_string.find(' ', i)

            end_of_el = min(next_comma, next_bracket) - 1
            if end_of_el < 0 : end_of_el = next_bracket - 1

            if char == '-' or char.isdigit(): # If char is number (neg/pos)
                A[cur_row].append(int(factor_string[i:end_of_el + 1]))

                if next_space == -1: # If there aren't any more spaces
                    break
                else:
                    i = min(next_space, next_bracket) # In case this is the last element - so we don't skip elements
            
            elif char =='\n':
                cur_row += 1

            i += 1

        # Find b matrix
        b = []
        extract_one_dim_matrix(r'b=.*?\]\n', b)

        # Find c matrix
        c = []
        extract_one_dim_matrix(r'c=.*?\]\n', c)

        # Find Eqin matrix
        eqin = []
        extract_one_dim_matrix(r'Eqin=.*?\]\n', eqin)

        # Find MinMax
        min_max = r.findall(r'(?<=MinMax=\[)[-+]?\d', text)
        min_max[0] = int(min_max[0])

        # Find variable constraints
        constraints = r.findall(r'(?<=w\_).*?\n', text)
        var_constr = []
        for con in constraints:
            if '>=' in con:
                var_constr.append(1)
            elif '<=' in con:
                var_constr.append(-1)
            else:
                var_constr.append(0)

        if dual:
            return{'A' : A, 'b' : b, 'c' : c, 'Eqin' : eqin, 'MinMax' : min_max, 'VarConstr':var_constr} 
        else:
            return{'A' : A, 'b' : b, 'c' : c, 'Eqin' : eqin, 'MinMax' : min_max}