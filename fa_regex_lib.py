class IllegalArgumentError(ValueError):
    pass

#funkcija koja ispituje da li je regex validan
# O(n) [n-dužina regexa]
def regex_validation(regex):
    stack = []
    prev_char = None

    for char in regex:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if prev_char and prev_char in '|(':
                return False
            if not stack or stack[-1] != '(':
                return False
            stack.pop()
        elif char == '|':
            if not prev_char:
                return False
            if prev_char and prev_char in '|(':
                return False
        elif char == '*':
            if not prev_char:
                return False
            if prev_char and prev_char in '|*(':
                return False

        prev_char = char

    if stack:
        return False

    return True

#pomocna funkcija za funkciju postfix, provjerava da li operator a ima veci prioritet od operatora b
# O(1)
def higherPr(a, b):
    d={
        "|" : 0,
        "." : 1,
        "*" : 2,
    }
    return d[a]>d[b]

#pretvaranje regexa iz infiksnog u postfiksni oblik (konkatenacija se oznacava sa ".")
# O(n) [n-dužina regexa]
def postfix(regexp):
    
    #if not regex_validation(regexp):
     #   raise Exception('Regex ' + regexp + ' nije validan!')
    
    temp = []
    for i in range(len(regexp)):
        if i != 0 and (regexp[i-1].isalpha() or regexp[i-1] == ")" or regexp[i-1] == "*") and (regexp[i].isalpha() or regexp[i] == "("):
            temp.append(".")
        temp.append(regexp[i])
    regexp = temp
    
    stack = []
    output = ""

    for c in regexp:
        if c.isalpha():
            output = output + c
            continue

        if c == ")":
            while len(stack) != 0 and stack[-1] != "(":
                output = output + stack.pop()
            stack.pop()
        elif c == "(":
            stack.append(c)
        elif c == "*":
            output = output + c
        elif len(stack) == 0 or stack[-1] == "(" or higherPr(c, stack[-1]):
            stack.append(c)
        else:
            while len(stack) != 0 and stack[-1] != "(" and not higherPr(c, stack[-1]):
                output = output + stack.pop()
            stack.append(c)

    while len(stack) != 0:
        output = output + stack.pop()

    return output

#pomocu ove klase predstavljamo regex kao binarno stablo
class Tree:
    def __init__(self, _type, value=None):
        self._type = _type
        self.value = value
        self.left = None
        self.right = None
    
#funkcija za formiranje stabla na osnovu datog regexa u postfiksnom obliku
# O(n) [n-dužina regexa]
def constructTree(regexp):
    stack = []
    for c in regexp:
        if c.isalpha():
            stack.append(Tree("SYMBOL", c))
        else:
            if c == "|":
                z = Tree("UNION")
                z.right = stack.pop()
                z.left = stack.pop()
            elif c == ".":
                z = Tree("CONCAT")
                z.right = stack.pop()
                z.left = stack.pop()
            elif c == "*":
                z = Tree("KLEENE")
                z.left = stack.pop()
            stack.append(z)

    return stack[0]

#klasa koja predstavlja stanje u automatu (pomocu nje se od stabla formira automat)
class FiniteAutomataState:
    def __init__(self):
        self.next_state = {}

#prolazi kroz stablo i formira automat, povratna vrijednost je "tuple" (prva vrijednost je pocetno stanje, dok je druga vrijednost završno stanje automata)
#poziva funkcije ispod, i one pozivaju ovu funkciju, sve dok se ne dođe do evalRegexSymbol, onda rezultatima uvezuju automat (sa predavanja *,|,konkatenacija)
# Pravljenje automata (funkcije do klase EpsilonNfa) ima složenost O(n) [n-broj čvorova u stablu koje vraća funkcija constructTree]
def evalRegex(et):
    if et._type == "SYMBOL":
        return evalRegexSymbol(et)
    elif et._type == "CONCAT":
        return evalRegexConcat(et)
    elif et._type == "UNION":
        return evalRegexUnion(et)
    elif et._type == "KLEENE":
        return evalRegexKleene(et)

def evalRegexSymbol(et):
    start_state = FiniteAutomataState()
    end_state   = FiniteAutomataState()
    
    start_state.next_state[et.value] = [end_state]
    return start_state, end_state

def evalRegexConcat(et):
    left_nfa  = evalRegex(et.left)
    right_nfa = evalRegex(et.right)

    left_nfa[1].next_state['ε'] = [right_nfa[0]]
    return left_nfa[0], right_nfa[1]

def evalRegexUnion(et):
    start_state = FiniteAutomataState()
    end_state   = FiniteAutomataState()

    up_nfa   = evalRegex(et.left)
    down_nfa = evalRegex(et.right)

    start_state.next_state['ε'] = [up_nfa[0], down_nfa[0]]
    up_nfa[1].next_state['ε'] = [end_state]
    down_nfa[1].next_state['ε'] = [end_state]

    return start_state, end_state

def evalRegexKleene(et):
    start_state = FiniteAutomataState()
    end_state   = FiniteAutomataState()

    sub_nfa = evalRegex(et.left)

    start_state.next_state['ε'] = [sub_nfa[0], end_state]
    sub_nfa[1].next_state['ε'] = [sub_nfa[0], end_state]

    return start_state, end_state

class EpsilonNfa:
    def __init__(self,states,alphabet=None,transitions=None,start_state=None,accept_states=None):
        if alphabet is not None and transitions is not None and start_state is not None and accept_states is not None:
            self.states=states
            self.alphabet=alphabet
            self.transitions=transitions
            self.start_state=start_state
            self.accept_states=accept_states

        else:
            regex=states
            self.states=set()
            self.alphabet=set("ε")
            self.transitions={}
            self.start_state=""
            self.accept_states=set()

            #popunjavanje alfabeta
            # O(n) [n-dužina regexa]
            for x in regex:
                if x.isalpha():
                    self.alphabet.add(x)
    #########################################################################################################################
            #upis stanja, tranzicija, finalnih i pocetnog stanja
            # O(n) 
            postfix_regex=postfix(regex)
            tr=constructTree(postfix_regex)
            fin=evalRegex(tr)
            start=fin[0]
            acc=fin[1]
            def set_values(state, states_done, symbol_table):
                if state in states_done:
                    return
                states_done.append(state)
                self.states.add("q" + str(symbol_table[state]))
                for symbol in list(state.next_state):
                    if state==start:
                        self.start_state="q" + str(symbol_table[state])
                        #self.accept_states.add(str("q" + str(symbol_table[state]))) #POCETNO STANJE=FINALNO?
                    
                    self.transitions[("q" + str(symbol_table[state]),symbol)]=set()

                    for ns in state.next_state[symbol]:
                        if ns not in symbol_table:
                            symbol_table[ns] = 1 + sorted(symbol_table.values())[-1]
                        self.transitions[("q" + str(symbol_table[state]),symbol)].add(str("q" + str(symbol_table[ns])))
                        set_values(ns, states_done, symbol_table)
 
                    if symbol_table[acc]:
                        self.accept_states.add(str("q" + str(symbol_table[acc])))
            set_values(fin[0],[],{fin[0]:0})
    ###########################################################################################################################
    # O(n) [n-broj tranzicija]
    def print_eNfa(self):
        print(">=============ε-NKA=============<")
        print("Alfabet: ", self.alphabet) 
        print("Stanja: ", self.states) 
        print("Pocetno stanje: ", self.start_state)
        print("Finalna stanja: ", self.accept_states)
        print("==========TRANZICIIJE==========")
        print("(Stanje, Simbol) = Sledeca stanja")
        el={}
        for el in self.transitions:
            print("  ",el,"  = ",self.transitions[el])

class Nfa:
    def __init__(self, eNfa:EpsilonNfa,alphabet=None,transitions=None,start_state=None,accept_states=None):
        if alphabet is not None and transitions is not None and start_state is not None and accept_states is not None:
                self.states=set(eNfa)
                self.alphabet=alphabet
                self.transitions=transitions
                self.start_state=start_state
                self.accept_states=set(accept_states)
        else:
            self.states=eNfa.states
            self.alphabet=eNfa.alphabet
            self.alphabet.discard("ε")
            self.transitions={}
            self.start_state=eNfa.start_state
            self.accept_states=eNfa.accept_states

            self.eclosure={}
            ###########################################################################################################
            def calculateEpsilonClosure(state, transitions):
                if state== "∅":
                    return set("∅")
                closure = set([state])  
                stack = [state]  

                while stack:
                    current_state = stack.pop()
                    epsilon_transitions = transitions.get((current_state, "ε"), set())

                    for next_state in epsilon_transitions:
                        if next_state not in closure:
                            closure.add(next_state)
                            stack.append(next_state)

                return closure
            
            for state in self.states:
                self.eclosure[state] = calculateEpsilonClosure(state, eNfa.transitions)
            #############################################################################################################

            def fillTransitions(epsilon_transitions):
                for state in self.states:
                    for symbol in self.alphabet:
                        self.transitions[(state, symbol)] = set()
                        p=calculateEpsilonClosure(state,epsilon_transitions)
                        u=set()
                        for pi in p:
                            toAdd=epsilon_transitions.get((pi,symbol))
                            if toAdd is not None:
                                u.update(toAdd)
                            else:
                                u.update("∅")
                        for el in u:
                            self.transitions[(state,symbol)].update(calculateEpsilonClosure(el,epsilon_transitions))
            fillTransitions(eNfa.transitions)
            for value in self.transitions.values():
                if len(value)>1 and "∅" in value:
                    value.discard("∅")
            for key, value in self.transitions.items():
                if value=={"∅"}:
                    self.transitions[key]="∅"

            acce_states=set()
            for st in self.accept_states:
                acce_states.add(st)
            for state in self.states:
                for acc_statee in acce_states:
                    if acc_statee in self.eclosure[state]:
                        self.accept_states.add(state)

    # O(n) [n-broj tranzicija]
    def print_Nfa(self):
        print(">=============NKA=============<")
        print("Alfabet: ", self.alphabet) 
        print("Stanja: ", self.states) 
        print("Pocetno stanje: ", self.start_state)
        print("Finalna stanja: ", self.accept_states)
        print("==========TRANZICIIJE==========")
        print("(Stanje, Simbol) = Sledeca stanja")
        el={}
        for el in self.transitions:
            print("  ",el,"  = ",self.transitions[el])
        
class Dfa:
    def to_regex(self):
        states_cp=self.states.copy()
        start_state_cp=self.start_state
        accept_states_cp=self.accept_states.copy()
        transitions_cp=self.transitions.copy()

        new_start="S"
        new_fin="F"
        transitions_cp[(new_start,'')]=start_state_cp
        start_state_cp=new_start
        for state in accept_states_cp:
            transitions_cp[(state,'')]=new_fin
        accept_states_cp=set({new_fin})
        
        while len(states_cp):
            removed_state=states_cp.pop() 
            in_set=set()
            out_set=set()
            self_loop=''
            key_list=list(transitions_cp)
            for key in key_list:
                if key[0]==removed_state and transitions_cp[key]==removed_state:
                    if self_loop!='':
                        self_loop=self_loop+'|'+key[1]
                    else:
                        self_loop=key[1]
                    transitions_cp.pop(key)                
                elif transitions_cp[key]==removed_state:
                    in_set.add(key)
                    transitions_cp.pop(key)
                elif key[0]==removed_state:
                    out_set.add((transitions_cp[key],key[1])) 
                    transitions_cp.pop(key)               
                else:
                    pass

            if '|' in self_loop:
                self_loop='('+self_loop+')*'
            elif self_loop!='':
                self_loop=self_loop+'*'
            else:
                pass
            
            for out_state in out_set:
                for in_state in in_set:
                    transitions_cp[(in_state[0],in_state[1]+self_loop+out_state[1])]=out_state[0]  ### REGEX BEZ UKLANJANJA
                    ### REGEX SA UKLANJANJEM
                    ########################################################################
                    """
                    if self_loop!='' and in_state[1] in self_loop:
                        transitions_cp[(in_state[0],self_loop+out_state[1])]=out_state[0]
                    elif self_loop!='' and out_state[1] in self_loop:
                        transitions_cp[(in_state[0],in_state[1]+self_loop)]=out_state[0]
                    else:
                        transitions_cp[(in_state[0],in_state[1]+self_loop+out_state[1])]=out_state[0]
                    """
                    ########################################################################
    
        s_to_f_list=list()
        for key in transitions_cp:
            if key[0]==new_start and transitions_cp[key]==new_fin and key[1]!='':
                s_to_f_list.append(key[1])
        ### REGEX SA UKLANJANJEM
        ########################################################################
        """
        to_return=''
        for one_s_to_f in s_to_f_list:
            with_star='*'+one_s_to_f
            in_other=False
            for other in s_to_f_list:
                if with_star in other:
                    in_other=True
            if not in_other:
                if to_return!='':
                    to_return=to_return+'|'+one_s_to_f
                else:
                    to_return=one_s_to_f
        """
        ########################################################################
        to_return='|'.join(s_to_f_list)    ### REGEX BEZ UKLANJANJA
        return to_return

    def is_accepting(self, state):
        return state in self.accept_states
    
    def get_next_state(self, state, symbol):
        return self.transitions.get((state, symbol))

    def does_accept(self, s):
        state = self.start_state
        for symbol in s:
            if state!=None:
                state = self.get_next_state(state, symbol)
            else:
                return False
        return self.is_accepting(state)
    
    def __init__(self, nfa:Nfa,alphabet=None, transitions=None, start_state=None, accept_states=None):
        if alphabet is not None and transitions is not None and start_state is not None and accept_states is not None:
                self.is_minimized=False
                self.states=set(nfa)
                self.alphabet=alphabet
                self.transitions=transitions
                self.start_state=start_state
                self.accept_states=set(accept_states)
                self.dead_state=""

        else:
            self.is_minimized=False
            self.states=set()
            self.accept_states=set()
            self.alphabet=nfa.alphabet
            self.transitions={}
            self.dead_state=""

            transitions_copy={}
            names={}
            i=0
            frozen_states=set()
        
            unvisited_states=[]
            unvisited_states.append(frozenset({nfa.start_state}))
            while unvisited_states:
                current_state_set=unvisited_states.pop(0)
                frozen_states.add(current_state_set)
                if current_state_set not in names:
                    names[current_state_set]=str("p"+str(i))
                    i=i+1
                for symbol in self.alphabet:
                    if current_state_set =="∅":
                        self.dead_state=names[current_state_set]
                        transitions_copy[(current_state_set,symbol)]= "∅"
                    else:
                        new_state_set=set()
                        for state in current_state_set:
                            x=nfa.transitions[(state,symbol)]
                            if isinstance(x,set):
                                new_state_set.update(x)
                            else:
                                pass
                        if new_state_set:
                            fr_new=frozenset(new_state_set)
                            transitions_copy[(current_state_set,symbol)]=new_state_set
                            if fr_new not in frozen_states:
                                unvisited_states.append(fr_new)
                        else:
                            fr_new="∅"
                            transitions_copy[(current_state_set,symbol)]="∅"
                            if fr_new not in frozen_states:
                                unvisited_states.append(fr_new)


            for symbol in self.alphabet:
                el={}
                for el in names:
                    self.states.add(names[el])
                    if el!="∅":
                        if transitions_copy[(el,symbol)]!="∅":
                            self.transitions[(names[el],symbol)]=names[frozenset(transitions_copy[(el,symbol)])]
                        else:
                            self.transitions[(names[el],symbol)]=names[transitions_copy[(el,symbol)]]
                    else:
                        self.transitions[(names[el],symbol)]=transitions_copy[(el,symbol)]

            key_s=frozenset({nfa.start_state})
            self.start_state=names[key_s]

            for myb_contains_f_state_set in names:
                for original_f_state in nfa.accept_states:
                    if original_f_state in myb_contains_f_state_set:
                        self.accept_states.add(names[myb_contains_f_state_set])
    
    def remove_unreachable_states(self):
        reachable_states=set()
        stack=[self.start_state]

        while stack:
            current_state=stack.pop()
            if current_state not in reachable_states:
                reachable_states.update({current_state})
                for symbol in self.alphabet:
                    if self.transitions[(current_state,symbol)]!="∅":
                        next_state=self.transitions[(current_state,symbol)]
                        stack.append(next_state)

        reachable_states=list(reachable_states)
        filtered_states=[state for state in self.states if state in reachable_states]
        filtered_transitions={(state,symbol):self.transitions[(state,symbol)] for (state,symbol) in self.transitions if state in filtered_states}
        filtered_accept_states=[state for state in self.accept_states if state in reachable_states]

        self.states=set(filtered_states)
        self.transitions=filtered_transitions
        self.accept_states=set(filtered_accept_states)

    def minimize(self):
        self.remove_unreachable_states()

        sorted_states=list(sorted(self.states,key=lambda state: int(state[1:]) if state[1:].isdigit() else state))
        eq_table=[[False for j in range(i)] for i in range(1,len(self.states))]
        for i in range(len(self.states)-1):
            for j in range(i+1):
                if (sorted_states[i+1] in self.accept_states and sorted_states[j] not in self.accept_states) or (sorted_states[i+1] not in self.accept_states and sorted_states[j] in self.accept_states):
                    eq_table[i][j] = True

        rows=len(eq_table)
        cols=len(eq_table[rows-1])
        while True:
            changed=False
            for j in range(cols):
                for i in range(rows):
                        if i>=j:    
                            if not eq_table[i][j]:
                                for symbol in self.alphabet:
                                    first=self.transitions[(sorted_states[j],symbol)]
                                    second=self.transitions[(sorted_states[i+1],symbol)]
                                    if first!="∅" and second!="∅":
                                        if(int(first[1:])>int(second[1:])):
                                            pom=first
                                            first=second
                                            second=pom
                                        x=sorted_states.index(second)-1 if second in sorted_states else None
                                        y=sorted_states.index(first) if (first in sorted_states and sorted_states.index(first)<=x) else None
                                        if (x!=None and y!=None):
                                            if(eq_table[x][y]):
                                                eq_table[i][j]=True
                                                changed=True
                                    elif first!="∅" and second=="∅":
                                        sec=sorted_states[i+1]
                                        if(int(first[1:])>int(sec[1:])):
                                            pom=first
                                            first=sec
                                            sec=pom
                                        x=sorted_states.index(sec)-1 if sec in sorted_states else None
                                        y=sorted_states.index(first) if (first in sorted_states and sorted_states.index(first)<=x) else None
                                        if (x!=None and y!=None):
                                            if(eq_table[x][y]):
                                                eq_table[i][j]=True
                                                changed=True
                                    elif first=="∅" and second!="∅": 
                                        fir=sorted_states[j]
                                        if(int(fir[1:])>int(second[1:])):
                                            pom=fir
                                            fir=second
                                            second=pom
                                        x=sorted_states.index(second)-1 if second in sorted_states else None
                                        y=sorted_states.index(fir) if (fir in sorted_states and sorted_states.index(fir)<=x) else None
                                        if (x!=None and y!=None):
                                            if(eq_table[x][y]):
                                                eq_table[i][j]=True
                                                changed=True
                                
                                if changed:
                                    break
                                    
                            if changed:
                                break
                if changed:
                    break
            if not changed:
                break
        
        merged_states_set=set()

        for j in range(cols):
            col_has_marked_el=False
            for i in range(rows):
                if i>=j:
                    if eq_table[i][j]==False:
                        merged_states_set.add(frozenset({sorted_states[i+1],sorted_states[j]}))
                        col_has_marked_el=True
            if not col_has_marked_el:
                merged_states_set.add(frozenset({sorted_states[j]}))

        last_row=len(eq_table)-1
        last_row_has_marked_el=False
        for z in range(cols):
            if eq_table[last_row][z]==False:
                last_row_has_marked_el=True
        if not last_row_has_marked_el:
            merged_states_set.add(frozenset({sorted_states[last_row+1]}))

        while True:
            change=False
            idx1=0
            while idx1 < len(merged_states_set):
                idx2=0
                while idx2 < len(merged_states_set):
                    first_set=list(merged_states_set)[idx1]
                    second_set=list(merged_states_set)[idx2]
                    if first_set!=second_set:
                        if not first_set.isdisjoint(second_set):
                            if first_set.issubset(second_set):
                                merged_states_set.discard(first_set)
                                change=True
                            elif first_set.issuperset(second_set):
                                merged_states_set.discard(second_set)
                                change=True
                            else:
                                merged_states_set.add(frozenset(first_set.union(second_set)))
                                merged_states_set.discard(first_set)
                                merged_states_set.discard(second_set)
                                change=True
                    idx2=idx2+1
                    if change:
                        break
                idx1=idx1+1
                if change:
                    break
            if not change:
                break

        merged_states_list=list(sorted(merged_states_set,key=lambda x:(len(x),sorted(x))))  
        name_dic={}
        minimized_states=set()
        minimized_start_state=''
        minimized_dead_state=''
        minimized_accept_states=set()
        minimized_transitions={}
        i=0
        for merged_states in merged_states_list:
            name_dic[merged_states]=str("p"+str(i))
            minimized_states.add(name_dic[merged_states])
            if self.start_state in merged_states:
                minimized_start_state=name_dic[merged_states]
            if self.dead_state in merged_states:
                minimized_dead_state=name_dic[merged_states]
            if merged_states.issubset(self.accept_states):
                minimized_accept_states.add(name_dic[merged_states])
            i=i+1
        
        merged_states_transitions={}
        for symbol in self.alphabet:
            for merged_statess in merged_states_list:
                for state in merged_statess:
                    merged_states_transitions[(merged_statess,symbol)]=self.transitions[(state,symbol)]
        
        for fs in merged_states_transitions:
            a=merged_states_transitions[fs]
            for merged_states in merged_states_list:
                if a in merged_states:
                    b=name_dic[merged_states]
                    minimized_transitions[(name_dic[fs[0]],fs[1])]=b

        self.start_state=minimized_start_state
        self.dead_state=minimized_dead_state
        self.states=minimized_states
        self.accept_states=minimized_accept_states
        self.transitions=minimized_transitions.copy()
        for el in minimized_transitions:
            if el[0]==self.dead_state or minimized_transitions[el]==self.dead_state:
                self.transitions.pop(el)
        self.states.discard(self.dead_state)
        if self.dead_state not in self.states:
            self.dead_state=""
        self.is_minimized=True

    # O(n) [n-broj tranzicija]
    def print_Dfa(self):
        print(">=============DKA=============<")
        print("Alfabet: ", self.alphabet) 
        print("Stanja: ", self.states) 
        print("Pocetno stanje: ", self.start_state)
        print("Finalna stanja: ", self.accept_states)
        if self.dead_state:
            print("Mrtvo stanje (∅): ", self.dead_state)
        print("==========TRANZICIIJE==========")
        print("(Stanje, Simbol) = Sledece stanje")
        el={}
        for el in self.transitions:
            print("  ",el,"  = ",self.transitions[el])

def regex_to_min_DFA(regex:str):
    enfa=EpsilonNfa(regex)
    nfa=Nfa(enfa)
    dfa=Dfa(nfa)
    dfa.minimize()
    return dfa

def FA_to_regex(fa):
    if isinstance(fa, Dfa):
        if not fa.is_minimized:
            fa.minimize()
        return fa.to_regex()
    elif isinstance(fa, Nfa):
        dfa=Dfa(fa)
        if not dfa.is_minimized:
            dfa.minimize()
        return dfa.to_regex()
    elif isinstance(fa, EpsilonNfa):
        nfa=Nfa(fa)
        dfa=Dfa(nfa)
        if not dfa.is_minimized:
            dfa.minimize()
        return dfa.to_regex()
    else:
        raise IllegalArgumentError("Argument nije konačni automat!")
    
dfa=regex_to_min_DFA('(abc|((ab*|ε|b*)))(acb|((ab*|ε|b*)))**|c*')
dfa.print_Dfa()

