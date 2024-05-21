import openai
import os, re
import sys
import extract_func_body as efb
import function_info_arrange as finfo
import make_syscall_and_relation_file as mkrel
import function_call_graph as fcg
import relation_parser as rel_parser
from openai import OpenAI

global_model = "gpt-4-turbo-2024-04-09"
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
            api_key = "sk-5nga6ZRm5D87QSytGYlw9jIhItjhnPqxeUoUfRuAJAam87zt",
            base_url="https://api.aiproxy.io/v1"
        )

    # reserved for latter if key for openai can be obtained, currently we are using the aiproxy
    # aiproxy is not free
    def set_up_default_configs(self):
        self.client = OpenAI(
            api_key = "sk-5nga6ZRm5D87QSytGYlw9jIhItjhnPqxeUoUfRuAJAam87zt",
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
        print(function_body)
        description += function_body
        description  += "Generate a list of functions that can reach the above function in the following format: \n[func1, func2, func3, ....]\n the expected output is the above format with NO descriptions"
        answer = self.ask_question_and_record(description)
        print(answer)
        return answer
    
    def ask_for_syscalls_can_reach_functions(self, funcname):
        description = "Based on your knowledge on linux kernel, what syscall variant may reach the following function: \n"
        description += funcname
        description += "Generate a list of functions that can reach the function in the following format: \n[syscall1, syscall2, syscall3, ...]\n, the expected output is the above format with NO descriptions"
        answer = self.ask_question_and_record(description)
        print(answer)
        return answer

        
    
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

if __name__ == '__main__':

    version1 = False
    version2 = False
    version3 = False
    experiment_on_chat_syscall_commit_change_analysis = True
    extract_function = False
    print("main")
    interface = chat_interface()
    interface.set_up_aiproxy_configs()
    function_list = ["stable_page_flags", "fscontext_create_fd", "memfd_fcntl", "vmap_pages_range", "__sys_setfsgid", "sock_free_inode"]
    i = 111111
    if experiment_on_chat_syscall_commit_change_analysis:
        result = ""
        for name in function_list:
            # result += str(i) + " function analysis: ----------------------------\n"
            # print(str(i) + " function analysis: ----------------------------")
            # result += interface.ask_for_function_callgraph_with_body(name, "./linux/").content + "\n"
            result += str(i) + " syscall analysis: ----------------------------\n"
            print(str(i) + " syscall analysis: ----------------------------")
            result += interface.ask_for_syscalls_can_reach_functions(name).content + "\n"
            i += 111111
        print("RESULT: ")
        print(result)

    if extract_function:
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

        