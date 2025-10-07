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
    push_0 = [
        "@SP", "A=M", "M=0",
        "@SP", "M=M+1"
    ]
    for _ in range(i):
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
        ## Magic here
        "0;JMP"
    ]
    return code

import sys

if __name__=="__main__":

    # TODO:
    # Add Directory Input
    # Initalize Bootstrap Code

    file_name = f"{sys.argv[1][:-3]}"
    in_file = open(sys.argv[1], "r")
    # out_file = open(f"{file_name}.asm", "w")
    lines = in_file.readlines()
    assembly_code = []
    current_function = ""

    # Check which instruction
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = line.split()
        cmd = line[0]
        match cmd :
            case _ if cmd in basic:
                assembly_code += basic_code(cmd)
            case _ if cmd in cmp:
                assembly_code += cmp_code(cmd)
            case "pop":
                segment, i = line[1], line[2]
                assembly_code += pop_code(segment, i, file_name)
            case "push":
                segment, i = line[1], line[2]
                assembly_code += push_code(segment, i, file_name)
            case "label":
                name = line[1]
                assembly_code += label_code(name, current_function, file_name)
            case "goto":
                name = line[1]
                assembly_code += goto_code(name, current_function, file_name)
            case "if-goto":
                name = line[1]
                assembly_code += if_goto_code(name, current_function, file_name)
            case "function":
                name, i = line[1], line[2]
                current_function = name
                assembly_code += function_code(name, i, file_name)
            case "call":
                name, i = line[1], line[2]
                assembly_code += call_code(name, i, current_function, file_name)
            case "return":
                assembly_code += return_code()

    for line in assembly_code:
        print(line)

    # Write to out file
    # for index, line in enumerate(assembly_code):
    #     if index == len(assembly_code) - 1:
    #         out_file.write(line)
    #     else:
    #         out_file.write(line + "\n")

    in_file.close()
    # out_file.close()
