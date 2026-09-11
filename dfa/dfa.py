class DFA:
    def __init__(self, alphabet, states, accept, start,transitions):
        self.alphabet = alphabet
        self.states = states
        self.accept_states = accept
        self.start = start
        self.transitions = transitions

    def print_table(self):
        col_w = 8
        header = "state".ljust(col_w)
        for symbol in self.alphabet:
            header += ("delta(" + symbol + ")").ljust(col_w)
        print(header)
        print("-" * (col_w * (len(self.alphabet) + 1)))
        for state in self.states:
            mark = ""
            if state == self.start:
                mark = "->"
            if state in self.accept_states:
                mark += "*"
            row = (mark + state).ljust(col_w)
            for symbol in self.alphabet:
                next_state = self.transitions[(state, symbol)]
                row += next_state.ljust(col_w)
            print(row)
        print()

    def run(self, chain) -> None:
        current_state = self.start
        path = [current_state]
        position = 0

        while position < len(chain):
            symbol = chain[position]
            if (current_state, symbol) not in self.transitions:
                print(f"Цепочка {chain}: символ {symbol} вне алфавита -> REJECT")
                return
            current_state = self.transitions[(current_state, symbol)]
            path.append(current_state)
            position += 1

        accept = current_state in self.accept_states

        trace = " -> ".join(path)
        verdict = "ACCEPT" if accept else "REJECT"
        print(f"Цепочка {chain}")
        print(f"  Путь: {trace}")
        print(f"  Результат: {verdict}")



def create_dfa():
    alphabet = ['a', 'b']
    states = ['q0', 'q1', 'q2', 'q3', 'q4']
    accept_states = ['q0', 'q1', 'q2', 'q3']
    start = 'q0'
    transitions = {
        ("q0", "a"): "q1", ("q0", "b"): "q0",
        ("q1", "a"): "q2", ("q1", "b"): "q1",
        ("q2", "a"): "q3", ("q2", "b"): "q2",
        ("q3", "a"): "q4", ("q3", "b"): "q3",
        ("q4", "a"): "q4", ("q4", "b"): "q4",
    }

    return DFA(alphabet, states, accept_states, start, transitions)


