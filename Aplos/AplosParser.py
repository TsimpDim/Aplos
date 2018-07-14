import exceptions as ex
import warnings
import re as r

class AplosParser:
    lp_lines = []

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
            raise ex.MissingArguementsException('No \'text\' or \'filename\' arguement specified for initialization')

        if self.lp_lines == []:
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
            last_idx = int(var_list[-1][1:])
            for i in range(1, last_idx+1):
                extended_list.append('x' + str(i))


            return {"existing":var_list, "extended":extended_list}