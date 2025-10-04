'''
Translates Stack Machine Language to Assembly

Read   : ***.vm from command line argument
output : ***.asm
'''

arithmetic = {
    "add" : [],
    "sub" : [],
    "neg" : [],
    "eq"  : [],
    "gt"  : [],
    "lt"  : [],
    "and" : [],
    "or"  : [],
    "not" : []
}

segment_pointer = {
    "local"    : "LCL",
    "argument" : "ARG",
    "this"     : "THIS",
    "that"     : "THAT",
    "constant" : "0",
    "temp"     : "5"
}

def pop_instruction (segment, i):
    assembly_code = []

    if segment in segment_pointer :
        pass

    elif segment == "static":
        pass

    elif segment == "pointer":
        pass

    return assembly_code

def push_instruction(segment, i):
    assembly_code = []

    if segment in segment_pointer :
        pass

    elif segment == "static":
        pass

    elif segment == "pointer":
        pass

    return assembly_code

import sys

if __name__=="__main__":
    out_file_name = f"{sys.argv[1][:-3]}.asm"
    in_file = open(sys.argv[1], "r")
    print(out_file_name)
    lines = in_file.readlines()
    assembly_code = []

    # Check which instruction
    for line in lines:
        instruction = line.split()
        if instruction[0] in arithmetic:
            assembly_code += arithmetic[instruction[0]]
        elif instruction[0] == "pop":
            assembly_code += pop_instruction(instruction[1], instruction[2],)
        elif instruction[0] == "push":
            assembly_code += push_instruction(instruction[1], instruction[2])

    # Write to out file
    # for index, line in enumerate(assembly_code):
    #     if index == len(assembly_code) - 1:
    #         out_file.write(line)
    #     else:
    #         out_file.write(line + "\n")

    in_file.close()
    # out_file.close()
