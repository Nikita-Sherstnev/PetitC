import sys
import traceback
from enum import Enum


# Lexical analyzer

def init():
    global ch # Текущий символ
    global ch_index # Индекс текущего символа в исходной программе
    global sym # Текущая лексема
    global int_val
    global id_name
    ch = ''
    ch_index = -1

    global decode_table # Таблица имен переменных
    global term_id # Переменная для присвоения индексов переменным
    term_id = 0
    decode_table = dict()

    global here
    global obj # Байткод программы
    obj = [0] * 100
    here = 0 # Позиция текущего элемента в байт-коде


class Lexeme(Enum):
    DO_SYM = 0
    ELSE_SYM = 1
    IF_SYM = 2
    WHILE_SYM = 3
    FOR_SYM = 4
    LBRA = 5
    RBRA = 6
    LPAR = 7
    RPAR = 8
    PLUS = 9
    MINUS = 10
    MUL = 11
    DIV = 12
    LT = 13
    GT = 14
    LE = 15
    GE = 16
    EQ = 17
    NE = 18
    SEMI = 19
    EQUAL = 20
    INT = 21
    ID = 22
    EOI = 23

keywords = [ "do", "else", "if", "while", "for", None ] # Order matters!


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
    global keywords
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
        elif ch == '*': next_ch(); sym = Lexeme.MUL; break
        elif ch == '/': next_ch(); sym = Lexeme.DIV; break
        elif ch == '<':
            next_ch()
            if ch == '=':
                sym = Lexeme.LE
                next_ch()
            else:
                sym = Lexeme.LT
            break
        elif ch == '>':
            next_ch()
            if ch == '=':
                sym = Lexeme.GE
                next_ch()
            else:
                sym = Lexeme.GT
            break
        elif ch == '#': next_ch(); sym = Lexeme.NE; break
        elif ch == '=':
            next_ch()
            if ch == '=':
                sym = Lexeme.EQ
                next_ch()
            else:
                sym = Lexeme.EQUAL
            break
        elif ch == ';': next_ch(); sym = Lexeme.SEMI; break
        else:
            if ch.isdigit():
                int_val = 0

                while ch.isdigit():
                    int_val = int_val*10 + int(ch)
                    next_ch()
                sym = Lexeme.INT
            elif ch.isalpha():
                while ch.isalpha() or ch == '_' or ch.isdigit():
                    id_name += ch
                    next_ch()
                
                sym = 0
                while keywords[sym] != None and keywords[sym] != id_name:
                    sym += 1
                
                if keywords[sym] == None:
                    sym = Lexeme.ID

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
    MUL = 4
    DIV = 5
    LT = 6
    GT = 7
    LE = 8
    GE = 9
    EQ = 10
    NE = 11
    SET = 12
    IF1 = 13
    IF2 = 14
    WHILE = 15
    DO = 16
    FOR = 17
    EMPTY = 18
    SEQ = 19
    EXPR = 20
    PROG = 21


class Tree:
    def __init__(self, kind):
        self.kind = kind
        self.o1 = None
        self.o2 = None
        self.o3 = None
        self.o4 = None
        self.val = None

    def __str__(self, level=0):
        if self.val is None:
            self.val = ""
        ret = "\t"*level+repr(self.kind)+' '+str(self.val)+"\n"
        if self.o1 is not None:
            ret += self.o1.__str__(level+1)
        if self.o2 is not None:
            ret += self.o2.__str__(level+1)
        if self.o3 is not None:
            ret += self.o3.__str__(level+1)
        return ret

    def __repr__(self):
        return '<tree node representation>'


def paren_expr():  # <paren_expr> ::= "(" <expr> ")"
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


def term():  # <term> ::= <id> | <int> | <paren_expr>
    global sym
    global ch
    global decode_table
    global term_id
    global id_name
    inv_decode_table = {v: k for k, v in decode_table.items()}
    if sym == Lexeme.ID:
        x = Tree(Rule.VAR)
        if id_name not in inv_decode_table:
            decode_table[term_id] = id_name
            id_name = term_id
            term_id += 1
        else:
            id_name = inv_decode_table[id_name]
        x.val = id_name
        next_sym()
    elif sym == Lexeme.INT:
        x = Tree(Rule.CST)
        x.val = int_val
        next_sym()
    else: 
        x = paren_expr()
    return x


def sum():  # <term> | <sum> "+" <term> | <sum> "-" <term> | <sum> "*" <term> | <sum> "/" <term>
    global sym
    x = term()
    while sym == Lexeme.MUL or sym == Lexeme.DIV:
        t=x
        x=Tree(Rule.MUL if sym==Lexeme.MUL else Rule.DIV)
        next_sym()
        x.o1=t
        x.o2=term()
    while sym == Lexeme.PLUS or sym == Lexeme.MINUS:
        t=x
        x=Tree(Rule.ADD if sym==Lexeme.PLUS else Rule.SUB)
        next_sym()
        x.o1=t
        x.o2=term()
    return x

def test(): # <test> ::= <sum> | <sum> <compar> <sum>
    global sym
    x = sum()
    if sym == Lexeme.LT:
        t=x
        x=Tree(Rule.LT)
        next_sym()
        x.o1=t
        x.o2=sum()
    elif sym == Lexeme.GT:
        t=x
        x=Tree(Rule.GT)
        next_sym()
        x.o1=t
        x.o2=sum()
    elif sym == Lexeme.LE:
        t=x
        x=Tree(Rule.LE)
        next_sym()
        x.o1=t
        x.o2=sum()
    elif sym == Lexeme.GE:
        t=x
        x=Tree(Rule.GE)
        next_sym()
        x.o1=t
        x.o2=sum()
    elif sym == Lexeme.EQ:
        t=x
        x=Tree(Rule.EQ)
        next_sym()
        x.o1=t
        x.o2=sum()
    elif sym == Lexeme.NE:
        t=x
        x=Tree(Rule.NE)
        next_sym()
        x.o1=t
        x.o2=sum()
    return x

def expr(): # <expr> ::= <test> | <id> "=" <expr>
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

def condit():
    x = Tree(Rule.IF1) # "if" <paren_expr> <statement>
    next_sym()
    x.o1 = paren_expr()
    x.o2 = statement()
    if sym == Lexeme.ELSE_SYM: # ... "else" <statement>
        x.kind = Rule.IF2
        next_sym()
        x.o3 = statement()
    return x

def loop():
    if sym == Lexeme.WHILE_SYM: # "while" <paren_expr> <statement>
        x = Tree(Rule.WHILE)
        next_sym()
        x.o1 = paren_expr()
        x.o2 = statement()
    elif sym == Lexeme.DO_SYM: # "do" <statement> "while" <paren_expr> ";"
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
    elif sym == Lexeme.FOR_SYM: # "for" <for_paren> <statement>
        x = Tree(Rule.FOR)
        next_sym()
        if sym == Lexeme.LPAR:
            next_sym()
        else:
            syntax_error()
        x.o1 = expr()
        if sym == Lexeme.SEMI:
            next_sym()
        else:
            syntax_error()
        x.o2 = test()
        if sym == Lexeme.SEMI:
            next_sym()
        else:
            syntax_error()
        x.o3 = expr()
        if sym == Lexeme.RPAR:
            next_sym()
        else:
            syntax_error()
        x.o4 = statement()
    return x

def statement():
    global sym
    if sym == Lexeme.IF_SYM:  
        x = condit()
    elif sym == Lexeme.WHILE_SYM or sym == Lexeme.DO_SYM or sym == Lexeme.FOR_SYM: 
        x = loop()
    elif sym == Lexeme.SEMI: # ";"
        x = Tree(Rule.EMPTY)
        next_sym()
    elif sym == Lexeme.LBRA: # "{" { <statement> } "}"
        x = Tree(Rule.EMPTY)
        next_sym()
        while sym != Lexeme.RBRA:
            t = x
            x = Tree(Rule.SEQ)
            x.o1 = t
            x.o2 = statement()
        next_sym()
    else:  # <expr> ";"
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
    MUL = 6
    DIV = 7
    LT = 8
    GT = 9
    LE = 10
    GE = 11
    EQ = 12
    NE = 13
    JZ = 14
    JNZ = 15
    JMP = 16
    HALT = 17

def g(code):
    global here
    obj[here] = code
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
    elif x.kind == Rule.MUL  : comp(x.o1); comp(x.o2); g(VM.MUL)
    elif x.kind == Rule.DIV  : comp(x.o1); comp(x.o2); g(VM.DIV)
    elif x.kind == Rule.LT   : comp(x.o1); comp(x.o2); g(VM.LT)
    elif x.kind == Rule.GT   : comp(x.o1); comp(x.o2); g(VM.GT)
    elif x.kind == Rule.LE   : comp(x.o1); comp(x.o2); g(VM.LE)
    elif x.kind == Rule.GE   : comp(x.o1); comp(x.o2); g(VM.GE)
    elif x.kind == Rule.EQ   : comp(x.o1); comp(x.o2); g(VM.EQ)
    elif x.kind == Rule.NE   : comp(x.o1); comp(x.o2); g(VM.NE)
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
    elif x.kind == Rule.FOR:
        comp(x.o1)
        p1=here
        comp(x.o2)
        g(VM.JZ)
        p2=reserve()
        comp(x.o3)
        comp(x.o4)
        g(VM.JMP)
        obj[here] = p1 - here
        obj[p2] = reserve() - p2
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
        elif obj[pc] == VM.MUL  : sp[sp_i-2] = sp[sp_i-2] * sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.DIV  : sp[sp_i-2] = sp[sp_i-2] / sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.LT   : sp[sp_i-2] = sp[sp_i-2] < sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.GT   : sp[sp_i-2] = sp[sp_i-2] > sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.LE   : sp[sp_i-2] = sp[sp_i-2] <= sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.GE   : sp[sp_i-2] = sp[sp_i-2] >= sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.EQ   : sp[sp_i-2] = sp[sp_i-2] == sp[sp_i-1]; sp_i-=1
        elif obj[pc] == VM.NE   : sp[sp_i-2] = sp[sp_i-2] != sp[sp_i-1]; sp_i-=1
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
    names_table = dict()
    next_ch()

    syntax_tree = program()
    comp(syntax_tree)
  
    run()

    res = ''
    for key in names_table.keys():
        res += decode_table[key] + "=" + str(int(names_table[key])) + '\n'

    return res


if __name__ ==  "__main__":
    res = main(sys.argv[1])
    print(res)