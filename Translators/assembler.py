'''
Translates Assembly to Machine Language

Input  : ***.asm
Output : ***.hack
'''

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
def translate(symbols, comp, dest, jump):
    binary = ""

    if "@" in symbols:
        binary = format(int(symbols["@"]), "016b")
    else:
        comp = comp[symbols["comp"]]
        dest = dest[symbols["dest"]] if "dest" in symbols else "000"
        jump = jump[symbols["jump"]] if "jump" in symbols else "000"
        binary = "111" + comp + dest + jump

    return binary

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
    out_file_name = f"{sys.argv[1][:-4]}.hack"
    in_file = open(sys.argv[1], "r")
    out_file = open(out_file_name, "w")
    lines = in_file.readlines()
    assembly = []
    binary_code = []
    assembly_with_labels = []

    # Remove Whitespace and Comments
    for line in lines:
        if line[0] != "\n" and line[0] != "/":
            command = line.split()[0]
            if command[0] != "/":
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
        binary = translate(symbols, comp, dest, jump)
        binary_code.append(binary)

    # Write to out file
    for index, line in enumerate(binary_code):
        if index == len(binary_code) - 1:
            out_file.write(line)
        else :
            out_file.write(line + "\n")

    in_file.close()
    out_file.close()
