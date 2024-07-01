import os, sys
import extract_func_body as efb



def collect_func_names_and_lines(coverage_path):
    funcname2lineset = {}
    funcnames = set()
    os.system("cat " + coverage_path + " | addr2line -f -e ../linux/linux-6.5/vmlinux > coverage2line" + "_" + coverage_path)
    coveraged_lines = "coverage2line" + "_" + coverage_path
    f = open(coveraged_lines)
    all_lines = f.readlines()
    is_name = True
    striped_name = ""
    for line in all_lines:
        if is_name:
            striped_name = line.strip('\n')
            funcnames.add(striped_name)
            if not striped_name in funcname2lineset:
                funcname2lineset[striped_name] = set()
            is_name = False
        else:
            modified_line = line.strip('\n').split(" ")[0]
            funcname2lineset[striped_name].add(modified_line)
            is_name = True        
    return (funcnames, funcname2lineset)

def generate_coverage_mutation_prompt(func_name, path_line_num_set):
    prompt = "Current analyzed linux function is: \n"
    func_body = efb.extract_function_body(func_name)
    prompt += func_body + "\n"
    prompt += "Current covered lines are:\n"
    line_num_list = set()
    file_path = ""
    for line in path_line_num_set:
        file_path = line.split(":")[0]
        striped_line = line.strip('\n')
        splitted_num = int(striped_line.split(":")[1])
        line_num_list.add(splitted_num)
    func_file = open(file_path)
    i = 1
    for line in func_file.readlines():
        if i in line_num_list:
            prompt += line
        i = i + 1
    prompt += "\n"
    prompt += "Generate syscall program in the format that each line is a syscall and its argument to cover the uncovered lines of the above function.\n\
    For example the format of a syscall program is \nread(arg1, arg2, arg3)\nwrite(arg4, arg5, arg6)\n\
    "
    return prompt

if __name__ == "__main__":
    print("")