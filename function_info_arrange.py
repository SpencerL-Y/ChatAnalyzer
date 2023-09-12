import os, re
#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
class FuncClass():
    def __init__(self, funcName, globalVars, funcInterfaceVar, funcCalled, importantFunc):
        self.func_name = funcName
        self.global_vars = globalVars
        self.func_interface_vars = funcInterfaceVar
        self.func_called = funcCalled
        self.important_func = importantFunc
    
    def get_func_desc(self):
        print("name: " + self.func_name+ " global: " +self.global_vars+" interface: " +self.func_interface_vars+" func_called: "+self.func_called+" important: "+self.important_func)
    def extract_global_vars(self):
        vs = self.global_vars.split(" ")
        print(vs)
        return 
    def extract_interface_vars(self):
        ivs = self.func_interface_vars.split(",")
        result = []
        for s in ivs:
            sp = s.strip()
            res = re.findall(r'\(.*?\)', sp)
            result.append(res[0])
        print(result)
        return result
    def extract_func_called(self):
        print("extrac_func_called")
        funcs = self.func_called.split("),")
        print("funcs_called: ")
        print(funcs)
        striped_funcs = []
        i = 0
        for f in funcs:
            if i < len(funcs) - 1:
                striped_funcs.append(f.strip() + ')')
            else:
                striped_funcs.append(f.strip())
            i = i + 1
        print(striped_funcs)
        all_func_called = []
        for f in striped_funcs:
            name_args = f.split("(")
            func_name = name_args[0]
            args = name_args[1].split(")")
            striped_args = []
            for arg in args:
                striped_args.append(arg.strip())
            striped_args = striped_args[:-1]
            if len(striped_args) > 0:
                splitted_args = [] 
                for a in striped_args[0].split(","):
                    splitted_args.append(a.strip())
            else:
                splitted_args = []
            print("func called: " + func_name)
            print(splitted_args)
            all_func_called.append(FuncCalled(func_name, splitted_args))       
        return all_func_called
    

class FuncCalled():
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args
    def print_func_called(self):
        print("func_name: " + self.func_name + " args: " + self.args)
        
class SyscallNode():
    def __init__(self, interface_argtypes, all_func_called):
        self.interface_args = interface_argtypes
        self.all_func_called = all_func_called


def get_fs_syscall_funclist():
    funcList = []
    funcName = ""
    globalVars = ""
    funcInterfaceVar = ""
    funcCalled = ""
    importantFunc = ""

    f = open("./format.txt", "r", encoding="utf-8")

    lines = f.readlines()

    for line in lines:

        if line[0:6]=="FUNC_N":
            funcName=line[12:-2]
            #print(line[12:-2])
        elif line[0:6]=="GLOBAL":
            globalVars=line[14:-2]
            #print(line[14:-2])
        elif line[0:6]=="FUNC_I":
            funcInterfaceVar=line[21:-2]
            #print(line[21:-2])
        elif line[0:6]=="FUNC_C":   
            funcCalled=line[14:-2]
            #print(line[14:-2])
        elif line[0:6]=="IMPORT":
            #封装
            importantFunc=line[17:-2]
            #print(line[17:-2])
            func = FuncClass(funcName,globalVars,funcInterfaceVar,funcCalled,importantFunc)
            #func.get_funcDescription()
            funcList.append(func)
        else:
            continue

    f.close()
    return funcList

def get_func_ds(lines):
    globalVars = ""
    funcInterfaceVar = ""
    funcCalled = ""
    importantFunc = ""
    for line in lines:

        if line[0:6]=="FUNC_N":
            funcName=line[12:-2]
            #print(line[12:-2])
        elif line[0:6]=="GLOBAL":
            globalVars=line[14:-2]
            #print(line[14:-2])
        elif line[0:6]=="FUNC_I":
            funcInterfaceVar=line[21:-2]
            #print(line[21:-2])
        elif line[0:6]=="FUNC_C":   
            funcCalled=line[14:-2]
            #print(line[14:-2])
        elif line[0:6]=="IMPORT":
            #封装
            importantFunc=line[17:-2]
            #print(line[17:-2])
            func = FuncClass(funcName,globalVars,funcInterfaceVar,funcCalled,importantFunc)
            #func.get_funcDescription()
            return func
        else:
            continue
    assert(False)

if __name__ == "__main__":
    funcList = get_fs_syscall_funclist()
    #test
    for func in funcList:
        print("TOTAL DESCRIPTION:")
        func.get_func_desc()
        print("-----------------------------------")
        print("GLOBAL VARS:")
        func.extract_global_vars()
        print("-----------------------------------")
        print("INTERFACE VARS:")
        func.extract_interface_vars()
        print("-----------------------------------")
        print("FUNC CALLED:")
        func.extract_func_called()
