import os, sys

def get_filename_firstline(function_name):
    f = open("./linux/tags")
    path = os.system("pwd")
    for line in f.readlines():
        items = line.split("\t")
        # print(items)
        if(items[0] == function_name):
            latter = items[2][2:]
            final = latter[:-4]
            print("./linux/" + items[1])
            print(final)
            return ["./linux/" + items[1], final]
        
if __name__ == "__main__":
    get_filename_firstline()