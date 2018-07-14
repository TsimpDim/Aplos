# Aplos

Aplos is a simple and elegant linear problem(LP) parser. It allows one to get all the information he needs about any linear problem given with the correct syntax. You can read more about Linear Programming [here.](https://en.wikipedia.org/wiki/Linear_programming)

#### Expected LP format

>Min/Max c<sup>t</sup>x  
>
>s.t /st /s.t./ Ax ⊗ b  
>
>End

Where ⊗ can be any of the following =, <=, >=

Variable(x) constraints/domains are not taken into consideration *(not yet)*.

---
Examples:

1. Max 3x1 +2x2

    s.t. x1+2x2<=9

	2x1+5x2<=4

	End
    
 2. min 3x1 - 5x2 + x4  
 	st x2 + x3 = 2  
       2x1 + 3x2 + 5x4 >= 5  
       x1 - 5x2 + 2x3 - 4x4 <= 10  
       END
       
## Usage
``` python
import Aplos

# Initialization
# From a file
parser = Aplos.AplosParser(filename='lp.txt')

# From a string
text_lp = '''Max 3x1 +2x2

s.t. x1+2x2<=9

2x1+5x2<=4

End'''

parser = Aplos.AplosParser(text=text_lp)

# From a string with a custom delimeter
text = '''Max 3x1 +2x3 + x5,s.t. x1+2x2<=9,2x1+5x2<=4,End'''

parser = AplosParser(text=text, delimeter=',')


# Getting the variables
variables_of_line = parser.get_vars(line_idx=0)
# variables_of_line = {"existing":['x1','x3'], "extended":['x1','x2','x3','x4','x5']}
variables_all = parser.get_vars()
# variables_all = ['x1','x2','x3','x4','x5']
```


*As the project continues, the 'usage' section will get updated and eventually (hopefully) be moved in a documentation file/page altogether.*

