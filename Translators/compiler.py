tokens_dict = {
    "keyword": [
        "class", "constructor", "function", "method", "field", "static", "var",
        "int", "char", "boolean", "void", "true", "false", "null", "this",
        "let", "do", "if", "else", "while", "return"
    ],
    "symbol": [
        "{", "}", "(", ")", "[", "]", ".", ",", ";",
        "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"
    ],
}

# Returns a Tuple -> (type, token)
def tokenize(line):
    line = "".join(line.split())
    tokens = []

    # TODO: 
    # Iterate line char by char
    # if char == comment:
    #   continue

    tokens += [("type", "token")]
    return tokens

import sys
import os

if __name__=="__main__":
    path = sys.argv[1]
    out_file_name = ""
    tokens = []

    # If it is a file
    if os.path.isfile(path):
        in_file = open(path, "r")
        lines = in_file.readlines()
        for line in lines:
            tokens += tokenize(line)

    out_file = open("test.xml", "w")
    out_file.write("<tokens>\n")
    for token_tuple in tokens:
        symbol, token = token_tuple[0], token_tuple[1]
        out_file.write(f"<{symbol}>")
        out_file.write(f" {token} ")
        out_file.write(f"</{symbol}>\n")
    out_file.write("</tokens>\n")
