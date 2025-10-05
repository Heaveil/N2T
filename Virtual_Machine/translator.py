'''
Translates Stack Machine Language to Assembly

Read   : ***.vm from command line argument
output : ***.asm
'''

functions = {
    # Arithmetc
    "add" : [
        "@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "M=D+M"
    ],
    "sub" : [
        "@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "M=M-D"
    ],
    "neg" : [
        "@SP",
        "A=M-1",
        "M=-M"
    ],
    # Logical
    "and" : [
        "@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "M=D&M"
    ],
    "or"  : [
        "@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "M=D|M"
    ],
    "not" : [
        "@SP",
        "A=M-1",
        "M=!M"
    ],
    # Comparisons (Require Jump Labels)
    "eq"  : [],
    "gt"  : [],
    "lt"  : []
}

segment_pointer = {
    "local"    : ["LCL" , "M", "M"],
    "argument" : ["ARG" , "M", "M"],
    "this"     : ["THIS", "M", "M"],
    "that"     : ["THAT", "M", "M"],
    "temp"     : ["5"   , "A", "M"],
    "constant" : ["0"   , "A", "A"]
}

def push_instruction(segment, i, file_name):
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
        return code
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
        return code
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
    # out_file = open(f"{file_name}.asm", "w")
    lines = in_file.readlines()
    assembly_code = []

    # Check which instruction
    for line in lines:
        instruction = line.split()
        if instruction[0] in functions:
            assembly_code += functions[instruction[0]]
        elif instruction[0] == "pop":
            assembly_code += pop_instruction(instruction[1], instruction[2], file_name)
        elif instruction[0] == "push":
            assembly_code += push_instruction(instruction[1], instruction[2], file_name)

    # Write to out file
    # for index, line in enumerate(assembly_code):
    #     if index == len(assembly_code) - 1:
    #         out_file.write(line)
    #     else:
    #         out_file.write(line + "\n")

    in_file.close()
    # out_file.close()
