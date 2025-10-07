'''
Translates Stack Machine Language to Assembly

Input  : ***.vm || Directory with ***.vm files
Output : ***.asm
'''

basic = {
    "add" : "M=D+M",
    "sub" : "M=M-D",
    "neg" : "M=-M",
    "and" : "M=D&M",
    "or"  : "M=D|M",
    "not" : "M=!M"
}

cmp = {
    "eq": "JEQ",
    "gt": "JGT",
    "lt": "JLT"
}

segment_pointer = {
    "local"    : ["LCL" , "M", "M"],
    "argument" : ["ARG" , "M", "M"],
    "this"     : ["THIS", "M", "M"],
    "that"     : ["THAT", "M", "M"],
    "temp"     : ["5"   , "A", "M"],
    "constant" : ["0"   , "A", "A"]
}

counter = 0

def basic_code(cmd):
    code = []
    if cmd == "neg" or cmd == "not":
        code = [ "@SP", "A=M-1" ]
    else :
        code = [ "@SP", "AM=M-1", "D=M", "A=A-1" ]
    code.append(basic[cmd])
    return code

def cmp_code(cmd):
    global counter
    label_true = f"CMP_TRUE_{counter}"
    label_end = f"CMP_END_{counter}"
    counter += 1
    code = [
        "@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D",
        f"@{label_true}", f"D;{cmp[cmd]}",
        "@SP", "A=M-1", "M=0",
        f"@{label_end}", "0;JMP",
        f"({label_true})",
        "@SP", "A=M-1", "M=-1",
        f"({label_end})"
    ]
    return code

def push_code(segment, i, file_name):
    code = []
    if segment in segment_pointer :
        seg = segment_pointer[segment]
        code = [
            f"@{i}", "D=A",
            f"@{seg[0]}", f"A=D+{seg[1]}", f"D={seg[2]}",
            "@SP", "A=M", "M=D",
            "@SP", "M=M+1"
        ]
    else :
        seg = "THIS" if i == "0" else "THAT"
        line = f"@{file_name}.{i}" if segment == "static" else f"@{seg}"
        code = [
            f"{line}", "D=M",
            "@SP", "A=M", "M=D",
            "@SP", "M=M+1"
        ]
    return code

def pop_code(segment, i, file_name):
    code = []
    if segment in segment_pointer :
        seg = segment_pointer[segment]
        code = [
            f"@{i}", "D=A",
            f"@{seg[0]}", f"D=D+{seg[1]}",
            "@R13", "M=D",
            "@SP", "AM=M-1", "D=M",
            "@R13", "A=M", "M=D"
        ]
    else :
        seg = "THIS" if i == "0" else "THAT"
        line = f"@{file_name}.{i}" if segment == "static" else f"@{seg}"
        code = [
            "@SP", "AM=M-1", "D=M",
            f"{line}", "M=D",
        ]
    return code

def label_code(name, function, file_name):
    code = [f"({file_name}.{function}${name})"]
    return code

def goto_code(name, function, file_name):
    code = [f"@{file_name}.{function}${name}", "0;JMP"]
    return code

def if_goto_code(name, function, file_name):
    code = [
        "@SP", "AM=M-1", "D=M",
        f"@{file_name}.{function}${name}", "D;JNE"
    ]
    return code

def function_code(name, i, file_name):
    code = [ f"({file_name}.{name})" ]
    push_0 = [ "@SP", "A=M", "M=0", "@SP", "M=M+1" ]
    for _ in range(int(i)):
        code += push_0
    return code

def call_code(name, i, function, file_name):
    global counter
    code = [
        f"@{file_name}.{function}$ret.{counter}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@LCL", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@ARG", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@THIS", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@THAT", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@SP", "D=M", f"@{i}", "D=D-A", "@5", "D=D-A", "@ARG", "M=D",
        "@SP", "D=M", "@LCL", "M=D",
        f"@{name}", "0;JMP",
        f"({file_name}.{function}$ret.{counter})"
    ]
    counter += 1
    return code

def return_code():
    code = [
        "@LCL", "D=M", "@R13", "M=D",
        "@SP", "A=M-1","D=M", "@ARG", "A=M", "M=D",
        "@ARG", "D=M", "@SP", "M=D+1",
        "@R13", "AM=M-1", "D=M", "@THAT", "M=D",
        "@R13", "AM=M-1", "D=M", "@THIS", "M=D",
        "@R13", "AM=M-1", "D=M", "@ARG", "M=D",
        "@R13", "AM=M-1", "D=M", "@LCL", "M=D",
        "@R13", "AM=M-1", "D=M", "@R14", "M=D",
        "@R14", "A=M", "0;JMP"
    ]
    return code

def bootstrap_code():
    code = ["@256", "D=A", "@SP", "M=D"]
    code += call_code("Sys.init", "0", "", "Sys")
    return code

def translate_file(in_file, file_name):
    lines = in_file.readlines()
    current_function = ""
    code = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = line.split()
        cmd = line[0]
        match cmd :
            case _ if cmd in basic:
                code += basic_code(cmd)
            case _ if cmd in cmp:
                code += cmp_code(cmd)
            case "pop":
                segment, i = line[1], line[2]
                code += pop_code(segment, i, file_name)
            case "push":
                segment, i = line[1], line[2]
                code += push_code(segment, i, file_name)
            case "label":
                name = line[1]
                code += label_code(name, current_function, file_name)
            case "goto":
                name = line[1]
                code += goto_code(name, current_function, file_name)
            case "if-goto":
                name = line[1]
                code += if_goto_code(name, current_function, file_name)
            case "function":
                name, i = line[1], line[2]
                current_function = name
                code += function_code(name, i, file_name)
            case "call":
                name, i = line[1], line[2]
                code += call_code(name, i, current_function, file_name)
            case "return":
                code += return_code()
    return code

import sys
import os

if __name__=="__main__":
    path = sys.argv[1]
    assembly_code = []
    out_file_name = ""

    # If it is a file
    if os.path.isfile(path):
        in_file = open(path, "r")
        file_name = path[:-3]
        out_file_name =f"{file_name}.asm"
        assembly_code += translate_file(in_file, file_name)
        in_file.close()

    # If it is a directory
    else :
        out_file_name = f"{path}.asm"
        assembly_code += bootstrap_code()
        for file in os.listdir(path):
            if file.endswith(".vm"):
                file_name = file[:-3]
                in_file_path = os.path.join(path, file)
                in_file = open(in_file_path, "r")
                assembly_code += translate_file(in_file, file_name)
                in_file.close()

    # Write to out file
    out_file = open(out_file_name, "w")
    for index, line in enumerate(assembly_code):
        if index == len(assembly_code) - 1:
            out_file.write(line)
        else:
            out_file.write(line + "\n")

    out_file.close()
