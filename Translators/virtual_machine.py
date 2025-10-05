'''
Translates Stack Machine Language to Assembly

Input  : ***.vm
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

comparisons = {
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

def basic_instruction(command):
    code = []
    if command == "neg" or command == "not":
        code = [
            "@SP",
            "A=M-1"
        ]
    else :
        code = [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1"
        ]
    code.append(basic[command])
    return code

def comparison_instruction(command):
    global counter
    label_true = f"CMP_TRUE_{counter}"
    label_end = f"CMP_END_{counter}"
    counter += 1
    code = [
        "@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "D=M-D",
        f"@{label_true}",
        f"D;{comparisons[command]}",
        "@SP",
        "A=M-1",
        "M=0",
        f"@{label_end}",
        "0;JMP",
        f"({label_true})",
        "@SP",
        "A=M-1",
        "M=-1",
        f"({label_end})"
    ]
    return code

def push_instruction(segment, i, file_name):
    code = []
    if segment in segment_pointer :
        seg = segment_pointer[segment]
        code = [
            f"@{i}",
            "D=A",
            f"@{seg[0]}",
            f"A=D+{seg[1]}",
            f"D={seg[2]}",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ]
    else :
        seg = "THIS" if i == "0" else "THAT"
        line = f"@{file_name}.{i}" if segment == "static" else f"@{seg}"
        code = [
            f"{line}",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ]
    return code

def pop_instruction (segment, i, file_name):
    code = []
    if segment in segment_pointer :
        seg = segment_pointer[segment]
        code = [
            f"@{i}",
            "D=A",
            f"@{seg[0]}",
            f"D=D+{seg[1]}",
            "@R13",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D"
        ]
    else :
        seg = "THIS" if i == "0" else "THAT"
        line = f"@{file_name}.{i}" if segment == "static" else f"@{seg}"
        code = [
            "@SP",
            "AM=M-1",
            "D=M",
            f"{line}",
            "M=D",
        ]
    return code

import sys

if __name__=="__main__":
    file_name = f"{sys.argv[1][:-3]}"
    in_file = open(sys.argv[1], "r")
    out_file = open(f"{file_name}.asm", "w")
    lines = in_file.readlines()
    assembly_code = []

    # Check which instruction
    for line in lines:
        instruction = line.split()
        command = instruction[0]
        if command in basic:
            assembly_code += basic_instruction(command)
        elif command in comparisons:
            assembly_code += comparison_instruction(command)
        elif command == "pop":
            assembly_code += pop_instruction(instruction[1], instruction[2], file_name)
        elif command == "push":
            assembly_code += push_instruction(instruction[1], instruction[2], file_name)

    # Write to out file
    for index, line in enumerate(assembly_code):
        if index == len(assembly_code) - 1:
            out_file.write(line)
        else:
            out_file.write(line + "\n")

    in_file.close()
    out_file.close()
