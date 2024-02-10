# How to make a python program that does symbolic algebra, without using any libraries.

from functools import reduce
import operator
import sys

def isnumeric(x):
    if isinstance(x, int):
        return True
    if isinstance(x, str):
        return x.isnumeric()
    return False

def simplify(equation):
    s = simplifyStep(equation)
    s2 = simplifyStep(s)
    while s2 != s:
        s = s2
        s2 = simplifyStep(s)
    return s

def simplifyStep(equation):
    match equation:
        case [x]:
            return x
        # Coalesce sum expressions.
        case ['+', *rest] if len(list([x for x in rest if isnumeric(x)])) > 1:
            numerics = [x for x in rest if isnumeric(x)]
            other = [x for x in rest if not isnumeric(x) ]

            total = sum(int(x) for x in numerics)
            if len(other) > 0:
                return ['+', other, total]
            else:
                return total
        # Coalesce products.
        case ['*', *rest] if len(list([x for x in rest if isnumeric(x)])) > 1:
            numerics = [x for x in rest if isnumeric(x)]
            other = [x for x in rest if not isnumeric(x) ]

            product = reduce(operator.mul, [int(x) for x in numerics], 1)
            if len(other) > 0:
                return ['*', other, product]
            else:
                return product
        # Remove + 0. (remove all zeros from a sum expression)
        case ['+', *rest] if 0 in rest:
            newrest = [x for x in rest if x != 0]
            if len(newrest) > 1:
                return ['+'] + newrest
            else:
                return newrest
        # Remove - 0.
        case ['-', *rest] if 0 in rest:
            newrest = [x for x in rest if x != 0]
            if len(newrest) > 1:
                return ['-'] + newrest
            else:
                return newrest
        # Remove * 1.
        case ['*', *rest] if 1 in rest:
            newrest = [x for x in rest if x != 1]
            if len(newrest) > 1:
                return ['*'] + newrest
            else:
                return newrest
        # a - (b + c) = a - b - c.
        case ['-', term, ['+', *terms]]:
            return ['-', term] + terms
        # (a + b) * c = a * c + b * c
        case ['*', fact, ['+', *terms]]:
            # But first, try to simplify the sum.
            maybe_simpler = simplifyStep(['+', *terms])
            if maybe_simpler != ['+', *terms]:
                return ['*', maybe_simpler, fact]
            return ['+'] + [['*', fact, term] for term in terms]
        case ['*', fact, ['-', *terms]]:
            # But first, try to simplify the sum.
            maybe_simpler = simplifyStep(['+', *terms])
            if maybe_simpler != ['+', *terms]:
                return ['*', maybe_simpler, fact]
            return ['-'] + [['*', fact, term] for term in terms]
        # a * (b * c) to a * b * c.
        case ['*', term, ['*', *terms]]:
            return ['*'] + [term] + terms
        # a + (b + c) to a + b + c.
        case ['+', term, ['+', *terms]]:
            return ['+'] + [term] + terms
        case [op, *rest]:
            return [op] + [simplify(r) for r in rest]
        case x:
            return x

def derive(equation):
    pass

def tostr(equation):
    match equation:
        case [x]:
            return f"{x}"
        case [op, *params]:
            newparams = ['(' + tostr(param) + ')' if isinstance(param, list) else str(param) for param in params]
            return str(op).join(newparams)
        case x:
            return str(x)
    
    return "no representation"

def simplifyAndPrint(equation):
    s = simplify(equation)

    print(tostr(equation) + '=' + tostr(s))

# get one token from s starting at position n.
def getNextToken(s, n):
    if n >= len(s):
        return None, None

    # whitespace
    i = 0
    while s[n+i] in [' ', '\t']:
        i += 1
    if i > 0:
        return ' ', i

    if 'a' <= s[n] <= 'z' or s[n] == '_':
        i = 1
        if n+i >= len(s):
            return s[n], 1
        while 'a' <= s[n+1] <= 'z' or '0' <= s[n+i] <= '9' or s[n+i] == '_':
            i += 1
            if n+i >= len(s):
                break
        return s[n:n+i], i
    if '0' <= s[n] <= '9' or s[n] == '.':
        i = 0
        while '0' <= s[n+i] <= '9' or s[n+i] == '.':
            i += 1
            if n+i >= len(s):
                break
        if '.' in s[n:n+1]:
            return float(s[n:n+i]), i
        else:
            return int(s[n:n+i]), i
    if s[n] in ['+', '-', '*', '/', '(', ')']:
        return s[n], 1
    return None, None

def first(lst):
    if len(lst) > 0:
        return lst[0]
    return None

# Grammar:
# expr -> term + expression | term - expression | term
# term -> factor * term | factor / term | factor
# factor -> id | float | ( expr ) 

def expr(tokens):
    t, tokens = term(tokens)
    token = first(tokens)
    if token in ['+', '-']:
        e, tokens = expr(tokens[1:])
        return [token, t, e], tokens
    return t, tokens

# term -> factor * term | factor / term | factor
def term(tokens):
    f, tokens = factor(tokens)
    token = first(tokens)
    if token in ['*', '/']:
        t, tokens = term(tokens[1:])
        return [ token, f, t ], tokens
    return f, tokens

# factor -> id | float | ( expr ) 
def factor(tokens):
    token = first(tokens)
    if token == '(':
        subexpr, tokens = expr(tokens[1:])
        if first(tokens) != ')':
            raise "parsing error!"
        return subexpr, tokens[1:]
    elif type(token) == str:
        return token, tokens[1:]
    elif type(token) == float:
        return token, tokens[1:]
    elif type(token) == int:
        return token, tokens[1:]
    raise "parsing error!"

# compile a string equation to the format used by this library.
def compile(s):
    # start by lexing
    tokens = []

    i = 0
    token, eaten = getNextToken(s, i)
    while token is not None:
        i += eaten
        if token != ' ':
            tokens.append(token)
        token, eaten = getNextToken(s, i)

    # print("TOKENS: ", tokens)
    # then parse.
    result, remainder = expr(tokens)
    # print("RESULT: ", result)
    # print("REMAINDER: ", remainder)
    return result
    

def main2(argv):
    # simplifyAndPrint(compile("  2+ 3"))
    # simplifyAndPrint(compile("2 + (3 * 2)"))
    # eq = compile("(8 * a) - (2 * a)")
    # print("%s => %s" % (eq, tostr(eq)))
    # simplifyAndPrint(compile("(8 * a) - (2 * a)"))
    simplifyAndPrint(compile("(x * 1) + 3"))

def main(argv):
    equations = [
        ['*', 'x', 1],
        ['*', 3, 2],
        ['+', ['*', 'x', 1], 3],
        ['*', 5, ['-', 'x', ['*', 3, ['+', 'y', 2]]]],
        ['-', ['*', 8, 'a'], ['*', 2, 'a']],
        ['-', ['*', 8, 'a'], ['*', 2, ['-', 'b', ['*', 3, 'a']]]],
    ]

    for equation in equations:
        simplifyAndPrint(equation)

if __name__ == "__main__":
    main(sys.argv)