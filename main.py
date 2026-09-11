from dfa.dfa import create_dfa
from nfa.nfa import create_nfa


def main():
    dfa = create_dfa()
    nfa = create_nfa()

    dfa_tests = ["", "b", "aaa", "aaab", "aaaa", "ababab", "aaaab", "bbbbaaa", "aaaabaaa"]
    for chain in dfa_tests:
        dfa.run(chain)

    print()

    nfa_tests = ["12321", "123", "1231", "111", "12", "1", "", "321123"]
    for chain in nfa_tests:
        nfa.run(chain)

if __name__ == "__main__":
    main()