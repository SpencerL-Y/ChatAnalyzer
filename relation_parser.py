import os, re

def parse(syscall_pair_result):
    lines = str.split(syscall_pair_result, "\n")
    if(lines[1].find("YES") != -1):
        syscall_pair_strs = str.split(lines[0], ":")
        bracket = syscall_pair_strs[1].strip()
        raw_syscall_pair = bracket.split(",")
        print(bracket)
        first_syscall = raw_syscall_pair[0][1:].strip()
        second_syscall = raw_syscall_pair[1][:-1].strip()
        print("parsed syscall pair: " + first_syscall + " " + second_syscall)
        return (True, first_syscall, second_syscall)
    else:
        return (False, "null", "null")
