import openai
import os, re


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
            GLOBAL_VARS: {(v1, type1), (v2, type2)...} \
            FUNC_INTERFACE_VAR: {(ifv1, type1), (ifv2, type2)...} \
            FUNC_CALLED: {func1((arg1, type1), (arg2, type2))...} \
            IMPORTANT_FUNC: {func1((arg1, type1), (arg2, type2))...}\
            where \
            \"type\" denote the type of the variable, \
            \"v1, v2, ifv1, arg1\" are the variable names or arguments names and\
            \"func1\" are the names of function called or important function"
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



if __name__ == '__main__':
    print("main")
    interface = chat_interface()
    interface.set_up_aiproxy_configs()
    interface.ask_for_setting_configuration()
    content = "\
    SYSCALL_DEFINE3(lseek, unsigned int, fd, off_t, offset, unsigned int, whence)\
{\
	return ksys_lseek(fd, offset, whence);\
}\
"
    interface.ask_analyze_function(content)
    interface.show_conversations()
                