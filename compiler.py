import sys
import traceback
from enum import Enum


# Lexical analyzer

def init():
    global ch # Текущий символ
    global ch_index
    global sym
    global int_val
    global id_name
    ch = ''
    ch_index = -1

    global here
    global obj
    obj = [0] * 100
    here = 0 # Позиция текущего элемента в байт-коде


class Lexeme(Enum):
    DO_SYM = 0
    ELSE_SYM = 1
    IF_SYM = 2
    WHILE_SYM = 3
    LBRA = 4
    RBRA = 5
    LPAR = 6
    RPAR = 7
    PLUS = 8
    MINUS = 9
    LESS = 10
    SEMI = 11
    EQUAL = 12
    INT = 13
    ID = 14
    EOI = 15

words = [ "do", "else", "if", "while", None ]


def next_ch():
    global ch
    global ch_index
    ch_index += 1
    if ch_index == len(program_text):
        ch = Lexeme.EOI
    else:
        ch = program_text[ch_index]

def prev_ch():
    global ch
    global ch_index
    return program_text[ch_index-1]
    
def syntax_error():
    print(f"Syntax error at symbol {ch_index}\n")
    # traceback.print_stack()
    sys.exit()

def next_sym():
    global ch
    global ch_index
    global sym
    global words
    global id_name
    global int_val
    id_name = ''
    int_val=0

    while True:
        if ch == Lexeme.EOI:
            sym = Lexeme.EOI
            break
        elif ch == ' ' or ch == '\n':
            next_ch()
        elif ch == '{': next_ch(); sym = Lexeme.LBRA; break
        elif ch == '}': next_ch(); sym = Lexeme.RBRA; break
        elif ch == '(': next_ch(); sym = Lexeme.LPAR; break
        elif ch == ')': next_ch(); sym = Lexeme.RPAR; break
        elif ch == '+':
            if prev_ch() == '=':
                next_ch()
                if ch.isdigit():
                    while ch.isdigit():
                        int_val = int_val*10 + int(ch)
                        next_ch()
                    sym = Lexeme.INT
            else:
                next_ch()
                sym = Lexeme.PLUS
            break
        elif ch == '-': 
            if prev_ch() == '=':
                next_ch()
                if ch.isdigit():
                    while ch.isdigit():
                        int_val = int_val*10 + int(ch)
                        next_ch()
                    int_val = -int_val
                    sym = Lexeme.INT
            else:
                next_ch()
                sym = Lexeme.MINUS
            break
        elif ch == '<': next_ch(); sym = Lexeme.LESS; break
        elif ch == ';': next_ch(); sym = Lexeme.SEMI; break
        elif ch == '=': 
            next_ch()
            sym = Lexeme.EQUAL
            break
        else:
            if ch.isdigit():
                int_val = 0

                while ch.isdigit():
                    int_val = int_val*10 + int(ch)
                    next_ch()
                sym = Lexeme.INT
            elif ch.isalpha():
                while ch.isalpha() or ch == '_':
                    id_name += ch
                    next_ch()
                
                sym = 0
                while words[sym] != None and words[sym] != id_name:
                    sym += 1
                
                if words[sym] == None:
                    if len(id_name) == 1:
                        sym = Lexeme.ID
                    else:
                        syntax_error()

                sym = Lexeme(sym)
            else:
                syntax_error()
            break

# Parser

class Rule(Enum):
    VAR = 0
    CST = 1
    ADD = 2
    SUB = 3
    LT = 4
    SET = 5
    IF1 = 6
    IF2 = 7
    WHILE = 8
    DO = 9
    EMPTY = 10
    SEQ = 11
    EXPR = 12
    PROG = 13

class Tree:
    def __init__(self, kind):
        self.kind = kind
        self.o1 = None
        self.o2 = None
        self.o3 = None
        self.val = None


def paren_expr():  # /* <paren_expr> ::= "(" <expr> ")" */
    if sym == Lexeme.LPAR:
        next_sym()
    else:
        syntax_error()
    x = expr()
    if sym == Lexeme.RPAR:
        next_sym()
    else:
        syntax_error()
    return x


def term():  # /* <term> ::= <id> | <int> | <paren_expr> */
    global sym
    global ch
    if sym == Lexeme.ID: 
        x = Tree(Rule.VAR)
        x.val = ord(id_name[0])-ord('a')
        next_sym()
    elif sym == Lexeme.INT:
        x = Tree(Rule.CST)
        x.val = int_val
        next_sym()
    else: 
        x = paren_expr()
    return x


def sum():  # /* <sum> ::= <term> | <sum> "+" <term> | <sum> "-" <term> */
    global sym
    x = term()
    while sym == Lexeme.PLUS or sym == Lexeme.MINUS:
        t=x
        x=Tree(Rule.ADD if sym==Lexeme.PLUS else Rule.SUB)
        next_sym()
        x.o1=t
        x.o2=term()
    return x

def test(): # /* <test> ::= <sum> | <sum> "<" <sum> */
    global sym
    x = sum()
    if sym == Lexeme.LESS:
        t=x
        x=Tree(Rule.LT)
        next_sym()
        x.o1=t
        x.o2=sum()
    return x


def expr(): # /* <expr> ::= <test> | <id> "=" <expr> */
    global sym
    if sym != Lexeme.ID:
        return test()
    x = test()
    if x.kind == Rule.VAR and sym == Lexeme.EQUAL:
        t=x
        x=Tree(Rule.SET)
        next_sym()
        x.o1=t
        x.o2=expr()
    return x


def statement():
    global sym
    if sym == Lexeme.IF_SYM:  # "if" <paren_expr> <statement> */
        x = Tree(Rule.IF1)
        next_sym()
        x.o1 = paren_expr()
        x.o2 = statement()
        if sym == Lexeme.ELSE_SYM: # /* ... "else" <statement> */
            x.kind = Rule.IF2
            next_sym()
            x.o3 = statement()
    elif sym == Lexeme.WHILE_SYM: # /* "while" <paren_expr> <statement> */
        x = Tree(Rule.WHILE)
        next_sym()
        x.o1 = paren_expr()
        x.o2 = statement()
    elif sym == Lexeme.DO_SYM: # /* "do" <statement> "while" <paren_expr> ";" */
        x = Tree(Rule.DO)
        next_sym()
        x.o1 = statement()
        if sym == Lexeme.WHILE_SYM:
            next_sym()
        else:
            syntax_error()
        x.o2 = paren_expr()
        if sym == Lexeme.SEMI:
            next_sym()
        else:
            syntax_error()
    elif sym == Lexeme.SEMI: # /* ";" */
        x = Tree(Rule.EMPTY); next_sym()
    elif sym == Lexeme.LBRA: # /* "{" { <statement> } "}" */
        x = Tree(Rule.EMPTY)
        next_sym()
        while sym != Lexeme.RBRA:
            t = x
            x = Tree(Rule.SEQ)
            x.o1 = t
            x.o2 = statement()
        next_sym()
    else:  # /* <expr> ";" */
        x = Tree(Rule.EXPR)
        x.o1 = expr()
        if sym == Lexeme.SEMI:
            next_sym()
        else:
            syntax_error()
    return x

def program(): # <program> ::= <statement>
    global sym
    node = Tree(Rule.PROG)
    next_sym()
    node.o1 = statement()
    if sym != Lexeme.EOI:
        syntax_error()

    return node

# Generator

class VM(Enum):
    FETCH = 0
    STORE = 1
    PUSH = 2
    POP = 3
    ADD = 4
    SUB = 5
    LT = 6
    JZ = 7
    JNZ = 8
    JMP = 9
    HALT = 10

def g(code):
    global here
    obj[here]= code
    here+=1

def reserve():
    global here
    here+=1
    return here-1

def comp(x):
    if x.kind == Rule.VAR: g(VM.FETCH); g(x.val)
    elif x.kind == Rule.CST  : g(VM.PUSH); g(x.val)
    elif x.kind == Rule.ADD  : comp(x.o1); comp(x.o2); g(VM.ADD)
    elif x.kind == Rule.SUB  : comp(x.o1); comp(x.o2); g(VM.SUB)
    elif x.kind == Rule.LT   : comp(x.o1); comp(x.o2); g(VM.LT)
    elif x.kind == Rule.SET  : comp(x.o2); g(VM.STORE); g(x.o1.val)
    elif x.kind == Rule.IF1  : 
        comp(x.o1)
        g(VM.JZ)
        p1=reserve()
        comp(x.o2)
        obj[p1] = here - p1
    elif x.kind == Rule.IF2  :
        comp(x.o1)
        g(VM.JZ)
        p1=reserve()
        comp(x.o2)
        g(VM.JMP)
        p2=reserve()
        obj[p1] = here - p1
        comp(x.o3)
        obj[p2] = here - p2
    elif x.kind == Rule.WHILE:
        p1=here
        comp(x.o1)
        g(VM.JZ)
        p2=reserve()
        comp(x.o2)
        g(VM.JMP)
        obj[here] = p1 - here
        obj[p2] = reserve() - p2
    elif x.kind == Rule.DO   : 
        p1=here
        comp(x.o1)
        comp(x.o2)
        g(VM.JNZ)
        p2 = reserve()
        obj[p2] = p1 - p2
    elif x.kind == Rule.EMPTY: pass
    elif x.kind == Rule.SEQ  : comp(x.o1); comp(x.o2)
    elif x.kind == Rule.EXPR : comp(x.o1); g(VM.POP)
    elif x.kind == Rule.PROG : comp(x.o1); g(VM.HALT)


# VM

def run():
    sp = [0] * 100
    sp_i = 0
    pc = 0
    while obj[pc] != VM.HALT:
        if obj[pc] == VM.FETCH  : pc += 1; sp[sp_i] = names_table[obj[pc]]; sp_i+=1 
        elif obj[pc] == VM.STORE: pc+=1; names_table[obj[pc]] = sp[sp_i-1]
        elif obj[pc] == VM.PUSH : pc+=1; sp[sp_i] = obj[pc]; sp_i+=1                         
        elif obj[pc] == VM.POP  : sp_i-=1
        elif obj[pc] == VM.ADD  : sp[sp_i-2] = sp[sp_i-2] + sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.SUB  : sp[sp_i-2] = sp[sp_i-2] - sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.LT   : sp[sp_i-2] = sp[sp_i-2] < sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.JMP   : pc+=1; pc += obj[pc]-1
        elif obj[pc] == VM.JZ    :
            if sp[sp_i-1] == 0:
                pc += obj[pc+1]
            else:
                pc += 1
            sp_i-=1
        elif obj[pc] == VM.JNZ   : 
            if sp[sp_i-1] != 0:
                pc += obj[pc+1]
            else:
                pc += 1
            sp_i-=1
        pc += 1


def main(program_txt):
    init()

    global program_text
    program_text = program_txt
    global names_table
    names_table = [0] * 26
    next_ch()

    syntax_tree = program()
    comp(syntax_tree)
  
    run()

    res = ''

    for i in range(26):
        if names_table[i] != 0:
            res += chr(ord('a')+i) + "=" + str(int(names_table[i])) + '\n'

    return res


if __name__ ==  "__main__":
    res = main(sys.argv[1])
    print(res)