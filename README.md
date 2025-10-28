# Regex to Finite Automata Converter

Python library for converting regular expressions to finite automata and vice versa.

## Features

- **Regex → ε-NFA** (Thompson's Construction)
- **ε-NFA → NFA** (ε-closure elimination)
- **NFA → DFA** (Subset Construction)
- **DFA Minimization** (Table-filling algorithm)
- **DFA → Regex** (State elimination method)
- **String matching** via DFA

## Usage
```python
from fa_regex_lib import regex_to_min_DFA, FA_to_regex

# Convert regex to minimized DFA
dfa = regex_to_min_DFA('a*b*')

# Test string acceptance
print(dfa.does_accept('aaabbb'))  # True
print(dfa.does_accept('aba'))     # False

```
