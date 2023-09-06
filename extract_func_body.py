import os, sys
import re


if __name__ == "__main__":
    filename = sys.argv[1]
    # function_firstline_str = sys.argv[2]
    function_str = ""
    f = open(filename)
    lines = f.readlines()
    function_start = False
    bracket_stack = 0 
    into_body = False
    for line in lines:
        print(line)
        if line == "int altera_wait_cycles(struct altera_state *astate,\n":
            function_start = True
            
        if function_start:
            bracket_stack += line.count("{") - line.count("}")
            if bracket_stack > 0:
                into_body = True
                function_str += line 
            elif bracket_stack == 0 and not into_body:
                function_str += line
            elif bracket_stack == 0 and into_body:
                function_str += line
                function_start = False
                break
        print(bracket_stack)
    print(function_str)
    f.close()
