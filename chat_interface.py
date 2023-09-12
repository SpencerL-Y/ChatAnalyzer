import openai
import os, re
import sys
import extract_func_body as efb
import function_info_arrange as finfo


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
        description = "In the following you are going to act like a code analyzer to analyze a function, the output format should be as follows: \
            FUNC_NAME: [Function Name] \
            GLOBAL_VARS: {v1 (type1), v2 (type2)...} \
            FUNC_INTERFACE_VAR: {ifv1 (type1), ifv2 (type2)...} \
            FUNC_CALLED: {func1(arg1, arg2...)...} \
            IMPORTANT_FUNC: {func1, func2...}\
            where \
            \"type\" denote the type of the variable, \
            \"v1, v2, ifv1, arg1\" are the variable names or arguments names and\
            \"func1\" are the names of function called or important function\n\
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
    
    def ask_correlation_analysis(self):
        return



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
    entries = []
    entries.append("SYSCALL_DEFINE6(mmap, unsigned long, addr, unsigned long, len,\
		unsigned long, prot, unsigned long, flags,\
		unsigned long, fd, unsigned long, off)\
{\
	if (offset_in_page(off) != 0)\
		return -EINVAL;\
	return ksys_mmap_pgoff(addr, len, prot, flags, fd, off >> PAGE_SHIFT);\
}")
                   
    analyzing_depth = sys.argv[1]
    analyzing_log = []
    analyzing_result = {}
    for p in entries:
        analyze_syscall(interface, p, analyzing_log, analyzing_result, 0, int(analyzing_depth))


        
    interface.show_conversations()
                