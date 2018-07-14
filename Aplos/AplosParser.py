import exceptions as ex
import warnings

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