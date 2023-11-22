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
            if not funcname2lineset.has_key(striped_name):
                funcname2lineset[striped_name] = set()
            is_name = False
        else:
            funcname2lineset[striped_name].add(line.strip('\n'))
            is_name = True        
    return (funcnames, funcname2lineset)

def generate_coverage_mutation_prompt(func_name, path_line_num):


if __name__ == "__main__":
