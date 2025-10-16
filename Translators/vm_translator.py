'''
Translates Stack Machine Language to Assembly

Input  : ***.vm || Directory with ***.vm files
Output : ***.asm
'''

counter = 0
current_function = ""
filename = ""

instruction = {
    "pop"      : lambda line: pop_code(line),
    "push"     : lambda line: push_code(line),
    "label"    : lambda line: label_code(line),
    "goto"     : lambda line: goto_code(line),
    "if-goto"  : lambda line: if_goto_code(line),
    "function" : lambda line: function_code(line),
    "call"     : lambda line: call_code(line),
    "return"   : lambda line: return_code(line),
    "add"      : lambda line: basic_code(line,"M=D+M"),
    "sub"      : lambda line: basic_code(line,"M=M-D"),
    "neg"      : lambda line: basic_code(line,"M=-M"),
    "and"      : lambda line: basic_code(line,"M=D&M"),
    "or"       : lambda line: basic_code(line,"M=D|M"),
    "not"      : lambda line: basic_code(line,"M=!M"),
    "eq"       : lambda line: cmp_code(line, "JEQ"),
    "gt"       : lambda line: cmp_code(line,"JGT"),
    "lt"       : lambda line: cmp_code(line,"JLT")
}

segment_dict = {
    "local"    : ["LCL" , "M", "M"],
    "argument" : ["ARG" , "M", "M"],
    "this"     : ["THIS", "M", "M"],
    "that"     : ["THAT", "M", "M"],
    "temp"     : ["5"   , "A", "M"],
    "constant" : ["0"   , "A", "A"]
}

def basic_code(line, arg):
    cmd = line[0]
    code = []
    if cmd == "neg" or cmd == "not":
        code = [ "@SP", "A=M-1" ]
    else :
        code = [ "@SP", "AM=M-1", "D=M", "A=A-1" ]
    code.append(arg)
    return code

def cmp_code(line, arg):
    global counter
    label_true = f"CMP_TRUE_{counter}"
    label_end = f"CMP_END_{counter}"
    counter += 1
    code = [
        "@SP", "AM=M-1", "D=M", "A=A-1", "D=M-D",
        f"@{label_true}", f"D;{arg}",
        "@SP", "A=M-1", "M=0",
        f"@{label_end}", "0;JMP",
        f"({label_true})",
        "@SP", "A=M-1", "M=-1",
        f"({label_end})"
    ]
    return code

def push_code(line):
    global filename
    seg , i = line[1], line[2]
    code = []
    if seg in segment_dict :
        val = segment_dict[seg]
        code = [
            f"@{i}", "D=A",
            f"@{val[0]}", f"A=D+{val[1]}", f"D={val[2]}",
            "@SP", "A=M", "M=D",
            "@SP", "M=M+1"
        ]
    else :
        arg = "THIS" if i == "0" else "THAT"
        val = f"@{filename}.{i}" if seg == "static" else f"@{arg}"
        code = [
            f"{val}", "D=M",
            "@SP", "A=M", "M=D",
            "@SP", "M=M+1"
        ]
    return code

def pop_code(line):
    global filename
    seg, i = line[1], line[2]
    code = []
    if seg in segment_dict:
        val = segment_dict[seg]
        code = [
            f"@{i}", "D=A",
            f"@{val[0]}", f"D=D+{val[1]}",
            "@R13", "M=D",
            "@SP", "AM=M-1", "D=M",
            "@R13", "A=M", "M=D"
        ]
    else :
        arg = "THIS" if i == "0" else "THAT"
        val = f"@{filename}.{i}" if seg == "static" else f"@{arg}"
        code = [
            "@SP", "AM=M-1", "D=M",
            f"{val}", "M=D",
        ]
    return code

def label_code(line):
    global current_function
    label_name= line[1]
    code = [f"({current_function}${label_name})"]
    return code

def goto_code(line):
    global current_function
    label_name = line[1]
    code = [f"@{current_function}${label_name}", "0;JMP"]
    return code

def if_goto_code(line):
    global current_function
    label_name = line[1]
    code = [
        "@SP", "AM=M-1", "D=M",
        f"@{current_function}${label_name}", "D;JNE"
    ]
    return code

def function_code(line):
    global current_function
    i = line[2]
    code = [ f"({current_function})" ]
    push_0 = [ "@SP", "A=M", "M=0", "@SP", "M=M+1" ]
    for _ in range(int(i)):
        code += push_0
    return code

def call_code(line):
    global counter, current_function
    function_name, i = line[1], line[2]
    code = [
        f"@{current_function}$ret.{counter}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@LCL", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@ARG", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@THIS", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@THAT", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",
        "@SP", "D=M", f"@{i}", "D=D-A", "@5", "D=D-A", "@ARG", "M=D",
        "@SP", "D=M", "@LCL", "M=D",
        f"@{function_name}", "0;JMP",
        f"({current_function}$ret.{counter})"
    ]
    counter += 1
    return code

def return_code(line):
    code = [
        "@LCL", "D=M", "@R13", "M=D",
        "@5", "A=D-A", "D=M", "@R14", "M=D",
        "@SP", "A=M-1", "D=M", "@ARG", "A=M", "M=D",
        "@ARG", "D=M+1", "@SP", "M=D",
        "@R13", "AM=M-1", "D=M", "@THAT", "M=D",
        "@R13", "AM=M-1", "D=M", "@THIS", "M=D",
        "@R13", "AM=M-1", "D=M", "@ARG", "M=D",
        "@R13", "AM=M-1", "D=M", "@LCL", "M=D",
        "@R14", "A=M", "0;JMP"
    ]
    return code

def translate_file(in_file):
    global current_function
    code = []
    lines = in_file.readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = line.split()
        if line[0] == "function":
            current_function = line[1]
        if line[0] in instruction:
            code += instruction[line[0]](line)
    return code

import sys
import os

if __name__=="__main__":
    path = sys.argv[1]
    assembly_code = []
    out_file_name = ""

    # If it is a file
    if os.path.isfile(path):
        filename = path[:-3]
        out_file_name =f"{filename}.asm"
        in_file = open(path, "r")
        assembly_code += translate_file(in_file)
        in_file.close()

    # If it is a directory
    else :
        out_file_name = f"{path}.asm"
        assembly_code += ["@256", "D=A", "@SP", "M=D"]
        assembly_code += call_code(["call", "Sys.init", "0"])
        for file in os.listdir(path):
            if file.endswith(".vm"):
                filename = file[:-3]
                in_file_path = os.path.join(path, file)
                in_file = open(in_file_path, "r")
                assembly_code += translate_file(in_file)
                in_file.close()

    # Write to out file
    out_file = open(out_file_name, "w")
    for index, line in enumerate(assembly_code):
        if index == len(assembly_code) - 1:
            out_file.write(line)
        else:
            out_file.write(line + "\n")
    out_file.close()
