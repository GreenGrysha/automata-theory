import sys
import re
from itertools import product


DELTA = {
    ('q0', '',  ''):  [('q1', 'Z')],
    ('q1', 'a', 'Z'): [('q1', 'AZ')],
    ('q1', 'a', 'A'): [('q1', 'AA')],
    ('q1', '',  ''):  [('q2', '')],
    ('q2', 'b', 'A'): [('q2', '')],
    ('q2', '',  'Z'): [('q3', 'Z')],
    ('q3', 'b', 'Z'): [('q3', 'BZ')],
    ('q3', 'b', 'B'): [('q3', 'BB')],
    ('q3', 'c', 'B'): [('q4', '')],
    ('q4', 'c', 'B'): [('q4', '')],
    ('q4', '',  'Z'): [('q5', '')],
}
START, FINAL = 'q0', {'q5'}


def accepts(w: str) -> bool:
    seen = set()
    todo = [(START, 0, '')]
    while todo:
        q, i, st = todo.pop()
        if (q, i, st) in seen or len(st) > len(w) + 2:
            continue
        seen.add((q, i, st))
        if i == len(w) and q in FINAL:
            return True
        for (s, r, p), moves in DELTA.items():
            if s != q:
                continue
            if r and (i >= len(w) or w[i] != r):
                continue
            if p and not st.startswith(p):
                continue
            for q2, push in moves:
                todo.append((q2, i + len(r), push + st[len(p):]))
    return False


def in_l4(w: str) -> bool:
    m = re.fullmatch(r'(a*)(b*)(c+)', w)
    if not m:
        return False
    n, bb, m_ = len(m[1]), len(m[2]), len(m[3])
    return bb == n + m_


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for s in sys.argv[1:]:
            print(repr(s), 'ПРИНЯТА' if accepts(s) else 'ОТВЕРГНУТА')
    else:
        bad = 0
        for L in range(0, 10):
            for t in product('abc', repeat=L):
                s = ''.join(t)
                if accepts(s) != in_l4(s):
                    bad += 1
                    print('ОШИБКА:', repr(s))
        print('Самотест пройден' if not bad else f'Ошибок: {bad}')
        for s in ['bc', 'abbc', 'aabbbc', 'abbbcc', '', 'abc', 'aabbc', 'bcc', 'abbcc']:
            print(f'{s!r:10} ->', 'принята' if accepts(s) else 'отвергнута')
