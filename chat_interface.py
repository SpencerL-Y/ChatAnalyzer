import openai
import os, re
import sys
import extract_func_body as efb
import function_info_arrange as finfo
import make_syscall_and_relation_file as mkrel


# chat interface 
class chat_interface:
    def __init__(self) -> None:
        self.msg_list = []

    def show_conversations(self):
        print("------------------------------------- conversations")
        for msg in self.msg_list:
            if msg['role'] == 'user':
                print("USER ================== BEGIN")
                print(msg['content'])
                print("USER ================== END")
            else:
                print("CHATGPT ================== BEGIN")
                print(msg['content'])
                print("CHATGPT ================== END")
        print("------------------------------------- conversations end")
    

    def set_up_aiproxy_configs(self):
        openai.api_key = "sk-5nga6ZRm5D87QSytGYlw9jIhItjhnPqxeUoUfRuAJAam87zt"
        openai.api_base = "https://api.aiproxy.io/v1"

    # reserved for latter if key for openai can be obtained, currently we are using the aiproxy
    # aiproxy is not free
    def set_up_default_configs(self):
        openai.api_key = "sk-5nga6ZRm5D87QSytGYlw9jIhItjhnPqxeUoUfRuAJAam87zt"
        openai.api_base = "https://api.aiproxy.io/v1"


    def ask_question_and_record(self, content):
        self.msg_list.append({"role": "user", "content": content})
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": content}]
        )
        answer = res.choices[0].message
        self.msg_list.append(answer)
        return answer
    
    def ask_for_setting_configuration(self):
        description = "In the following you are going to act like a code analyzer to analyze a function, the output format should be as follows:\n \
            FUNC_NAME: funcname\n \
            GLOBAL_VARS: {v1 (type1), v2 (type2)...}\n \
            FUNC_INTERFACE_VAR: {ifv1 (type1), ifv2 (type2)...}\n \
            FUNC_CALLED: {func1(arg1, arg2...)...}\n \
            IMPORTANT_FUNC: {func1, func2...}\n\
            where \
            \"funcname\" is the name of analyzed function or the name of first argument when the function is SYSCALL_DEFINE\
            \"type\" denote the type of the variable, \
            \"v1, v2, ifv1, arg1\" are the variable names or arguments names and\
            \"func1\" are the names of function called or important function\n\
            FUNC_CALLED must have arguments\n.\
            Please generate only this format with no descriptive statements\n\
            If FUNC_NAME is SYSCALL_DEFINE*, use the name of the first argument as FUNC_NAME\n"
        self.ask_question_and_record(description)

    def ask_for_setting_configuration_with_more_detail(self):
        description = "In the following you are going to act like a code analyzer to analyze a function, the output format should be as follows:\n \
            FUNC_NAME: funcname\n \
            GLOBAL_VARS_USED: {v1 (type1), v2 (type2)...}\n \
            GLOBAL_VARS_CHANGED: {v1 (type1), v2 (type2) ...}\
            FUNC_INTERFACE_VAR: {ifv1 (type1), ifv2 (type2)...}\n \
            FUNC_CALLED: {func1(arg1, arg2...)...}\n \
            IMPORTANT_FUNC: {func1, func2...}\n\
            where \
            \"funcname\" is the name of analyzed function or the name of first argument when the function is SYSCALL_DEFINE\
            \"type\" denote the type of the variable, \
            \"v1, v2, ifv1, arg1\" are the variable names or arguments names and\
            \"func1\" are the names of function called or important function\n\
            FUNC_CALLED must have arguments\n.\
            GLOBAL_VARS_USED stores the global vars in linux source code that are used within this function\n\
            GLOBAL_VARS_CHANGED stores the global vars in linux source code that are modified within this function\n\
            Please generate only this format with no descriptive statements\n\
            If FUNC_NAME is SYSCALL_DEFINE*, use the name of the first argument as FUNC_NAME\n"
        self.ask_question_and_record(description)

    def ask_analyze_function(self, content):
        ask_str = "analyze this function: \n" + content
        self.msg_list.append({"role": "user", "content": ask_str})
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.msg_list
        )
        answer = res.choices[0].message
        self.msg_list.append(answer)
        return answer
    
    def ask_relation_analysis(self):
        description = "Based on the analysis above, now you are going to construct a table where rows and columns are the syscalls (the first argument of SYSCALL_DEFINE) you analyzed\n\
            The table represent the relation between any two syscall where each entry is an integer ranged between 0 to 100\n\
            0 represents these two syscalls have no relation, and 100 represent the first syscall influeces the second strongly\n\
            the influece in defined by considering following factors: 1. the returned value of the first syscall has the same type\
            of the some argument in the second syscall. 2. in the procedure of the first syscall, it changes some global variables that may influece the executing procedure of the second syscall.\n\
            Please generate the table in a formatted table in the following format with descriptive statements:\
            Use the format:\n\
            SYSCALLS: [syscall_name1], [syscall_name2] ....\n\
            TABLE_ENTRIES: \n\
            (i, j)\n\
            where SYSCALLS denote the sequence of syscalls considered, and [syscall_name1] denote the name of a syscall\n\
            TABLE_ENTRIES list table entries where the existence of (i,j) means [syscall_namei] influence [syscall_namej] with some specific arguments, we require that i is inequal to j and if (i, j) is an entry then (j, i) should not appear in the entries. If the influencial relation is not sure, do not add the entry.\n\
            please only generate the format with no descriptive text\n\
        "
        self.msg_list.append({"role": "user", "content": description})
        res = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=self.msg_list
        )
        answer = res.choices[0].message
        self.msg_list.append(answer)
        print(answer)
        return answer.content



def get_entry_functions():
    f = open("./original_syscall_definitions.txt")
    lines = f.readlines()
    result = []
    curr_func = ""
    for line in lines:
        if line == "===\n":
            result.append(curr_func)
            curr_func = ""
        else:
            curr_func += line
    print("original syscall result:")
    return result

def get_test_entry_functions():
    f = open("./small_syscalls_test.txt")
    lines = f.readlines()
    result = []
    curr_func = ""
    for line in lines:
        if line == "===\n":
            result.append(curr_func)
            curr_func = ""
        else:
            curr_func += line
    print("original syscall result:")
    return result


def analyze_syscall(interface, func_str, analyzing_log, analyzing_result, curr_depth, max_depth):
    print(" ======== analyzing function ========= \n " + func_str)
    print(" ======== ========\n")
    if curr_depth == max_depth:
        return
    content = func_str
    answer = interface.ask_analyze_function(content)
    analyzing_log.append({"role" : "user", "content" : content})
    analyzing_log.append({"role" : "assistant", "content" : answer})
    print(" ======== answer ========= ") 
    print(answer.content)
    print(" ======== ========")
    lined_answer = answer.content.splitlines()
    func_info = finfo.get_func_ds(lined_answer)
    analyzing_result[func_info.func_name] = func_info
    funcs_ds_called = func_info.extract_func_called()
    funcs_called = []
    for f in funcs_ds_called:
        funcs_called.append(f.func_name)
    funcs_called_str = []
    for f in funcs_called:
        func_body = efb.extract_function_body(f)
        if func_body == "NOT FOUND":
            continue
        funcs_called_str.append(func_body)
    for b in funcs_called_str:
        analyze_syscall(interface, b, analyzing_log, analyzing_result, curr_depth + 1, max_depth)        

if __name__ == '__main__':
    print("main")
    interface = chat_interface()
    interface.set_up_aiproxy_configs()
    interface.ask_for_setting_configuration()


    # entries = get_entry_functions()
#     entries = []
#     entries.append("SYSCALL_DEFINE6(mmap, unsigned long, addr, unsigned long, len,\
# 		unsigned long, prot, unsigned long, flags,\
# 		unsigned long, fd, unsigned long, off)\
# {\
# 	if (offset_in_page(off) != 0)\
# 		return -EINVAL;\
# 	return ksys_mmap_pgoff(addr, len, prot, flags, fd, off >> PAGE_SHIFT);\
# }")
    entries = get_test_entry_functions()
                   
    analyzing_depth = sys.argv[1]
    analyzing_log = []
    analyzing_result = {}
    for p in entries:
        analyze_syscall(interface, p, analyzing_log, analyzing_result, 0, int(analyzing_depth))

    relation_result = interface.ask_relation_analysis()
    print("relation_result: " + relation_result)
    mkrel.make_syscall_relation_file(relation_result)
    interface.show_conversations()
                