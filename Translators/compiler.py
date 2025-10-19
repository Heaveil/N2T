import sys, os, re

class Compiler:
    def __init__(self, filename, source):
        self.filename = filename
        self.source = source
        self.tokens = []
        self.parse = []
        self.vm_code = []
        self.class_name = ""
        self.class_table = {}
        self.class_counters = {"static": 0, "field": 0}
        self.subroutine_table = {}
        self.subroutine_counters = {"local": 0, "argument": 0}
        self.subroutine_type = ""
        self.subroutine_return_type = ""
        self.subroutine_name = ""
        self.depth = 0
        self.tokens_dict = {
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

    def tokenize(self):
        for line in self.source:
            escaped = [re.escape(s) for s in self.tokens_dict["symbol"]]
            pattern = "(" + "|".join(escaped) + ")"
            parts = re.split(pattern, line)
            parts = [p.strip() for p in parts if p.strip()]
            words = []
            for part in parts:
                words += [part] if "\"" in part else part.split()
            for word in words :
                if word in self.tokens_dict["keyword"]:
                    self.tokens += [("keyword", word)]
                elif word in self.tokens_dict["symbol"]:
                    self.tokens += [("symbol", word)]
                elif word.isdigit():
                    self.tokens += [("integerConstant", word)]
                elif "\"" in word:
                    self.tokens += [("stringConstant", word.replace("\"", ""))]
                else:
                    self.tokens += [("identifier", word)]

    def write_tokens(self):
        out_file = open(f"{self.filename}T.xml", "w")
        out_file.write("<tokens>\n")
        for symbol, token in self.tokens:
            out_file.write(f"<{symbol}> {token} </{symbol}>\n")
        out_file.write("</tokens>\n")
        out_file.close()

    def write_parser(self):
        out_file = open(f"{self.filename}.xml", "w")
        for parse_tuple in self.parse:
            if len(parse_tuple) == 2:
                indent, symbol = parse_tuple[0], parse_tuple[1]
                out_file.write("  " * indent + f"<{symbol}>\n")
            elif len(parse_tuple) == 3:
                indent, symbol, token = parse_tuple[0], parse_tuple[1], parse_tuple[2]
                out_file.write("  " * indent + f"<{symbol}> {token} </{symbol}>\n")
        out_file.close()

    def write_vm_code(self):
        out_file = open(f"{self.filename}.vm", "w")
        for code in self.vm_code:
            out_file.write(f"{code}\n")
        out_file.close()

    def peek(self):
        return self.tokens[0][1] if self.tokens else None

    def peek2(self):
        return self.tokens[1][1] if len(self.tokens) > 1 else None

    def advance(self):
        return self.tokens.pop(0) if self.tokens else (None, None)

    def eat(self):
        symbol, token = self.advance()
        self.parse.append((self.depth, symbol, token))
        return token

    def write(self, code):
        self.vm_code.append(code)
        print(code)

    def parse_class(self):
        self.class_table = {}
        self.class_counters = {"static": 0, "field": 0}
        self.parse.append((self.depth, "class"))
        self.depth += 1
        self.eat() # class
        self.class_name = self.eat() # ClassName
        self.eat() # {
        while self.peek() in [ "static", "field"]:
            self.parse_class_var_dec()
        while self.peek() in ["constructor", "function", "method"]:
            self.parse_subroutine_dec()
        self.eat() # }
        self.depth -= 1
        self.parse.append((self.depth, "/class"))

    def parse_class_var_dec(self):
        self.parse.append((self.depth, "classVarDec"))
        self.depth += 1
        kind = self.eat() # static | field
        data_type = self.eat() # type
        name = self.eat() # varName
        self.class_table[name] = (data_type, kind, self.class_counters[kind])
        self.class_counters[kind] += 1
        while self.peek() == ",":
            self.eat() # ,
            name = self.eat() # varName
            self.class_table[name] = (data_type, kind, self.class_counters[kind])
            self.class_counters[kind] += 1
        self.eat() # ;
        self.depth -= 1
        self.parse.append((self.depth, "/classVarDec"))

    def parse_subroutine_dec(self):
        self.subroutine_table = {}
        self.subroutine_counters = {"local": 0, "argument": 0}
        self.parse.append((self.depth, "subroutineDec"))
        self.depth += 1
        self.subroutine_type = self.eat() # constructor | function | method
        self.subroutine_return_type = self.eat() # void | type
        self.subroutine_name = self.eat() # subroutineName
        self.eat() # (
        self.parse_parameter_list()
        self.eat() # )
        self.parse_subroutine_body()
        self.depth -= 1
        self.parse.append((self.depth, "/subroutineDec"))

    def parse_parameter_list(self):
        self.parse.append((self.depth, "parameterList"))
        self.depth += 1
        if self.subroutine_type == "method":
            self.subroutine_table["this"] = (self.class_name, "argument", self.subroutine_counters["argument"])
            self.subroutine_counters["argument"] += 1
        if self.peek() != ")":
            data_type = self.eat() # type
            var_name = self.eat() # varName
            self.subroutine_table[var_name] = (data_type, "argument", self.subroutine_counters["argument"])
            self.subroutine_counters["argument"] += 1
            while self.peek() == ",":
                self.eat() # ,
                data_type = self.eat() # type
                var_name = self.eat() # varName
                self.subroutine_table[var_name] = (data_type, "argument", self.subroutine_counters["argument"])
                self.subroutine_counters["argument"] += 1
        self.depth -= 1
        self.parse.append((self.depth, "/parameterList"))

    def parse_subroutine_body(self):
        self.parse.append((self.depth, "subroutineBody"))
        self.depth += 1
        self.eat() # {
        while self.peek() == "var":
            self.parse_var_dec()
        self.write(f"function {self.class_name}.{self.subroutine_name} {self.subroutine_counters['local']}")
        self.parse_statements()
        self.eat() # }
        self.depth -= 1
        self.parse.append((self.depth, "/subroutineBody"))

    def parse_var_dec(self):
        self.parse.append((self.depth, "varDec"))
        self.depth += 1
        self.eat() # var
        data_type = self.eat() # type
        var_name = self.eat() # varName
        self.subroutine_table[var_name] = (data_type, "local", self.subroutine_counters["local"])
        self.subroutine_counters["local"] += 1
        while self.peek() == ",":
            self.eat() # ,
            var_name = self.eat() # varName
            self.subroutine_table[var_name] = (data_type, "local", self.subroutine_counters["local"])
            self.subroutine_counters["local"] += 1
        self.eat() # ;
        self.depth -= 1
        self.parse.append((self.depth, "/varDec"))

    def parse_statements(self):
        self.parse.append((self.depth, "statements"))
        self.depth += 1
        while self.peek() in ["let", "if", "while", "do", "return"]:
            match self.peek():
                case "let":
                    self.parse_let()
                case "if":
                    self.parse_if()
                case "while":
                    self.parse_while()
                case "do":
                    self.parse_do()
                case "return":
                    self.parse_return()
        self.depth -= 1
        self.parse.append((self.depth, "/statements"))

    def parse_let(self):
        self.parse.append((self.depth, "letStatement"))
        self.depth += 1
        self.eat() # let
        self.eat() # varName
        if self.peek() == "[":
            self.eat() # [
            self.parse_expression()
            self.eat() # ]
        self.eat() # =
        self.parse_expression()
        self.eat() # ;
        self.depth -= 1
        self.parse.append((self.depth, "/letStatement"))

    def parse_if(self):
        self.parse.append((self.depth, "ifStatement"))
        self.depth += 1
        self.eat() # if
        self.eat() # (
        self.parse_expression()
        self.eat() # )
        self.eat() # {
        self.parse_statements()
        self.eat() # }
        if self.peek() == "else":
            self.eat() # else
            self.eat() # {
            self.parse_statements()
            self.eat() # }
        self.depth -= 1
        self.parse.append((self.depth, "/ifStatement"))

    def parse_while(self):
        self.parse.append((self.depth, "whileStatement"))
        self.depth += 1
        self.eat() # while
        self.eat() # (
        self.parse_expression()
        self.eat() # )
        self.eat() # {
        self.parse_statements()
        self.eat() # }
        self.depth -= 1
        self.parse.append((self.depth, "/whileStatement"))

    def parse_do(self):
        self.parse.append((self.depth, "doStatement"))
        self.depth += 1
        self.eat() # do
        self.parse_subroutine_call() 
        self.eat() # ;
        self.depth -= 1
        self.parse.append((self.depth, "/doStatement"))

    def parse_return(self):
        self.parse.append((self.depth, "returnStatement"))
        self.depth += 1
        self.eat() # return
        if self.peek() != ";":
            self.parse_expression()
        else:
            self.write(f"push constant 0")
        self.write("return")
        self.eat() # ;
        self.depth -= 1
        self.parse.append((self.depth, "/returnStatement"))

    def parse_expression(self):
        self.parse.append((self.depth, "expression"))
        self.depth += 1
        self.parse_term()
        while self.peek() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            self.eat() # op
            self.parse_term()
        self.depth -= 1
        self.parse.append((self.depth, "/expression"))

    def parse_term(self):
        self.parse.append((self.depth, "term"))
        self.depth += 1
        if self.peek() == "(":
            self.eat() # (
            self.parse_expression()
            self.eat() # )
        elif self.peek() in ["-", "~"]:
            self.eat() # unaryOP
            self.parse_term()
        elif self.peek2() in ["(", "."]:
            self.parse_subroutine_call()
        else:
            self.eat() # intConst | strConst | keyConst | varName
            if self.peek() == "[":
                self.eat() # [
                self.parse_expression()
                self.eat() # ]
        self.depth -= 1
        self.parse.append((self.depth, "/term"))

    def parse_subroutine_call(self):
        # don't add depth
        self.eat() # subroutineName | className | varName
        if self.peek() == ".":
            self.eat() # .
            self.eat() # subroutineName
        self.eat() # (
        self.parse_expression_list()
        self.eat() # )

    def parse_expression_list(self):
        self.parse.append((self.depth, "expressionList"))
        self.depth += 1
        if self.peek() != ")":
            self.parse_expression()
            while self.peek() == ",":
                self.eat() # ,
                self.parse_expression()
        self.depth -= 1
        self.parse.append((self.depth, "/expressionList"))

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

    # if it is a file
    if os.path.isfile(path):
        filename = path[:-5]
        in_file = open(path, "r")
        lines = remove_comments(in_file)
        compiler = Compiler(filename, lines)
        compiler.tokenize()
        compiler.parse_class()
        in_file.close()

    # if it is a directory
    else:
        for file in os.listdir(path):
            if file.endswith(".jack"):
                filename = file[:-5]
                in_file_path = os.path.join(path, file)
                out_file_path = os.path.join(path, filename)
                in_file = open(in_file_path, "r")
                lines = remove_comments(in_file)
                compiler = Compiler(out_file_path, lines)
                compiler.tokenize()
                compiler.parse_class()
                in_file.close()
