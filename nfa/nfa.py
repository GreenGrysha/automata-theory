class NFA:
    def __init__(self, alphabet, states, accept, start,transitions):
        self.alphabet = alphabet
        self.states = states
        self.accept_states = accept
        self.start = start
        self.transitions = transitions

    def print_table(self):
        col_w = 14
        header = "state".ljust(10)
        for symbol in self.alphabet:
            header += ("delta(" + symbol + ")").ljust(col_w)
        print(header)
        print("-" * (10 + col_w * len(self.alphabet)))
        for state in self.states:
            mark = ""
            if state == self.start:
                mark = "->"
            if state in self.accept_states:
                mark += "*"
            row = (mark + state).ljust(10)
            for symbol in self.alphabet:
                targets = self.transitions.get((state, symbol), set())
                if targets:
                    cell = "{" + ",".join(sorted(targets)) + "}"
                else:
                    cell = "{}"
                row += cell.ljust(col_w)
            print(row)
        print()

    def run(self, chain) -> None:
        current_set = {self.start}
        history = [set(current_set)]
        position = 0

        while position < len(chain):
            symbol = chain[position]
            next_set = set()
            for state in current_set:
                targets = self.transitions.get((state, symbol), set())
                for t in targets:
                    next_set.add(t)
            current_set = next_set
            history.append(set(current_set))
            position += 1
            if not current_set:
                return

        accept = False
        for state in current_set:
            if state in self.accept_states:
                accept = True


        steps = []
        for s in history:
            steps.append("{" + ",".join(sorted(s)) + "}")
        trace = " -> ".join(steps)
        verdict = "ACCEPT" if accept else "REJECT"
        print(f"Цепочка {chain}")
        print(f"  Множества состояний: {trace}")
        print(f"  Результат: {verdict}")



def create_nfa():
    alphabet = ["1", "2", "3"]
    states = ["q0", "r1", "r2", "r3", "f1", "f2", "f3"]
    accept_states = {"f1", "f2", "f3"}
    start = "q0"

    table = {
        ("q0", "1"): {"q0", "r1"},
        ("q0", "2"): {"q0", "r2"},
        ("q0", "3"): {"q0", "r3"},

        ("r1", "1"): {"r1", "f1"},
        ("r1", "2"): {"r1"},
        ("r1", "3"): {"r1"},

        ("r2", "1"): {"r2"},
        ("r2", "2"): {"r2", "f2"},
        ("r2", "3"): {"r2"},

        ("r3", "1"): {"r3"},
        ("r3", "2"): {"r3"},
        ("r3", "3"): {"r3", "f3"},
    }

    return NFA(alphabet, states, accept_states, start, table)