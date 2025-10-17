import sys
import os
import re

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

def remove_comments(in_file):
    lines = in_file.readlines()

    # TODO:
    # Handle Block Comments

    clean_lines = []
    for line in lines:
        if "//" in line:
            clean_lines.append(line.split("//")[0])
        else:
            clean_lines.append(line)
    return clean_lines

# Returns a Tuple -> (type, token)
def tokenize(line):
    escaped = [re.escape(s) for s in tokens_dict["symbol"]]
    pattern = "(" + "|".join(escaped) + ")"
    parts = re.split(pattern, line)
    parts = [p.strip() for p in parts if p.strip()]

    words = []
    for part in parts:
        words += [part] if "\"" in part else part.split()

    tokens = []
    for word in words :
        if word in tokens_dict["keyword"]:
            tokens += [("keyword", word)]
        elif word in tokens_dict["symbol"]:
            tokens += [("symbol", word)]
        elif word.isdigit():
            tokens += [("integerConstant", word)]
        elif "\"" in word:
            tokens += [("StringConstant", word.replace("\"", ""))]
        else:
            tokens += [("identifier", word)]
    return tokens

def write_token_file(tokens):
    out_file = open("test.xml", "w")
    out_file.write("<tokens>\n")
    for token_tuple in tokens:
        symbol, token = token_tuple[0], token_tuple[1]
        out_file.write(f"<{symbol}>")
        out_file.write(f" {token} ")
        out_file.write(f"</{symbol}>\n")
    out_file.write("</tokens>\n")
    out_file.close()

if __name__=="__main__":
    path = sys.argv[1]
    out_file_name = ""
    tokens = []

    # If it is a file
    if os.path.isfile(path):
        in_file = open(path, "r")
        lines = remove_comments(in_file)
        for line in lines:
            tokens += tokenize(line)
        in_file.close()

    write_token_file(tokens)
