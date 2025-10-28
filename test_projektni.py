from fa_regex_lib import regex_to_min_DFA, FA_to_regex, Nfa, EpsilonNfa, Dfa

def test_dfa():

    dfa=regex_to_min_DFA('a*b*')
    assert dfa.does_accept('')
    assert dfa.does_accept('a')
    assert dfa.does_accept('b')
    assert dfa.does_accept('ab')
    assert dfa.does_accept('aaabbb')
    assert not dfa.does_accept('aba')
    assert not dfa.does_accept('abab')

    regex=FA_to_regex(dfa)
    dfa_copy=regex_to_min_DFA(regex)
    assert dfa_copy.does_accept('')
    assert dfa_copy.does_accept('a')
    assert dfa_copy.does_accept('b')
    assert dfa_copy.does_accept('ab')
    assert dfa_copy.does_accept('aaabbb')
    assert not dfa_copy.does_accept('aba')
    assert not dfa_copy.does_accept('abab')
 

def test_dfa1():
       
    dfa=regex_to_min_DFA('a|b')
    assert not dfa.does_accept('')
    assert dfa.does_accept('a')
    assert dfa.does_accept('b')
    assert not dfa.does_accept('ab')
    assert not dfa.does_accept('aaabbb')
    assert not dfa.does_accept('aba')
    assert not dfa.does_accept('abab')

    regex=FA_to_regex(dfa)
    dfa_copy=regex_to_min_DFA(regex)
    assert not dfa_copy.does_accept('')
    assert dfa_copy.does_accept('a')
    assert dfa_copy.does_accept('b')
    assert not dfa_copy.does_accept('ab')
    assert not dfa_copy.does_accept('aaabbb')
    assert not dfa_copy.does_accept('aba')
    assert not dfa_copy.does_accept('abab')

def test_dfa2():
       
    dfa=regex_to_min_DFA('abcd*|e*')
    assert dfa.does_accept('')
    assert dfa.does_accept('abc')
    assert dfa.does_accept('abcd')
    assert dfa.does_accept('abcddd')
    assert dfa.does_accept('eee')
    assert not dfa.does_accept('ab')
    assert not dfa.does_accept('abcde')
    assert not dfa.does_accept('abce')
    assert not dfa.does_accept('abcddda')

    regex=FA_to_regex(dfa)
    dfa_copy=regex_to_min_DFA(regex)
    assert dfa_copy.does_accept('')
    assert dfa_copy.does_accept('abc')
    assert dfa_copy.does_accept('abcd')
    assert dfa_copy.does_accept('abcddd')
    assert dfa_copy.does_accept('eee')
    assert not dfa_copy.does_accept('ab')
    assert not dfa_copy.does_accept('abcde')
    assert not dfa_copy.does_accept('abce')
    assert not dfa_copy.does_accept('abcddda')

def test_enfa_to_reg():
    enfa_06_14=EpsilonNfa({"q0","q1","q2","q3","q4","q5"},{"a","b","ε"},{
('q0', 'a'): {'q1'},
('q0', "b"): {'q0'},
('q1', "ε"): {'q2','q4'},
('q1', 'b'): {'q1'},
('q2', 'a'): {'q2'},
('q2', 'b'): {'q5'},
('q3', 'a'): {'q4'},
('q4', 'a'): {'q5'},
('q4', 'b'): {'q3'},
},"q0",{"q5"})
    nfa=Nfa(enfa_06_14)
    dfa=Dfa(nfa)
    dfa.minimize()
    assert dfa.does_accept('aa')
    assert dfa.does_accept('ab')
    assert dfa.does_accept('abaa')
    assert dfa.does_accept('abbbab')

    regex=FA_to_regex(dfa)
    dfa_copy=regex_to_min_DFA(regex)
    assert dfa_copy.does_accept('aa')
    assert dfa_copy.does_accept('ab')
    assert dfa_copy.does_accept('abaa')
    assert dfa_copy.does_accept('abbbab')

def test_nfa_to_regex():
    nfa_06_10=Nfa({'q0','q1'},{'a','b'},
        {
            ('q0','a'):{'q0','q1'},
            ('q0','b'):{'q1'},
            ('q1','a'):"∅",
            ('q1','b'):{'q0','q1'},
        },'q0',{'q1'})
    dfa=Dfa(nfa_06_10)
    dfa.minimize()
    assert dfa.does_accept('aa')
    assert dfa.does_accept('ab')
    assert dfa.does_accept('aaabbb')

    regex=FA_to_regex(dfa)
    dfa_copy=regex_to_min_DFA(regex)
    assert dfa_copy.does_accept('aa')
    assert dfa_copy.does_accept('ab')
    assert dfa_copy.does_accept('aaabbb')


test_dfa()
test_dfa1()
test_dfa2()
test_enfa_to_reg()
test_nfa_to_regex()