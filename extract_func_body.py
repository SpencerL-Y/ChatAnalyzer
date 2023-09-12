import os, sys
import re
import get_arguments as ga


if __name__ == "__main__":
    func_name = sys.argv[1]
    search_result = ga.get_filename_firstline(func_name)
    filename = search_result[0]
    function_firstline_str = search_result[1]
    function_str = ""
    f = open(filename)
    lines = f.readlines()
    function_start = False
    bracket_stack = 0 
    into_body = False
    for line in lines:
        if line == function_firstline_str + "\n":
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
    print(function_str)
    f.close()

def extract_function_body(func_name):
    print("extract func body for: " + func_name)
    search_result = ga.get_filename_firstline(func_name)
    if(search_result[0] == "NOT FOUND"):
        return "NOT FOUND"
    filename = search_result[0]
    function_firstline_str = search_result[1]
    function_str = ""
    f = open(filename)
    lines = f.readlines()
    function_start = False
    bracket_stack = 0 
    into_body = False
    for line in lines:
        if line == function_firstline_str + "\n":
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
    f.close()
    return function_str
