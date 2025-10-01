'''
An Assembler for the Hack Machine Language

Read  : xxx.asm from command line argument
Output: xxx.hack
'''

'''
### Strategy

## First Pass
# Compute Labels : (XXX), put them in the symbol table

## Second Pass

## Whitespace and Comments
# if empty skip; if starts with '/' skip; split white spaces and get the first string

## Replacing Variables
# @[variable]; if variable in table, variable = value; else put it in the symbol table

## Parsing Commands
# A-Command : @[value]
# C-Command : [dest] = [comp] ; [jump] 
#             comp always exist
#             dest exist if there is '='
#             jump exist if there is ';'
'''

### Tables
symbol = {
    "R0"     : "0",
    "R1"     : "1",
    "R2"     : "2",
    "R3"     : "3",
    "R4"     : "4",
    "R5"     : "5",
    "R6"     : "6",
    "R7"     : "7",
    "R8"     : "8",
    "R9"     : "9",
    "R10"    : "10",
    "R11"    : "11",
    "R12"    : "12",
    "R13"    : "13",
    "R14"    : "14",
    "R15"    : "15",
    "SCREEN" : "16384",
    "KBD"    : "24576",
    "SP"     : "0",
    "LCL"    : "1",
    "ARG"    : "2",
    "THIS"   : "3",
    "THAT"   : "4"
}

comp = {
    "0"   : "0101010",
    "1"   : "0111111",
    "-1"  : "0111010",
    "D"   : "0001100",
    "A"   : "0110000",
    "!D"  : "0001101",
    "!A"  : "0110001",
    "-D"  : "0001111",
    "-A"  : "0110011",
    "D+1" : "0011111",
    "A+1" : "0110111",
    "D-1" : "0001110",
    "A-1" : "0110010",
    "D+A" : "0000010",
    "D-A" : "0010011",
    "A-D" : "0000111",
    "D&A" : "0000000",
    "D|A" : "0010101",
    "M"   : "1110000",
    "!M"  : "1110001",
    "-M"  : "1110011",
    "M+1" : "1110111",
    "M-1" : "1110010",
    "D+M" : "1000010",
    "D-M" : "1010011",
    "M-D" : "1000111",
    "D&M" : "1000000",
    "D|M" : "1010101"
}

dest = {
    "M"   : "001",
    "D"   : "010",
    "MD"  : "011",
    "A"   : "100",
    "AM"  : "101",
    "AD"  : "110",
    "AMD" : "111"
}

jump = {
    "JGT" : "001",
    "JEQ" : "010",
    "JGE" : "011",
    "JLT" : "100",
    "JNE" : "101",
    "JLE" : "110",
    "JMP" : "111"
}

free_symbol_slot = 16

import sys

# Translates each field into corresponding binary values
# Also translates numbers into its binary form
def translate(symbols):
    return 0

# Parses A and C Commands
def parser(value):
    symbols = {}

    if "@" in value:
        symbols["@"] = value.split("@")[1]
    elif "=" in value and ";" in value:
        seperated_equal = value.split("=")
        seperated_comma = seperated_equal[1].split(";")
        symbols["comp"] = seperated_comma[0]
        symbols["jump"] = seperated_comma[1]
        symbols["dest"] = seperated_equal[0]
    elif "=" in value:
        seperated = value.split("=")
        symbols["comp"] = seperated[1]
        symbols["dest"] = seperated[0]
    elif ";" in value:
        seperated = value.split(";")
        symbols["comp"] = seperated[0]
        symbols["jump"] = seperated[1]
    else:
        symbols["comp"] = value

    return symbols

if __name__=="__main__":
    file = open(sys.argv[1], "r")
    lines = file.readlines()
    assembly_with_labels = []
    assembly = []
    binary_code = []

    # Remove Whitespace and Comments
    for line in lines:
        if line[0] != "\n" and line[0] != "/":
            command = line.split()[0]
            assembly_with_labels.append(command)

    # Remove Labels
    line_count = 0
    for index, line in enumerate(assembly_with_labels):
        if line[0] == "(":
            line = line.replace("(", "").replace(")", "")
            if line not in symbol:
                symbol[line] = line_count
        else:
            assembly.append(line)
            line_count += 1
    
    # Replace variables and labels
    for index, line in enumerate(assembly):
        if line[0] == "@":
            number = 0
            variable = line.split("@")[1]
            if not variable.isdigit():
                if variable in symbol:
                    number = symbol[variable]
                else :
                    symbol[variable] = free_symbol_slot
                    number = free_symbol_slot
                    free_symbol_slot += 1
                assembly[index] = f"@{number}"

    # Translates into binary
    for line in assembly:
        symbols = parser(line)
        binary = translate(symbols)
        binary_code.append(binary)

    print(assembly)

    file.close()
