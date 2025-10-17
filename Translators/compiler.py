import sys, os, re

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
            tokens += [("stringConstant", word.replace("\"", ""))]
        else:
            tokens += [("identifier", word)]
    return tokens

def write_token_file(tokens):
    out_file = open("tokens.xml", "w")
    out_file.write("<tokens>\n")
    for symbol, token in tokens:
        out_file.write(f"<{symbol}> {token} </{symbol}>\n")
    out_file.write("</tokens>\n")
    out_file.close()

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.parse = []
        self.depth = 0

    def getParse(self):
        return self.parse

    def parse_tokens(self):
        # TODO:
        # Populate the parse array
        for symbol, token in self.tokens:
            pass


def write_parser_file(parse):
    out_file = open("parse.xml", "w")
    for parse_tuple in parse:
        if len(parse_tuple) == 2:
            indent, symbol = parse_tuple[0], parse_tuple[1]
            out_file.write("  " * indent + f"<{symbol}>\n")
        elif len(parse_tuple) == 3:
            indent, symbol, token = parse_tuple[0], parse_tuple[1], parse_tuple[2]
            out_file.write("  " * indent + f"<{symbol}> {token} </{symbol}>\n")
    out_file.close()

# Assume if a line has block comments
# It does not contain any code
def remove_comments(in_file):
    lines = in_file.readlines()
    block_comment = False
    clean_lines = []
    for line in lines:
        if "/*" in line and "*/" in line:
            continue
        if "/*" in line:
            block_comment = True
            continue
        if "*/" in line:
            block_comment = False
            continue
        if not block_comment :
            if "//" in line:
                clean_lines.append(line.split("//")[0])
            else:
                clean_lines.append(line)
    return clean_lines

if __name__=="__main__":
    path = sys.argv[1]
    in_file = open(path, "r")
    lines = remove_comments(in_file)
    tokens = []
    for line in lines:
        tokens += tokenize(line)
    parser = Parser(tokens)
    parser.parse_tokens()
    write_parser_file(parser.getParse())
    in_file.close()
