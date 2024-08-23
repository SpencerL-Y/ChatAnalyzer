import os
import sys
import subprocess

sys.path.insert(0, os.path.abspath('/home/clexma/Desktop/fox3/fuzzing/ChatAnalyzer'))
import extract_func_body as efb

project_root = "/home/clexma/Desktop/fox3/fuzzing/"

linux_folder = os.path.join(project_root, "linuxRepo/")

too_general = {"raise_exception"}


file_list = []
def listdir_recur(path, fl):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir_recur(file_path, fl)
        else:
            if file_path.endswith(".c") or file_path.endswith(".h"):
                fl.append(file_path)




def extract_call_path_for_func_name(curr_func_name, terminals, call_paths, parsed_funcs):

    call_paths = call_paths + efb.extract_func_body_linux_path(curr_func_name, linux_folder)
    if curr_func_name in too_general:
        return
    print("function name: " + curr_func_name)
    if file_list == []:
        listdir_recur(linux_folder + "/linux_new", file_list)
    contain_list = []
    for item in file_list:
        f = open(item)
        for line in f.readlines():
            if line.find(curr_func_name + "(") != -1:
                contain_list.append(item)
                break
        f.close()

    if len(set(contain_list)) > 10:
        print("WARNING many upper func_name used: " + curr_func_name)
        for used_file in contain_list:
            print(used_file)
        print("WARNING end")
        return
    upper_result = find_upper_functions(curr_func_name, contain_list)
    for item in upper_result[1]:
        if not terminal_contains(terminals, item):
            terminals.append(item)
    for upper_func in upper_result[0]:
        if not upper_func in parsed_funcs:
            parsed_funcs.add(upper_func)
            extract_call_path_for_func_name(upper_func, terminals, call_paths, parsed_funcs)

def terminal_contains(terminals, item):
    for existed in terminals:
        if item[0] == existed[0] and item[1] == existed[1]:
            return True
    return False

def find_upper_functions(function_name, contain_list):
    terminal_segment = []
    result_list = []
    for file in contain_list:
        function_names_in_tags = []
        tag_f = open(linux_folder + "/tags")
        for line in tag_f.readlines():
            items = line.split("\t")
            relatve_path_from_root = linux_folder + items[1][1:]
            if(relatve_path_from_root == file):
                if(items[0].find("SYSCALL_DEFINE") != -1): 
                    # print(items[2][2:-4])
                    function_names_in_tags.append(items[2][2:-4])
                else:
                    function_names_in_tags.append(items[0])
        tag_f.close()

        funcname2linerange_in_file = {}
        for tag_func in function_names_in_tags:
            linerange = efb.extract_func_definition_linerange_linux_path(tag_func, linux_folder)
            funcname2linerange_in_file[tag_func] = linerange
        
        f = open(file)
        linenum = 0
        contain_lines = []
        is_in_comment = False
        for line in f.readlines():
            linenum += 1
            if is_single_line_comment(line): continue
            if is_comment_start(line):
                is_in_comment = True
            if is_comment_end(line):
                if not is_in_comment:
                    print(line + ", " + file)
                    assert(False)
                is_in_comment = False
            if is_in_comment: continue
            if line.find(function_name + "(") != -1:
                contain_lines.append(linenum)
        f.close()

        for cl in contain_lines:
            for pair in funcname2linerange_in_file.items():
                if cl >= pair[1][0] and cl <= pair[1][1]:
                    if pair[0].find("SYSCALL_DEFINE")!= -1:
                        terminal_segment.append((file, pair[1]))
                    else:
                        result_list.append(pair[0])
    # debug output
    # print("calling functions: ")
    # for item in result_list:
    #     print(item)
    # print("terminal ranges: ")
    # for item in terminal_segment:
    #     print(item[0] + " : [" + str(item[1][0]) + ", " + str(item[1][1]) +  "]")
    return (result_list, terminal_segment)

def extract_relative_functions_map(target_func_name):
    terminals = []
    curr_level = 0
    func_rank_map = dict()
    extract_relative_functions_map_rec(target_func_name, curr_level, terminals, func_rank_map)
    print("func_rank_map for target function: " + target_func_name)
    for item in func_rank_map:
        print(item, func_rank_map[item])
    return func_rank_map


def extract_relative_functions_map_rec(target_func_name, curr_level, terminals, func_rank_map):
    # give a importance ranking for the relative function in 5 steps of func_name
    # resulting a map where the map item is:
    # functionName, ranking in [1,5] identify the minimum steps need to go to target function
    if curr_level > 6:
        return
    print("function name: " + target_func_name)
    if file_list == []:
        listdir_recur(linux_folder + "/linux_new", file_list)
    contain_list = []
    for item in file_list:
        f = open(item)
        for line in f.readlines():
            if line.find(target_func_name + "(") != -1:
                contain_list.append(item)
                break
        f.close()

    if len(set(contain_list)) > 10:
        print("WARNING many upper func_name used: " + target_func_name)
        for used_file in contain_list:
            print(used_file)
        print("WARNING end")
        return
    upper_result = find_upper_functions(target_func_name, contain_list)
    for item in upper_result[1]:
        if not terminal_contains(terminals, item):
            terminals.append(item)
    for upper_func in upper_result[0]:
        if not upper_func in func_rank_map:
            func_rank_map[upper_func] = curr_level
            extract_relative_functions_map_rec(upper_func,  curr_level+1, terminals, func_rank_map)
        else:
            continue

def is_single_line_comment(line):
    striped_line = str.strip(line).strip("\n").strip("\t")
    if "//" == striped_line[:2] or "/*" == striped_line[:2] and "*/" == striped_line[-2:]:
        return True
    else:
        return False
def is_comment_start(line):
    striped_line = str.strip(line).strip("\n").strip("\t")
    if striped_line.find("/*") != -1 and striped_line.find("*/") == -1:
        return True
    else:
        return False
def is_comment_end(line):
    striped_line = str.strip(line).strip("\n").strip("\t")
    if "*/" == striped_line[-2:] and striped_line.find("/*") == -1:
        return True
    else:
        return False

def extract_call_path_str_for_func_name(function_name):
    terminals = []
    parsed_funcs = set()
    parsed_funcs.add(function_name)
    call_paths = ""
    extract_call_path_for_func_name(function_name, terminals, call_paths, parsed_funcs)
    print("Found syscall entrance ------- ")
    for item in terminals:
        print(item[0] + " : [" + str(item[1][0]) + ", " + str(item[1][1]) +  "]")
    print("Analyzed functions ------- ")
    for item in parsed_funcs:
        print(item)
    print("-------")
    print("extracting...")
    for term in terminals:
        rel_fp = term[0]
        sel = term[1]
        call_paths += obtain_terminal_source(rel_fp, sel)
    for called_func in parsed_funcs:
        call_paths += efb.extract_func_body_linux_path(called_func, linux_folder)
    return call_paths

def extract_call_path_str_for_func_name_LLVM(function_name, max_depth):
    call_path_list = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    final_result = ""
    try:
        analyzer_build_dir = os.path.join(current_dir, linux_folder, 'llvm_kernel_analysis', 'Analyzer', 'build')
        cmd = [os.path.join(analyzer_build_dir, "main"), function_name, str(max_depth)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"failed with return code {result.returncode}: {result.stderr}")
        with open('pathsFile.txt', 'r') as lines:
            path = []
            for line in lines:
                line = line.strip()
                if line == "#path":
                    if path:
                        call_path_list.append(path)
                        path = []
                else:
                    path.append(line)
            if path:
                call_path_list.append(path) 
        for path in call_path_list:
            for func_name in path:
                final_result += efb.extract_func_body_linux_path(func_name,linux_folder)
        return final_result
    
    finally:
        os.chdir(current_dir)


def obtain_terminal_source(relative_file_path, start_end_list):
    result = ""
    start = start_end_list[0]
    end = start_end_list[1]
    assert(start <= end)
    f = open(relative_file_path)
    curr_line_num = 1
    for line in f.readlines():
        if curr_line_num >= start and curr_line_num <= end:
            result += line
        curr_line_num += 1
        if curr_line_num > end:
            break
    return result
if __name__ == "__main__":
    function_name = sys.argv[1]
    # curr_function_name = function_name
    # terminals = []
    # parsed_funcs = set()
    # parsed_funcs.add(curr_function_name)
    # call_paths = ""
    # extract_call_path_for_func_name(curr_function_name, terminals, call_paths, parsed_funcs)
    result = extract_call_path_str_for_func_name(function_name)
    print(result)




