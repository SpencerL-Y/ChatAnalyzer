import os, sys

def get_filename_firstline(function_name):
    return get_funcname_firstline_linux_folder(function_name, "./linux")

def get_funcname_firstline_linux_folder(function_name, linux_folder):
    f = open( linux_folder + "/tags")
    # path = os.system("pwd")
    for line in f.readlines():
        items = line.split("\t")
        # print(items)
        if items[0] == function_name or items[0].find("SYSCALL_DEFINE") != -1 and items[2].find(function_name) != -1:
            latter = items[2][2:]
            final = latter[:-4]
            # print(linux_folder + items[1][1:])
            # print(final)
            return [linux_folder + items[1][0:], final]
    return ["NOT FOUND", "NOT_FOUND"]

def get_funcname_firstline_linux_folder_analyze(function_name, linux_folder):
    f = open( linux_folder + "/analyze_tags")
    # path = os.system("pwd")
    for line in f.readlines():
        items = line.split("\t")
        # print(items)
        if items[0] == function_name or items[0].find("SYSCALL_DEFINE") != -1 and items[2].find(function_name) != -1:
            latter = items[2][2:]
            final = latter[:-4]
            # print(linux_folder + items[1][1:])
            # print(final)
            return [linux_folder + items[1][0:], final]
    return ["NOT FOUND", "NOT_FOUND"]
    
if __name__ == "__main__":
    get_filename_firstline()