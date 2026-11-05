import sys


class Token:
    def __init__(self, kind, text, pos):
        self.kind = kind
        self.text = text
        self.pos = pos


DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SIGNS = '+-*:=();'


def tokenize(text):
    tokens = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]

        if c in ' \t\r\n':
            i += 1

        elif c in DIGITS:
            start = i
            while i < n and text[i] in DIGITS:
                i += 1
            if i < n and text[i] == '/':
                i += 1
                den_start = i
                while i < n and text[i] in DIGITS:
                    i += 1
                if i == den_start:
                    tokens.append(Token('BAD', 'после "/" нет знаменателя', start))
                else:
                    tokens.append(Token('NUM', text[start:i], start))
            else:
                tokens.append(Token('NUM', text[start:i], start))

        elif c in LETTERS:
            start = i
            while i < n and text[i] in LETTERS:
                i += 1
            name = text[start:i]
            if len(name) > 2:
                tokens.append(Token('BAD', 'имя "%s" длиннее 2 символов' % name, start))
            else:
                tokens.append(Token('ID', name, start))

        elif c in SIGNS:
            tokens.append(Token(c, c, i))
            i += 1

        else:
            tokens.append(Token('BAD', 'недопустимый символ %r' % c, i))
            i += 1

    tokens.append(Token('EOF', '', n))
    return tokens


def line_col(text, pos):
    """Номер строки и столбца по позиции символа - для сообщений об ошибках."""
    line = text.count('\n', 0, pos) + 1
    col = pos - text.rfind('\n', 0, pos)
    return line, col


class ParseError(Exception):
    def __init__(self, pos, message):
        super().__init__(message)
        self.pos = pos
        self.message = message


class Parser:
    """
    Идея очень простая: держим список токенов и "указатель" self.i на
    текущий. Каждая функция-нетерминал смотрит на self.tokens[self.i]
    (токен-"предпросмотр") и по нему решает, какое правило грамматики
    применить - это и есть "рекурсивный спуск".
    """

    def __init__(self, text):
        self.text = text
        self.tokens = tokenize(text)
        self.i = 0
        self.errors = []

    def peek(self):
        """Текущий токен, не сдвигая указатель."""
        return self.tokens[self.i]

    def next(self):
        """Текущий токен, со сдвигом указателя на следующий."""
        t = self.tokens[self.i]
        if t.kind != 'EOF':
            self.i += 1
        return t

    def error(self, expected):
        t = self.peek()
        if t.kind == 'BAD':
            raise ParseError(t.pos, 'лексическая ошибка: ' + t.text)
        got = {'EOF': 'конец ввода', 'NUM': 'число "%s"' % t.text,
               'ID': 'имя "%s"' % t.text}.get(t.kind, '"%s"' % t.text)
        raise ParseError(t.pos, 'ожидалось %s, а найдено: %s' % (expected, got))

    def expect(self, kind, expected_name):
        """Проверить, что текущий токен - это kind, и сдвинуться дальше."""
        if self.peek().kind != kind:
            self.error(expected_name)
        return self.next()

    def parse_program(self):
        self.parse_statement()
        while self.peek().kind == ';':
            self.next()
            if self.peek().kind == 'EOF':
                break
            self.parse_statement()

    def parse_statement(self):
        """Одно выражение. Если в нём ошибка - запоминаем её и ищем
        следующее ';' , чтобы не останавливать разбор всего текста."""
        try:
            self.parse_expr()
            if self.peek().kind not in (';', 'EOF'):
                self.error('";" или конец ввода')
        except ParseError as e:
            self.errors.append(e)
            while self.peek().kind not in (';', 'EOF'):
                self.next()

    def parse_expr(self):
        kind = self.peek().kind

        if kind == 'ID':
            self.next()
            self.parse_tail()

        elif kind == 'NUM':
            self.next()
            self.parse_mul_rest()
            self.parse_add_rest()

        elif kind == '(':
            self.next()
            self.parse_expr()
            self.expect(')', '")"')
            self.parse_mul_rest()
            self.parse_add_rest()

        elif kind in ('+', '-'):
            self.next()
            self.parse_unary()
            self.parse_mul_rest()
            self.parse_add_rest()

        else:
            self.error('выражение (число, имя, "(" или "+"/"-")')

    def parse_tail(self):
        if self.peek().kind == '=':
            self.next()
            self.parse_expr()
        else:
            self.parse_mul_rest()
            self.parse_add_rest()

    def parse_unary(self):
        kind = self.peek().kind
        if kind in ('+', '-'):
            self.next()
            self.parse_unary()
        elif kind in ('NUM', 'ID'):
            self.next()
        elif kind == '(':
            self.next()
            self.parse_expr()
            self.expect(')', '")"')
        else:
            self.error('операнд (число, имя, "(" или "+"/"-")')

    def parse_mul_rest(self):
        while self.peek().kind in ('*', ':'):
            self.next()
            self.parse_unary()

        if self.peek().kind not in ('+', '-', ';', ')', 'EOF'):
            self.error('операция, ")", ";" или конец ввода')

    def parse_add_rest(self):
        while self.peek().kind in ('+', '-'):
            self.next()
            self.parse_mul()                   # M -> U R
        if self.peek().kind not in (';', ')', 'EOF'):
            self.error('операция, ")", ";" или конец ввода')

    def parse_mul(self):
        self.parse_unary()
        self.parse_mul_rest()


def check(text):
    """Возвращает (принято?, список_ошибок)."""
    p = Parser(text)
    p.parse_program()
    return (not p.errors), p.errors


def main(argv):
    if len(argv) != 1:
        print('Использование: python rd_parser.py "строка для разбора"', file=sys.stderr)
        return 2
    text = argv[0]
    ok, errors = check(text)
    for e in errors:
        line, col = line_col(text, e.pos)
        print('  строка %d, столбец %d: %s' % (line, col, e.message), file=sys.stderr)
    print('Accepted' if ok else 'Rejected')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
