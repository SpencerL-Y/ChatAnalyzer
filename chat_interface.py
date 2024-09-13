import openai
import os, re
import sys
import tiktoken

sys.path.insert(0, os.path.abspath('/home/clexma/Desktop/fox3/fuzzing/ChatAnalyzer'))
project_root = "/home/clexma/Desktop/fox3/fuzzing/"

import extract_func_body as efb
import function_info_arrange as finfo
import make_syscall_and_relation_file as mkrel
import function_call_graph as fcg
import relation_parser as rel_parser
import extract_function_callpaths as callpath_gen
from openai import OpenAI
import time

global_model = "gpt-4o"
secrete = ""


def num_token_from_string(str):
    encoding = tiktoken.get_encoding('cl100k_base')
    num_token = len(encoding.encode(str))
    return num_token

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
        self.client = OpenAI(
            api_key = secrete,
            base_url="https://api.aiproxy.io/v1"
        )

    # reserved for latter if key for openai can be obtained, currently we are using the aiproxy
    # aiproxy is not free
    def set_up_default_configs(self):
        self.client = OpenAI(
            api_key = secrete,
            base_url="https://api.aiproxy.io/v1"
        )

    def ask_question_and_record(self, content):
        self.msg_list.append({"role": "user", "content": content})
        res = self.client.chat.completions.create(
            model=global_model,
            messages=[{"role": "user", "content": content}]
        )
        answer = res.choices[0].message
        self.msg_list.append(answer)
        return answer
    
    def ask_for_fcg_setting_configuration(self):
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

    def ask_for_fcg_setting_configuration_with_more_detail(self):
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

    def ask_for_function_callgraph_with_body(self, funcname, linux_path):
        description = "Based on your knowledge on linux kernel, what functions in linux kernel could reach the following function: \n"
        function_body = efb.extract_func_body_linux_path(funcname, linux_path)
        path_source_code_file = open( project_root + "path_source_code.txt", "a+")
        path_source_code_file.write(function_body)
        description += function_body
        description  += "Generate a list of functions that can reach the above function in the following format: \n[func1, func2, func3, ....]\n the expected output is the above format with NO descriptions"
        answer = self.ask_question_and_record(description)
        print(answer)
        return answer
    
    def ask_for_syscalls_can_reach_functions(self, funcname):
        description = "Based on your knowledge on linux kernel and the following provided related function calling source code, what syscall may reach the following function: \n"
        description += funcname + "\n"
        # call_paths = callpath_gen.extract_call_path_str_for_func_name(funcname)
        call_paths = callpath_gen.extract_call_path_str_for_func_name_LLVM(funcname, 5)
        # print(call_paths)

        token_num = num_token_from_string(call_paths)
        if token_num > 25000:
            self.too_long = True
        else:
            self.too_long = False
        
        path_source_code_file = open("./path_source_code.txt", "a+")
        path_source_code_file.write(call_paths)
        path_source_code_file.close()
        description += call_paths
        description += "Generate a list of syscalls that can reach the function in the following format: \n[syscall1, syscall2, syscall3, ...]\n, the expected output is the above format with NO descriptions, for example one possible  example output is: [read, write, mmap]"
        # print("prompt: " + description)
        answer = self.ask_question_and_record(description)
        # print(answer.content)
        return answer.content
    
    def ask_for_syscalls_to_improve(self, target_function_list):
        description = "The following source code is the relation function calling source code for out target functions in linux kernel: "
        for func_name in target_function_list:
            description += func_name + ","
        description += "\n"
        path_source_code_file = open("./path_source_code.txt", "r")
        call_path_source_code = path_source_code_file.read()
        path_source_code_file.close()
        description += call_path_source_code
        description += "\n"
        description += "During the running fuzzing testing process of linux kernel, we have found the following system call programs can trigger the functions that can reach the some of the target functions: \n"
        close_cov_prog_source_code_file = open("./close_cov_prog_source_code.txt", "r")
        syscall_cov_info = close_cov_prog_source_code_file.read()
        close_cov_prog_source_code_file.close()
        description += syscall_cov_info
        description += "\n"
        description += "Generate a list of system calls that can increase the probability of generating such system calls, the fuzzing process will have higher chance to reach our target functions. Give the list of system calls in the following format: \n[syscall1, syscall2, syscall3, ...]\n, the expected output is the above format with NO descriptions, for example one possible  example output is: [read, write, mmap]\n"
        ask_records_file = open(project_root + "ChatAnalyzer/ask_records.txt", "a+")
        ask_records_file.write(description)
        ask_records_file.close()
        answer = self.ask_question_and_record(description)
        print(answer.content)
        return answer.content
        

    
    def ask_simple_relation_setting_syscall_relation(self, content):
        ask_str = content
        simple_list = []
        description = "In the following you will give the analysis result of a problem: whether the linux syscall [syscall name 1] influence the execution flow of [syscall name 2]\
            if they appear in some sequence of system calls and [system call name 1] is before [system call name 2] in the sequence\n\
            the input of user is ([syscall name 1], [syscall name 2]) and you will answer in the format:\n\
            SYSCALL_PAIR: (syscall_name1, syscall_name2)\n\
            RESULT: YES/NO\n\
            REASON: your analysis\n"
        simple_list.append({"role": "user", "content": description})
        simple_list.append({"role": "user", "content": ask_str})
        res = self.client.chat.completions.create(
            model=global_model,
            messages=simple_list
        )
        answer = res.choices[0].message
        self.msg_list.append(answer)
        print(answer)
        return answer.content

    def ask_analyze_function(self, content):
        ask_str = "analyze this function: \n" + content
        self.msg_list.append({"role": "user", "content": ask_str})
        res = openai.chat.completions.create(
            model=global_model,
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
        res = self.client.chat.completions.create(
            model = global_model,
            messages=self.msg_list
        )
        answer = res.choices[0].message
        self.msg_list.append(answer)
        print(answer)
        return answer.content



def get_entry_functions():
    f = open(os.path.join(project_root, "./original_syscall_definitions.txt"))
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
    f = open(os.path.join(project_root,"./small_syscalls_test.txt"))
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

def construct_func_call_graph_for_syscalls(interface, syscall_set, max_depth):
    is_init = False
    curr_depth = 0
    curr_call_graph = fcg.Func_call_graph([])
    for s in syscall_set:
        analyze_syscall_no_history(interface, s, curr_call_graph, curr_depth, max_depth, is_init)
    return curr_call_graph


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

def analyze_syscall_no_history(interface, func_str, curr_call_graph, curr_depth, max_depth, is_init):
    if is_init:
        syscall_bodies = [] 
        is_init = False
        curr_call_graph = fcg.Func_call_graph(syscall_bodies)
    if curr_depth == max_depth:
        return
    
    print(" ======== analyzing function ========= \n " + func_str)
    print(" ======== ========\n")
    curr_call_graph.add_func_node(func_str)
    content = func_str
    answer = interface.ask_analyze_function(content)
    lined_answer = answer.content.splitlines()
    func_info = finfo.get_func_ds(lined_answer)
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
        curr_call_graph.add_func_node(func_body)
        curr_call_graph.add_func_call_edge(func_str, func_body)
    for b in funcs_called_str:
        analyze_syscall_no_history(interface, b, curr_call_graph, curr_depth + 1, max_depth, is_init)        
    return

def old_main():

    version1 = False
    version2 = False
    version3 = False
    extract_call_path_for_target_function_and_ask_entries = True
    extract_function = False
    compute_relative_distance = False
    interface = chat_interface()
    interface.set_up_aiproxy_configs()
    if compute_relative_distance:
        function_name = sys.argv[1]
        callpath_gen.extract_relative_functions_map(function_name)
    if extract_call_path_for_target_function_and_ask_entries:
        function_name = sys.argv[1]
        function_list = [
            #"stable_page_flags", 
            # "fscontext_create_fd", "memfd_fcntl", "vmap_pages_range", "__sys_setfsgid", "sock_free_inode"
            function_name
        ]
        i = 1
        function_name = sys.argv[1]
        for name in function_list:
            result = ""
            time_start = time.time()
            result += str(i) + " syscall analysis for " + name + " : ----------------------------\n"
            llm_list_result = interface.ask_for_syscalls_can_reach_functions(name)
            result += llm_list_result
            # print("RESULT: ")
            # print(result)
            time_end = time.time()
            # print("TIME CONSUMED: " + str(time_end - time_start))


            # llm result sanitizing
            llm_list_result = llm_list_result.strip()
            assert(llm_list_result[0] == "[" and llm_list_result[-1] == "]")
            unwrap = llm_list_result[1:-1]
            unwrap_list = unwrap.split(",")
            content_file = open("./syz_comm_content.txt", "a+")
            for item in unwrap_list:
                print(item.strip())
                content_file.write(item.strip() + "\n")   

            content_file.close() 
            signal_file = open("./syz_comm_sig.txt", "w")
            signal_file.write("1")
            signal_file.close()
            # output the result to syz_comm_content and set syz_comm_sig

    if extract_function:
        # add function body by function_name list here?
        result = efb.extract_function_body(sys.argv[1])
        print(result)

    if version1 or version2:
        interface.ask_for_fcg_setting_configuration()


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
    if version1:
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
    elif version2:
        analyzing_depth = sys.argv[1]
        entries = get_test_entry_functions()
        cg = construct_func_call_graph_for_syscalls(interface, entries, int(analyzing_depth))
        cg.print_graph()
    elif version3:
        all_syscall_names = ["read", "write", "open", "close", "stat", "poll", "lseek", "mmap", "ioctl"]
        all_syscall_names_trial = ["read", "write"]
        relation_pairs = []
        for syscall1 in all_syscall_names:
            for syscall2 in all_syscall_names:
                answer = interface.ask_simple_relation_setting_syscall_relation("(" + syscall1 + ", " + syscall2 + ")")
                parse_result = rel_parser.parse(answer)
                if parse_result[0]:
                    relation_pairs.append(parse_result[1:3])
        
        mkrel.make_disabled_syscall_file(all_syscall_names)
        for p in relation_pairs:
            print(p)
            mkrel.add_simple_syscall_relation_entries(p[0], p[1])


def generate_close_function(funcname, close_steps):
    analyzer_bin_path = project_root + "linuxRepo/llvm_kernel_analysis/Analyzer/build/"
    cmd = analyzer_bin_path + "main close " + funcname + " " + str(close_steps) 
    os.system(cmd)



if __name__ == "__main__":
    running_mode = sys.argv[1]
    interface = chat_interface()
    interface.set_up_aiproxy_configs()
    if running_mode == "init":
        function_name = sys.argv[2]
        function_list = [
            #"stable_page_flags", 
            # "fscontext_create_fd", "memfd_fcntl", "vmap_pages_range", "__sys_setfsgid", "sock_free_inode"
            function_name
        ]
        i = 1
        for name in function_list:
            result = ""
            time_start = time.time()
            result += str(i) + " syscall analysis for " + name + " : ----------------------------\n"
            llm_list_result = interface.ask_for_syscalls_can_reach_functions(name)
            result += llm_list_result
            print(result)
            time_end = time.time()
            # print("TIME CONSUMED: " + str(time_end - time_start))

            # limit test
            if interface.too_long:
                print("Source code too long: HALT!!")

            # llm result sanitizing
            llm_list_result = llm_list_result.strip()
            assert(llm_list_result[0] == "[" and llm_list_result[-1] == "]")
            unwrap = llm_list_result[1:-1]
            unwrap_list = unwrap.split(",")
            content_file = open("./syz_comm_content.txt", "a+")
            for item in unwrap_list:
                print(item.strip())
                content_file.write(item.strip() + "\n")   

            content_file.close() 
        signal_file = open("./syz_comm_sig.txt", "w")
        signal_file.write("1")
        signal_file.close()
    elif running_mode == "close":
        function_name = sys.argv[2]
        close_steps = sys.argv[3]
        generate_close_function(function_name, close_steps)
    elif running_mode == "close_ask":
        target_function_list = []
        target_function_file_path = project_root + "target_functions.txt"
        target_function_file = open(target_function_file_path, "r")
        for line in target_function_file.readlines():
            stripped_target_function = line.strip().replace("\n", "")
            if stripped_target_function != "":
                target_function_list.append(stripped_target_function)
        llm_list_result = interface.ask_for_syscalls_to_improve(target_function_list)
        llm_list_result = llm_list_result.strip()
        assert(llm_list_result[0] == "[" and llm_list_result[-1] == "]")
        unwrap = llm_list_result[1:-1]
        unwrap_list = unwrap.split(",")
        os.truncate("./syz_comm_content.txt", 0)
        content_file = open("./syz_comm_content.txt", "a+")
        for item in unwrap_list:
            syscall = item.strip()
            content_file.write(syscall + "\n")
        signal_file = open("./syz_comm_sig.txt", "w")
        signal_file.write("1")
        signal_file.close()


    else:
        print("ERROR: running mode not supported, expect init or close_addr")
        