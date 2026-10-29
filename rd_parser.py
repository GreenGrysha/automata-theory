"""
ПР5 (ТАЯиВ), вариант 10, часть 2.

Синтаксический анализатор последовательностей выражений методом рекурсивного спуска.

Язык: последовательность выражений, разделённых символом «;» (после последнего
выражения «;» допускается, но не обязателен).
Элементы выражений:
  * целые десятичные константы:            42
  * рациональные дроби:                    3/4  (числитель/знаменатель, без пробелов)
  * имена переменных из 1-2 латинских букв: x, ab
  * унарные операции:                      +  -
  * бинарные операции:                     *  :  (мультипликативные), +  - (аддитивные)
  * присваивание (правоассоциативное):     имя = выражение
  * скобки:                                ( ... )
Знак деления записывается «:», так как «/» занят под дробную черту.

Грамматика (LL(1), см. README.md):
    S -> E Q                   Q -> ; K | ε                K -> E Q | ε
    E -> id T | num R A | ( E ) R A | + U R A | - U R A
    T -> = E | R A
    U -> + U | - U | num | id | ( E )
    R -> * U R | : U R | ε
    A -> + M A | - M A | ε
    M -> U R

Каждому нетерминалу соответствует процедура; решение о выборе правила
принимается по одному символу предпросмотра.

Результат работы: «Accepted» или «Rejected» (stdout).
Диагностика ошибок (строка, столбец, причина) выводится в stderr; после
синтаксической ошибки анализ продолжается со следующего «;» (режим паники),
поэтому за один запуск сообщается о всех ошибочных выражениях.

Запуск:
    python rd_parser.py файл.txt
    python rd_parser.py -s "x = 1/2 + y; z = -(x : 3)"
    echo "a=1;" | python rd_parser.py
"""
import sys

sys.setrecursionlimit(20000)

DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SPECIALS = '+-*:=();'
SPACES = ' \t\r\n'


class Token:
    __slots__ = ('kind', 'text', 'pos')

    def __init__(self, kind, text, pos):
        self.kind = kind
        self.text = text
        self.pos = pos


def tokenize(src):
    toks = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in SPACES:
            i += 1
        elif c in DIGITS:
            j = i
            while j < n and src[j] in DIGITS:
                j += 1
            if j < n and src[j] == '/':
                k = j + 1
                while k < n and src[k] in DIGITS:
                    k += 1
                if k == j + 1:
                    toks.append(Token('BAD', 'в дроби «%s/» нет знаменателя' % src[i:j], i))
                else:
                    toks.append(Token('NUM', src[i:k], i))
                i = k
            else:                                # целое число
                toks.append(Token('NUM', src[i:j], i))
                i = j
        elif c in LETTERS:
            j = i
            while j < n and src[j] in LETTERS:
                j += 1
            name = src[i:j]
            if len(name) > 2:
                toks.append(Token('BAD', 'имя «%s» длиннее двух символов' % name, i))
            else:
                toks.append(Token('ID', name, i))
            i = j
        elif c in SPECIALS:
            toks.append(Token(c, c, i))
            i += 1
        else:
            msg = 'недопустимый символ %r' % c
            if c == '/':
                msg += ' («/» допустим только внутри дроби; деление записывается «:»)'
            toks.append(Token('BAD', msg, i))
            i += 1
    toks.append(Token('EOF', '', n))
    return toks


def line_col(src, pos):
    line = src.count('\n', 0, pos) + 1
    col = pos - src.rfind('\n', 0, pos)
    return line, col


def describe(t):
    if t.kind == 'EOF':
        return 'конец ввода'
    if t.kind == 'NUM':
        return 'число «%s»' % t.text
    if t.kind == 'ID':
        return 'имя «%s»' % t.text
    return '«%s»' % t.text


class ParseError(Exception):
    def __init__(self, pos, msg):
        Exception.__init__(self, msg)
        self.pos = pos
        self.msg = msg


FIRST_E = ('NUM', 'ID', '(', '+', '-')
FOLLOW_R = ('+', '-', ';', ')', 'EOF')
FOLLOW_A = (';', ')', 'EOF')

WANT_EXPR = 'выражение (число, имя, «(» или унарный знак)'
WANT_OPND = 'операнд (число, имя, «(» или унарный знак)'
WANT_OP = 'бинарная операция, «)», «;» или конец ввода'


class Parser:
    def __init__(self, src):
        self.src = src
        self.toks = tokenize(src)
        self.i = 0
        self.errors = []

    @property
    def cur(self):
        return self.toks[self.i]

    def advance(self):
        t = self.toks[self.i]
        if t.kind != 'EOF':
            self.i += 1
        return t

    def fail(self, expected):
        t = self.cur
        if t.kind == 'BAD':
            raise ParseError(t.pos, 'лексическая ошибка: ' + t.text)
        raise ParseError(t.pos, 'ожидалось: %s; найдено: %s' % (expected, describe(t)))

    def expect(self, kind, expected):
        if self.cur.kind != kind:
            self.fail(expected)
        return self.advance()

    def program(self):
        self.item()
        while self.cur.kind == ';':
            self.advance()
            if self.cur.kind == 'EOF':
                break
            self.item()

    def item(self):
        try:
            self.expr()
            if self.cur.kind not in (';', 'EOF'):
                self.fail('«;» или конец ввода')
        except ParseError as e:
            self.errors.append(e)
            self.synchronize()

    def synchronize(self):
        """Режим паники: пропуск до ближайшего «;» (он не потребляется) или конца ввода."""
        while self.cur.kind not in (';', 'EOF'):
            self.advance()

    def expr(self):
        k = self.cur.kind
        if k == 'ID':
            self.advance()
            self.tail()
        elif k == 'NUM':
            self.advance()
            self.mul_rest()
            self.add_rest()
        elif k == '(':
            self.advance()
            self.expr()
            self.expect(')', '«)»')
            self.mul_rest()
            self.add_rest()
        elif k in ('+', '-'):
            self.advance()
            self.unary()
            self.mul_rest()
            self.add_rest()
        else:
            self.fail(WANT_EXPR)

    def tail(self):
        if self.cur.kind == '=':
            self.advance()
            self.expr()
        else:
            self.mul_rest()
            self.add_rest()

    def unary(self):
        k = self.cur.kind
        if k in ('+', '-'):
            self.advance()
            self.unary()
        elif k in ('NUM', 'ID'):
            self.advance()
        elif k == '(':
            self.advance()
            self.expr()
            self.expect(')', '«)»')
        else:
            self.fail(WANT_OPND)

    def mul(self):
        self.unary()
        self.mul_rest()

    def mul_rest(self):
        while self.cur.kind in ('*', ':'):
            self.advance()
            self.unary()
        if self.cur.kind not in FOLLOW_R:
            self.fail(WANT_OP)

    def add_rest(self):
        while self.cur.kind in ('+', '-'):
            self.advance()
            self.mul()
        if self.cur.kind not in FOLLOW_A:
            self.fail(WANT_OP)


def check(src):
    """Возвращает (принято?, список ParseError)."""
    p = Parser(src)
    p.program()
    return (not p.errors), p.errors


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description='Рекурсивный спуск: последовательность выражений (ПР5, вариант 10)')
    ap.add_argument('file', nargs='?', help='файл с текстом (по умолчанию - stdin)')
    ap.add_argument('-s', '--string', help='анализировать строку, переданную в аргументе')
    args = ap.parse_args(argv)
    if args.string is not None:
        src = args.string
    elif args.file:
        with open(args.file, encoding='utf-8') as f:
            src = f.read()
    else:
        src = sys.stdin.read()
    ok, errors = check(src)
    for e in errors:
        l, c = line_col(src, e.pos)
        print('  строка %d, столбец %d: %s' % (l, c, e.msg), file=sys.stderr)
    sys.stderr.flush()
    print('Accepted' if ok else 'Rejected')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
