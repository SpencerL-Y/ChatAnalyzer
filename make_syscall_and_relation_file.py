import os, sys


def make_disabled_syscall_file(exist_syscalls):
    print("exist_syscalls: ")
    print(exist_syscalls)
    enable_f = open("enabled_calls.txt", "w")

    result = []
    f = open("target_syscalls.txt", "r")
    lines = f.readlines()
    for line in lines:
        is_orig = False
        for i in exist_syscalls:
            if i == line[:-1]:
                is_orig = True
                break
        if is_orig:
            enable_f.write(line)
            continue
        line_split = line.split("$")
        is_remain = False
        for i in exist_syscalls:
            if i == line_split[0]:
                is_remain = True
                break
        if not is_remain:
            result.append(line)
        else:
            enable_f.write(line)
    f.close()
    f = open("disabled_calls.txt", "w")
    for line in result:
        f.write(line)
    f.close()
    return result

def make_syscall_relation_file(string):
    table_entries = []
    write_entries = []
    lines = str.split(string, "\n")
    begin_recording_relation = False
    for line in lines:
        if begin_recording_relation:
            print("relation: " + line)
            table_entries.append(line)
        if line.find("SYSCALLS:") != -1:
            syscalls_coarse = line.split(":")[1]
            syscalls_call_names = []
            for name in syscalls_coarse.split(","):
                syscalls_call_names.append(name.strip())
            make_disabled_syscall_file(syscalls_call_names)
        if line == "TABLE_ENTRIES:":
            begin_recording_relation = True
    for l in table_entries:
        splitted_l = l.split(",")
        first_syscall = str.strip(splitted_l[0])[1:]
        second_syscall = str.strip(splitted_l[1])[:-1]
        detailed_entries = construct_call_name_table_str(first_syscall, second_syscall)
        write_entries.extend(detailed_entries)
    f = open("relations.txt", "w")
    for e in write_entries:
        f.write(e)
    
def add_simple_syscall_relation_entries(first_syscall, second_syscall):
    detailed_entries = construct_call_name_table_str(first_syscall, second_syscall)
    f = open("relation.txt", "w+")
    for e in detailed_entries:
        f.write(e)
    f.close()

def construct_call_name_table_str(first_syscall, second_syscall):
    print(first_syscall + " | " + second_syscall)
    result_entries = []
    f = open("enabled_calls.txt", "r")
    lines = f.readlines()
    first_set = []
    second_set = []
    for line in lines:
        print(line[:-1])
        line_split = line[:-1].split("$")
        print("call name: " + line_split[0])
        if len(line_split) == 1:
            if(line_split[0] == first_syscall):
                first_set.append(line[:-1])
            if(line_split[0] == second_syscall):
                second_set.append(line[:-1])
        else:
            if line_split[0] == first_syscall:
                first_set.append(line[:-1])
            elif line_split[0] == second_syscall:
                second_set.append(line[:-1])

    for first_name in first_set:
        for second_name in second_set:
            result_entries.append(first_name + " " + second_name + "\n")
    f.close()
    return result_entries