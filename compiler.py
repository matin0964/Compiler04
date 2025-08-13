# Kian Ghassemi 401102264
# Matin Mohammadi 401110329


from enum import Enum

class Scanner:
    def __init__(self, filename):
        self.KEYWORDS = {"if", "else", "void", "int", "while", "break", "return"}
        self.SYMBOLS = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<'}
        self.WHITESPACE = {' ','\t','\r','\v','\f'}
        self.filename  = filename 
        self.tokens = []
        self.errors = []
        self.symbolTable = set()
        self.symbolTable.update(self.KEYWORDS)
        self.lineno = 1
        self.initialize_DFA() 

        with open(filename, encoding='utf-8') as f:
            self.inputProgram = f.read()


    def initialize_DFA(self):
        self.TRANSITIONS = {
        ('START', 'LETTER'): 'ID',
        ('START', 'DIGIT'): 'NUM',
        ('START', '='): 'ASSIGN_OR_EQ',
        ('START', 'SYMBOL' ): 'SYMBOL',  
        ('START', '/' ): 'SYMBOL/',    
        ('START', '*' ): 'SYMBOL*',    
        ('SYMBOL*', 'OTHER'): 'INV_IN',  
        ('SYMBOL/', 'OTHER'): 'INV_IN',  
        ('START', 'OTHER'): 'INV_IN',
        ('ASSIGN_OR_EQ', '='): 'EQ',
        ('ASSIGN_OR_EQ', 'OTHER'): 'INV_IN',
        ('ID', 'LETTER'): 'ID',
        ('ID', 'DIGIT'): 'ID',
        ('ID', 'OTHER'): 'INV_IN',
        ('NUM', 'OTHER'): 'INV_IN',
        ('NUM', 'DIGIT'): 'NUM',
        ('NUM', 'OTHER'): 'INV_NUM',
        ('NUM', 'LETTER'): 'INV_NUM',
        }
        
        self.FINAL_STATES = {
        'ID': 'ID',
        'NUM': 'NUM',
        'EQ': 'SYMBOL',
        'ASSIGN_OR_EQ': 'SYMBOL',
        'SYMBOL': 'SYMBOL',
        'INV_IN': 'INV_IN',
        'INV_NUM': 'INV_NUM',
        'SYMBOL*': 'SYMBOL',
        'SYMBOL/': 'SYMBOL',

    }


    def char_classification(self, ch):
        if ch.isalpha(): return 'LETTER'
        elif ch.isdigit(): return 'DIGIT'
        elif ch in self.SYMBOLS: return 'SYMBOL'  # Use char itself for symbols
        elif ch in self.WHITESPACE: return 'WHITESPACE'
        elif ch in '=/*': return ch 
        elif ch == '\n': 'NEWLINE'
        else: return 'OTHER'



     

    def get_next_token(self, location):
        while location < len(self.inputProgram) and self.inputProgram[location] in self.WHITESPACE:
            location += 1

        if location >= len(self.inputProgram): 
            return ("$", "$"), location
        

        # read first char 
        ch = self.inputProgram[location]

        if ch == '\n': 
            self.lineno += 1
            return None, location + 1

        state = 'START'
        lexeme = ''
   
        while location < len(self.inputProgram):
          
        
            # comment handeling
            if (location + 1) < len(self.inputProgram) and self.inputProgram[location] == '/' and self.inputProgram[location + 1] == '*':
                lineNumber = self.lineno
                comment = ''
                if lexeme != '': break
                reserveLineno = self.lineno
                while(True):
                    if (location + 1) < len(self.inputProgram) and self.inputProgram[location] == '*' and self.inputProgram[location + 1] == '/':
                        break
                    else:
                        if location + 1 == len(self.inputProgram): 
                            if len(comment) > 7:  
                                comment = f'{comment[:7]}...'
                            self.errors.append((lineNumber,  comment, 'Unclosed comment'))
                            return None, location + 1
                    comment += self.inputProgram[location]
                    if (self.inputProgram[location] == '\n'): 
                        self.lineno += 1
                    location += 1
                location += 2
                break

            elif (location + 1) < len(self.inputProgram) and self.inputProgram[location] == '*' and self.inputProgram[location + 1] == '/':
                self.errors.append((self.lineno, '*/', 'Unmatched comment'))
                location += 2
                break


            cls = self.char_classification(self.inputProgram[location])

            if cls == 'NEWLINE':
            #    location += 1
                break
            nextState = self.TRANSITIONS.get((state, cls))
            if nextState is None:
                break
            state = nextState
            lexeme += self.inputProgram[location]
            location += 1

        if state in self.FINAL_STATES:
            tokenType = self.FINAL_STATES[state]
            if lexeme in self.KEYWORDS:
                tokenType = 'KEYWORD'
            if tokenType == 'ID':
                 if lexeme not in self.symbolTable:
                    self.symbolTable.add(lexeme)

            if (tokenType == 'INV_IN'): 
                self.errors.append((self.lineno, lexeme, 'Invalid input'))
                return None, location 
            
            if (tokenType == 'INV_NUM'):
                self.errors.append((self.lineno, lexeme, 'Invalid number'))
                return None, location 
            
            return (tokenType, lexeme), location
        else:
            return None, location 


     
    def scanning(self): 
        currentIndex = 0
        while(currentIndex < len(self.inputProgram)):
            # while(currentIndex <  len(self.inputProgram)): 
                nextToken, endToken = self.get_next_token(currentIndex)
                if nextToken: 
                    self.tokens.append((self.lineno, nextToken))
                currentIndex = endToken
    
        
  
    def generateOutputs(self): 
        with open('tokens.txt', 'w', encoding='utf-8') as f:          
            token_dict = {}
            for lineno, tokenPair in self.tokens:
                if lineno not in token_dict:
                        token_dict[lineno] = []
                token_dict[lineno].append(tokenPair)
                 
            for lineno in sorted(token_dict.keys()):
                token_line = f"{lineno}.\t" + ' '.join((f"({type}, {value})" for type, value in token_dict[lineno]))
                f.write(token_line + '\n')


        with open('lexical_errors.txt', 'w', encoding='utf-8') as f:
            if not self.errors:
                f.write('There is no lexical error.\n')
            else:
                error_dict = {}
                for lineno, errorCode, errorType in self.errors:
                    if lineno not in error_dict:
                        error_dict[lineno] = []
                    error_dict[lineno].append(f"({errorCode}, {errorType})")
            
                for lineno in sorted(error_dict.keys()):
                    error_line = f"{lineno}.\t" + ' '.join(error_dict[lineno])
                    f.write(error_line + '\n')

        with open('symbol_table.txt', 'w', encoding='utf-8') as f:
            for no, lexeme in enumerate(self.symbolTable, 1):
                f.write(f"{no}.\t{lexeme}\n")



class State:
    def __init__(self, non_terminal: str, number: int):
        self.non_terminal = non_terminal
        self.number = number
        self.transitions = {}  # symbol -> next state number

    def add_transition(self, symbol: str, next_state: int):
        self.transitions[symbol] = next_state

    def __repr__(self):
        trans = {k : v for k, v in self.transitions.items()}
        return f"State({self.non_terminal}, {self.number}): {trans}"


def parse_grammar_string(rule_str: str):
    """
    Converts 'A -> B C | D E | epsilon' into ('A', [['B', 'C'], ['D', 'E'], ['epsilon']])
    """
    left, right = rule_str.split("->")
    non_terminal = left.strip()
    alternatives = right.strip().split("|")
    productions = []
    for alt in alternatives:
        tokens = alt.strip().split()
        if len(tokens) == 1 and tokens[0].lower() == "epsilon":
            productions.append(["epsilon"])
        else:
            productions.append(tokens)
    return non_terminal, productions


def build_state_machines_from_string(grammar_str: str) -> dict:
    """
    Takes a full grammar string with multiple lines and builds state machines.
    Each machine has minimal states, with a shared final state.
    """
    state_machines = {}
    rules = [line.strip() for line in grammar_str.strip().splitlines() if line.strip()]

    for rule in rules:
        non_terminal, productions = parse_grammar_string(rule)
        states = []
        start_state = State(non_terminal, 0)
        states.append(start_state)

        # Pre-allocate final state
        final_state_num = 1
        final_state = State(non_terminal, final_state_num)
        states.append(final_state)

        for prod in productions:
            if prod == ["epsilon"]:
                states[0].add_transition("epsilon", final_state_num)
                continue

            prev = 0
            for i, symbol in enumerate(prod):
                if symbol == "EPSILON":
                    symbol = "epsilon"

                # If last symbol, point to final state
                if i == len(prod) - 1:
                    states[prev].add_transition(symbol, final_state_num)
                else:
                    # Intermediate state
                    new_state_num = len(states)
                    states.append(State(non_terminal, new_state_num))
                    states[prev].add_transition(symbol, new_state_num)
                    prev = new_state_num

        state_machines[non_terminal] = states

    return state_machines




grammar_string = "Program -> DeclarationList $\n\
DeclarationList -> Declaration DeclarationList | EPSILON\n\
Declaration -> DeclarationInitial DeclarationPrime\n\
DeclarationInitial -> #push_ss TypeSpecifier #push_ss ID\n\
DeclarationPrime -> FunDeclarationPrime | VarDeclarationPrime\n\
VarDeclarationPrime -> ; #dec_var  | [ NUM ] ; \n\
FunDeclarationPrime -> #dec_func ( Params ) #param_det CompoundStmt #cls_func \n\
TypeSpecifier -> int | void\n\
Params -> #push_ss int #push_ss ID ParamPrime ParamList | void\n\
ParamList -> , Param ParamList | EPSILON\n\
Param -> DeclarationInitial ParamPrime\n\
ParamPrime -> [ ] #dec_pnt | EPSILON #dec_varParam \n\
CompoundStmt -> {  DeclarationList StatementList  }\n\
StatementList -> Statement StatementList | EPSILON\n\
Statement -> ExpressionStmt | CompoundStmt | SelectionStmt | IterationStmt | ReturnStmt\n\
ExpressionStmt -> Expression ; | break  ; | ;\n\
SelectionStmt -> if ( Expression ) #save  Statement #jpf_save else   Statement #jp \n\
IterationStmt -> while  ( Expression )  Statement  \n\
ReturnStmt -> return ReturnStmtPrime\n\
ReturnStmtPrime -> ; #return_j| Expression #save_retval ;\n\
Expression -> SimpleExpressionZegond |  #pid ID B  \n\
B -> = Expression #assign | [ Expression ]  H | SimpleExpressionPrime\n\
H -> = Expression #assign  | G D C\n\
SimpleExpressionZegond -> AdditiveExpressionZegond C\n\
SimpleExpressionPrime -> AdditiveExpressionPrime C\n\
C -> Relop AdditiveExpression #comp  | EPSILON\n\
Relop ->  #push_sss < | #push_ss ==\n\
AdditiveExpression -> Term D\n\
AdditiveExpressionPrime -> TermPrime D\n\
AdditiveExpressionZegond -> TermZegond D\n\
D -> Addop Term  D | EPSILON\n\
Addop ->  + |  -\n\
Term -> SignedFactor G\n\
TermPrime -> SignedFactorPrime G\n\
TermZegond -> SignedFactorZegond G\n\
G -> * SignedFactor  G | EPSILON\n\
SignedFactor -> + Factor | - Factor | Factor\n\
SignedFactorPrime -> FactorPrime\n\
SignedFactorZegond -> + Factor | - Factor | FactorZegond\n\
Factor -> ( Expression ) |  ID VarCallPrime | #push_num NUM\n\
VarCallPrime ->  ( #args_begin Args  ) #end_args | VarPrime\n\
VarPrime -> [ Expression ]  | EPSILON\n\
FactorPrime -> ( #args_begin Args ) #end_args| EPSILON\n\
FactorZegond -> ( Expression ) | #push_num NUM\n\
Args -> ArgList | EPSILON\n\
ArgList -> Expression ArgListPrime\n\
ArgListPrime -> , Expression ArgListPrime | EPSILON"




class Parser:
    def __init__(self, filename):
        self.state_machine = build_state_machines_from_string(grammar_string)
        self.filename  = filename
        self.scanner  = Scanner(filename)
        self.code_generator = CodeGenerator() # todo,
        self.parse_tree = []
        self.syntax_erros = []
        self.tree_depth = -1
        self.First_set  = {
        "Program": ["int", "void", "EPSILON"],
        "DeclarationList": ["int", "void", "EPSILON"],
        "Declaration": ["int", "void"],
        "DeclarationInitial": ["int", "void"],
        "DeclarationPrime": [";", "[", "(",],
        "VarDeclarationPrime": [";", "["],
        "FunDeclarationPrime": ["("],
        "TypeSpecifier": ["int", "void"],
        "Params": ["int", "void"],
        "ParamList": [",", "EPSILON"],
        "Param": ["int", "void"],
        "ParamPrime": ["[", "EPSILON"],
        "CompoundStmt": ["{"],
        "StatementList": ["ID", ";", "NUM", "(", "{", "break", "if", "while", "return", "+", "-", "EPSILON"],
        "Statement": ["ID", ";", "NUM", "(", "{", "break", "if", "while", "return", "+", "-"],
        "ExpressionStmt": ["ID", ";", "NUM", "(", "break", "+", "-"],
        "SelectionStmt": ["if"],
        "IterationStmt": ["while"],
        "ReturnStmt": ["return"],
        "ReturnStmtPrime": ["ID", ";", "NUM", "(", "+", "-"],
        "Expression": ["ID", "NUM", "(", "+", "-"],
        "B": ["[", "(", "==" ,"=", "+", "-", "<", "*", "EPSILON"],
        "H": ["=", "*", "+", "-", "<", "==", "EPSILON"],
        "SimpleExpressionZegond": ["NUM", "(", "+", "-"],
        "SimpleExpressionPrime": ["(", "+", "-", "<", "==", "EPSILON", "*"],
        "C": ["<", "==", "EPSILON"],
        "Relop": ["<", "=="],
        "AdditiveExpression": ["ID", "NUM", "(", "+", "-"],
        "AdditiveExpressionPrime": ["(", "+", "-", "*", "EPSILON"],
        "AdditiveExpressionZegond": ["NUM", "(", "+", "-"],
        "D": ["+", "-", "EPSILON"],
        "Addop": ["+", "-"],
        "Term": ["ID", "NUM", "(", "+", "-"],
        "TermPrime": ["(", "*", "EPSILON"],
        "TermZegond": ["NUM", "(", "+", "-"],
        "G": ["*", "EPSILON"],
        "SignedFactor": ["ID", "NUM", "(", "+", "-"],
        "SignedFactorPrime": ["(", "EPSILON"],
        "SignedFactorZegond": ["NUM", "(", "+", "-"],
        "Factor": ["ID", "NUM", "("],
        "VarCallPrime": ["(", "[", "EPSILON"],
        "VarPrime": ["[", "EPSILON"],
        "FactorPrime": ["(", "EPSILON"],
        "FactorZegond": ["NUM", "("],
        "Args": ["ID", "NUM", "(", "+", "-", "EPSILON"],
        "ArgList": ["ID", "NUM", "(", "+", "-"],
        "ArgListPrime": [",", "EPSILON"]
        }

        self.Follow_set = {
            "Program": ["$"],
            "DeclarationList": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "$"],
            "Declaration": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "int", "void","$"],
            "DeclarationInitial": ["[", "(", ")" , ",", ";"],
            "DeclarationPrime": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "int", "void", "$"],
            "VarDeclarationPrime": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "int", "void", "$"],
            "FunDeclarationPrime": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "int", "void", "$"],
            "TypeSpecifier": ["ID"],
            "Params": [")"],
            "ParamList": [")"],
            "Param": [")", ","],
            "ParamPrime": [")", ","],
            "CompoundStmt": ["ID", ";", "NUM", "(", "}", "{", "int", "void", "break", "if", "else", "while", "return", "+", "-", "$"],
            "StatementList": ["}"],
            "Statement": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-"],
            "ExpressionStmt": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-"],
            "SelectionStmt": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-"],
            "IterationStmt": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-"],
            "ReturnStmt": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-"],
            "ReturnStmtPrime": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-"],
            "Expression": [";", "]", ")", ","],
            "B": [";", "]", ")", ","],
            "H": [";", "]", ")", ","],
            "SimpleExpressionZegond": [";", "]", ")", ","],
            "SimpleExpressionPrime": [";", "]", ")", ","],
            "C": [";", "]", ")", ","],
            "Relop": ["ID", "+", "-", "NUM", "("],
            "AdditiveExpression": [";", "]", ")", ","],
            "AdditiveExpressionPrime": [";", "]", ")", ",", "<", "=="],
            "AdditiveExpressionZegond": [";", "]", ")", ",", "<", "=="],
            "D": [";", "]", ")", ",", "<", "=="],
            "Addop": ["ID", "NUM", "(" "+", "-"],
            "Term": [";", "]", ")", ",", "<", "==", "+", "-"],
            "TermPrime": [";", "]", ")", ",", "<", "==", "+", "-"],
            "TermZegond": [";", "]", ")", ",", "<", "==", "+", "-"],
            "G": [";", "]", ")", ",", "<", "==", "+", "-"],
            "SignedFactor": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "SignedFactorPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "SignedFactorZegond": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "Factor": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "VarCallPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "VarPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "FactorPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "FactorZegond": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "Args": [")"],
            "ArgList": [")"],
            "ArgListPrime": [")"]
        }
        self.terminals = self.scanner.KEYWORDS.union(self.scanner.SYMBOLS, {"NUM", "ID", "=", "==", "*", "$"})
        self.current_state = ("Program", 0)
        self.stateList = [self.current_state] # stack for tokens of Input
        self.parse_tree.append("Program")
        self.depthSit = [False] * 1000
        

    def getTokens(self): 
        currentIndex = 0
        nextToken = (None, None)
        while(self.stateList):   
            nextToken, endToken = self.scanner.get_next_token(currentIndex)
            if nextToken:  
                check_token = nextToken[0]
                if check_token == "SYMBOL" or check_token == "KEYWORD": 
                    check_token = nextToken[1]
                state = None
                flag = 0
                while not state in self.terminals:
                    flag = 0

                    state, number = self.call(check_token, nextToken[1])
                    if state is None: # Panic mode NT mode 
                        flag = self.recover(check_token)
                        if flag == 1: break  
                        elif flag == 2: continue
                        elif flag == 3: break
                    
                    else:
                        if state in self.terminals:
                            break       

                        self.stateList.pop()
                        self.stateList.append((self.current_state[0], number))   

                                       

                        self.tree_depth += 1 
                        self.add_tree_node(state)

                        if state != "epsilon":
                            self.stateList.append((state, 0))
                                
                        else: 
                            self.tree_depth -= 1 

                        self.balanceStateList()
                        self.current_state = self.stateList[-1]
                        
                if flag == 1:
                    currentIndex = endToken
                    continue  
                elif flag == 3:
                    break

                # terminal mode
                if self.match(state, check_token): 
                    self.stateList.pop()
                    self.stateList.append((self.current_state[0], number)) 
                    self.tree_depth += 1
                    self.add_tree_node(nextToken)
                    self.tree_depth -= 1
                    self.balanceStateList()

                else: # Panic mode case 3
                    next_link = list(self.state_machine[self.current_state[0]][self.current_state[1]].transitions.keys())[0]
                    self.stateList.pop()  
                    self.stateList.append((self.current_state[0], 
                            self.state_machine[self.current_state[0]][self.current_state[1]].transitions[next_link]))

                    self.balanceStateList()
                    if(state == '$'):
                        self.parse_tree.append('$')

                    else:
                        self.syntax_erros.append(f'#{self.scanner.lineno} : syntax error, missing {state}')
                    if(self.stateList): self.current_state = self.stateList[-1]
                    continue


                if(self.stateList): self.current_state = self.stateList[-1]

            else: nextToken = (None, None)
            currentIndex = endToken
                

    def match(self, token, state): 
        if token == state: return True
        else: return False
    
    def recover(self, token):
        state = self.current_state[0]
         # flags:  0 1 -> break 2 -> continue
        if not token in self.Follow_set[state] and token != '$':
     
            self.stateList.pop()
            self.stateList.append((self.current_state[0],0))
            self.current_state = self.stateList[-1]
            self.syntax_erros.append(f'#{self.scanner.lineno} : syntax error, illegal {token}')
            return 1
        elif token in self.Follow_set[state]:
            self.stateList.pop()
            self.parse_tree.pop()
            self.tree_depth -= 1
            self.balanceStateList()
            self.current_state = self.stateList[-1]
            self.syntax_erros.append(f'#{self.scanner.lineno} : syntax error, missing {state}')
            return 2
        elif token == '$':
            self.parse_tree.pop()
            l = self.scanner.lineno + 1
            if(self.scanner.inputProgram[-1] == '\n'): 
                l = l - 1
            self.syntax_erros.append(f'#{l} : syntax error, Unexpected EOF')
            return 3

        
        return 0
 

    def call(self, input_token, actionSymbol_token=None):
        if len(self.state_machine[self.current_state[0]][self.current_state[1]].transitions.keys()) == 1:
            next_state = list(self.state_machine[self.current_state[0]][self.current_state[1]].transitions)[0]
            if next_state.startswith("#"):
                self.code_generator.code_gen(next_state[1:], actionSymbol_token)
                number = self.state_machine[self.current_state[0]][self.current_state[1]].transitions[next_state]
                self.stateList.pop()
                self.stateList.append((self.current_state[0], number))   
                self.current_state = self.stateList[-1]

        if len(self.state_machine[self.current_state[0]][self.current_state[1]].transitions.keys()) == 1: 
            next_state = list(self.state_machine[self.current_state[0]][self.current_state[1]].transitions)[0]
            return next_state, self.state_machine[self.current_state[0]][self.current_state[1]].transitions[next_state]
        
        for key  in self.state_machine[self.current_state[0]][self.current_state[1]].transitions.keys(): 
            number = self.current_state[1]
            actionKey = None
            if key.startswith("#"):
                actionKey = key[1:]
                number = self.state_machine[self.current_state[0]][self.current_state[1]].transitions[key]
                key = list(self.state_machine[self.current_state[0]][number].transitions)[0]

            if key in self.terminals:
                if input_token == key: 
                    if actionKey: self.code_generator.code_gen(actionKey, actionSymbol_token)
                    return key,  self.state_machine[self.current_state[0]][number].transitions[key]
            elif key != "epsilon" and  (input_token in self.First_set[key] or
                                         (input_token in self.Follow_set[key] and 
                                                                               "EPSILON" in self.First_set[key])) :
                if actionKey: self.code_generator.code_gen(actionKey, actionSymbol_token)
                return key,  self.state_machine[self.current_state[0]][number].transitions[key]
            
            elif key == "epsilon" and input_token in self.Follow_set[self.current_state[0]]:
                if actionKey: self.code_generator.code_gen(actionKey, actionSymbol_token)
                return key,  self.state_machine[self.current_state[0]][number].transitions[key] 
          
          
        return None, None
    

    def add_tree_node(self, node):
        if isinstance(node, tuple) and len(node) == 2:
            if  node[0] == '$': 
                node = "$"
            else: 
                node = "(" + node[0] + ', ' + node[1] +  ") "
        
        charParent = None
        self.depthSit[self.tree_depth] = False

        if self.stateList[-1][1] == 1:
            charParent = '└── '
            self.depthSit[self.tree_depth] = True
        else :
            charParent =  '├── '

        prefix = ''.join( ('│   ' if self.depthSit[i] == False else '    ') for i in range(0, self.tree_depth))

        self.parse_tree.append(f"{prefix}{charParent}{node}")


    def balanceStateList(self): 
        if not self.stateList:
            return
        while(self.stateList[-1][1] == 1): # final state of diagram
                self.stateList.pop()
                self.tree_depth -= 1

                if len(self.stateList) == 0: return 

    def write_outputs(self):
        with open(f'parse_tree.txt', 'w') as f:
            for line in self.parse_tree:
                f.write(line + '\n')
        with open(f'syntax_errors.txt', 'w') as f: 
            if (len(self.syntax_erros) == 0): 
                f.write("There is no syntax error.")
            else:
                for line in self.syntax_erros: 
                    f.write(line + '\n')


class ActionSymbols(Enum): 
    PUSH_SS = "push_ss"
    PARAM_INFO = "param_det"
    CLOSE_FUNC = "cls_func"
    DECLARE_POINTER = "dec_pnt"
    DECLARE_VAR = "dec_var"
    DECLAARE_VAR_PARAM = "dec_varParam"
    DECLARE_FUNC = "dec_func"
    DECLARE_ARRAY = "dec_arr"
    SAVE_SCOPE = "save_scope"
    BACK_SCOPE = "back_scope"
    SAVE_BREAK = "save_b" 
    JUMP_IF_FALSE = "jpf_save"
    JUMP = "jp"
    SAVE = "save"
    WHILE_LABEL = "while_label"
    SAVE_WHILE_JUMP = "save_while_jp"
    END_WHILE = "end_while"
    RETURN_JUMP = "return_j"
    SAVE_RETURNVALUE = "save_retval"
    PRINT = "print"
    ASSIGN = "assign"
    ARRAY_ADDRESS = "arr_addr"
    COMPARE = "comp"
    MULTIPLY = "mult"
    ADD_SUB = "add_sub"
    PID = "pid"
    ARGS_BEGIN = "args_begin"
    END_ARGS = "end_args"
    PUSH_NUM = "push_num"
    POP_SS = "pop_ss"

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.memory = Memory(ProgramBlock(0,500), DataBlock(500, 10000))
        self.ss = []
        self.symbol_table = SymbolTable()
        self.global_scope = {}
        self.current_scope = self.global_scope
        self.current_function = None  # current function being processed
        self.all_scopes = {'global': self.global_scope}  # dictionary of scopes



    def code_gen(self, a_symbol, token=None):
        if a_symbol == "push_sss":
            a_symbol = "push_ss"
        
        print(f"Action: {a_symbol}, stack: {self.ss}\n")
        action_symbol = ActionSymbols(a_symbol)
        match action_symbol: 
            case ActionSymbols.PUSH_SS:
                self.push_ss_subroutine(token)
            case ActionSymbols.DECLARE_VAR:
                self.declare_var_subroutine()
            case ActionSymbols.DECLAARE_VAR_PARAM:
                self.declare_var_subroutine(False)
            case ActionSymbols.PARAM_INFO:
                self.param_info_subroutine()
            case ActionSymbols.DECLARE_FUNC:
                self.declare_func_subroutine()
            case ActionSymbols.DECLARE_POINTER:
                self.declare_pointer_subroutine()
            case ActionSymbols.DECLARE_ARRAY:
                self.declare_array_subroutine()
            case ActionSymbols.CLOSE_FUNC:
                self.close_func_subroutine()
            case ActionSymbols.SAVE_SCOPE:
                self.save_scope_subroutine()
            case ActionSymbols.BACK_SCOPE:
                self.back_scope_subroutine()
            case ActionSymbols.SAVE_BREAK:
                self.save_break_subroutine()
            case ActionSymbols.JUMP_IF_FALSE:
                self.jump_if_false_subroutine()
            case ActionSymbols.JUMP:
                self.jump_subroutine()
            case ActionSymbols.SAVE:
                self.save_subroutine()
            case ActionSymbols.WHILE_LABEL:
                self.while_label_subroutine()
            case ActionSymbols.SAVE_WHILE_JUMP:
                self.save_while_jump_subroutine()
            case ActionSymbols.END_WHILE:
                self.end_while_subroutine()
            case ActionSymbols.RETURN_JUMP:
                self.return_jump_subroutine()
            case ActionSymbols.SAVE_RETURNVALUE:
                self.save_return_value_subroutine()
            case ActionSymbols.PRINT:
                self.print_subroutine()
            case ActionSymbols.ASSIGN:
                self.assign_subroutine()
            case ActionSymbols.ARRAY_ADDRESS:
                self.array_address_subroutine()
            case ActionSymbols.COMPARE:
                self.compare_subroutine()
            case ActionSymbols.MULTIPLY:
                self.multiply_subroutine()
            case ActionSymbols.ADD_SUB:
                self.add_sub_subroutine(a_symbol)
            case ActionSymbols.PID:
                self.pid_subroutine(token)
            case ActionSymbols.ARGS_BEGIN:
                self.args_begin_subroutine()
            case ActionSymbols.END_ARGS:
                self.end_args_subroutine()
            case ActionSymbols.PUSH_NUM:
                self.push_num_subroutine(token)
            case ActionSymbols.POP_SS:
                self.pop_ss_subroutine()
        print(f"Stack after action: {self.ss}, and PB: {self.memory.get_pb().block}\n")

    # @correct
    def push_ss_subroutine(self, token):
        # print(token)
        self.ss.append(token)  # push token to stack

    # @correct
    def declare_var_subroutine(self, flag=True):
        lexeme = self.ss.pop(-1)  # get variable name
        type = self.ss.pop(-1)  # get type of variable
        self.memory.get_db().get_temp()  # get a temp variable
        self.memory.get_db().add_data(lexeme, type)
        self.current_scope[lexeme] = self.memory.get_db().get_data(lexeme) 
        if flag: self.memory.get_pb().add_instruction(("ASSIGN", '#0', self.memory.get_db().get_data(lexeme),''))  # add data to data block
        # todo 
    # @correct
    def save_subroutine(self,):
        self.ss.append(self.memory.get_pb().get_index()) # current line of pb
        self.memory.get_pb().increment_index()  # increment pb index

    # @correct
    def jump_if_false_subroutine(self,):
        idx = self.memory.get_pb().get_index()
        address = self.ss.pop(-1)
        istra = ["jpf", self.ss.pop(-1), idx + 1, None]  # jpf instruction
        self.memory.get_pb().add_instruction(istra, address)  # add instruction to pb

        self.ss.append(self.memory.get_pb().get_index()) # current line of pb
        self.memory.get_pb().increment_index()  # increment pb index

    # @correct
    def jump_subroutine(self):
        idx = self.memory.get_pb().get_index()
        instra = ["jp", idx, None, None]  # jp instruction
        self.memory.get_pb().add_instruction(instra, self.ss.pop(-1))  # add instruction to pb

    # @correct
    def pid_subroutine(self, token):
        if token == 'output':
            self.ss.append('PRINT')
            return
        
        p = self.current_scope[token]  # get data from data block
        # print(f"PID: {token}, data: {p}")
        self.ss.append(p)

    # @correct
    def push_num_subroutine(self, token):
        # print(f"PUSH_NUM: {token}")
        self.ss.append('#' + token)

    # @correct
    def compare_subroutine(self,):
        t = self.memory.get_db().get_temp()  # get a temp variable 
        opr2 = self.ss.pop(-1)  # get second operand
        op = self.ss.pop(-1) # get operator
        opr1 = self.ss.pop(-1) # get first operand
        if op == '<':
            op = 'LT'
        elif op == '==':
            op = 'EQ'

        instra = (op, opr1, opr2, t)
        self.ss.append(t)
        self.memory.get_pb().add_instruction(instra)  # add instruction to pb

    # @correct
    def assign_subroutine(self,):
        in1 = self.ss.pop(-1)  # get first operand
        in2 = self.ss.pop(-1)  # get second operand
        instra = ["ASSIGN", in1, in2, None]  # assign instruction
        self.memory.get_pb().add_instruction(instra)  # add instruction to pb

    # @correct
    def args_begin_subroutine(self):
        if self.ss and self.ss[-1] == 'PRINT':
            return 
        else: 
            self.ss.append("ARGUMENTS")

    # @correct
    def end_args_subroutine(self):
        args = []
        if 'ARGUMENTS' in self.ss: 
            while self.ss[-1] != 'ARGUMENTS':
                arg = self.ss.pop(-1)  # pop arguments from stack
                args.append(arg)

        elif 'PRINT' in self.ss:
             while self.ss[-1] != 'PRINT':
                arg = self.ss.pop(-1)  # pop arguments from stack
                args.append(arg)

        args = args[::-1]  # reverse the order of arguments
        argType = self.ss.pop(-1)  # pop 'ARGUMENTS' or 'PRINT' from stack

        if argType == 'PRINT':
            instra = ["PRINT", args[0], None, None]  # print instruction
            self.memory.get_pb().add_instruction(instra)  # add instruction to pb
            return
        # todo of calling function 

    # @correct
    def close_func_subroutine(self,):
        self.current_scope = self.all_scopes['global']  # reset current scope to global
        self.current_function = None  # reset current function
        # self.return_jump_subroutine()

    # @correct
    def declare_func_subroutine(self,):
        lexeme = self.ss.pop(-1)
        data_type = self.ss.pop(-1)  # get type of function
        self.current_scope = {}
        self.memory.get_db().add_data(lexeme, data_type, 1, True)  # add function to data block
        self.global_scope[lexeme] = self.memory.get_db().get_data(lexeme)  # add function to global scope
        self.current_function = lexeme
        self.all_scopes[lexeme] = self.current_scope  # add function to all scopes
        
        # if lexeme == 'main':
            # todo: main function special case

        self.ss.append(lexeme)  # push function name to stack

    # @correct
    def param_info_subroutine(self,):
        name = self.ss.pop(-1)
        # semantic analysis for parameter
        # update symbol table with parameter info
        pass
    

    def declare_pointer_subroutine(self,):
        lexeme = self.ss.pop(-1)
        self.ss.pop(-1)
        # semantic analysis for pointer
        self.memory.get_db().add_data(lexeme, 'array')
        # update symbol table with pointer info
        self.current_scope[lexeme] = self.memory.get_db().get_data(lexeme)  # add data to current scope

        pass
    

    def return_jump_subroutine(self):
        t = self.memory.get_db().get_temp()
        instra1 = ("ADD", self.ss.pop(-1), f'#{4}', t)  # add instruction
        instra2 = ("ASSIGN", '@' + str(t), t, '')  # assign instruction
        instra3 = ("JP", '@' + str(t), None, None)  # jump instruction
      
        self.memory.get_pb().add_instruction(instra1)
        self.memory.get_pb().add_instruction(instra2)
        self.memory.get_pb().add_instruction(instra3)

    def save_return_value_subroutine(self):
        ret_val = self.ss.pop(-1)
        t = self.memory.get_db().get_temp()
        instra = ("ASSIGN", '@' + str(self.ss.pop(-1)), t, '')  # assign instruction
        instra2 = ["ASSIGN", ret_val, '@' + str(t), None]
        self.memory.get_pb().add_instruction(instra)
        self.memory.get_pb().add_instruction(instra2)  # add instruction to pb
        
        self.return_jump_subroutine()  # return jump instruction


    def declare_array_subroutine(self,):
        lexeme = self.ss.pop(-1)  # get type of variable
        size = self.ss.pop(-1)  # get variable name
        type = self.ss.pop(-1)  # get type of variable
        self.memory.get_db().add_data(lexeme, type, int(size))  # add data to data block
        # todo
        pass
    
    def save_scope_subroutine(self,):
        pass
    
    def back_scope_subroutine(self,):
        pass

    def save_break_subroutine(self,):
        self.ss.append(self.memory.get_pb().get_index()) # current line of pb
        self.memory.get_pb().increment_index()  # increment pb index
        # todo : > 1 break statement

    def while_label_subroutine(self,):
        self.ss.append(self.memory.get_pb().get_index())

    def save_while_jump_subroutine(self,):
        self.ss.append(self.memory.get_pb().get_index())
        self.memory.get_pb().increment_index()


    def end_while_subroutine(self,):
        idx = self.memory.get_pb().get_index()
        addr = int(self.ss.pop(-1))
        instruction1 = ["JPF", self.ss.pop(-1), idx + 1, None]
        instruction2 = ["JP", self.ss.pop(-1), None, None]
        self.memory.get_pb().add_instruction(instruction1, addr)
        self.memory.get_pb().add_instruction(instruction2)


   
    def print_subroutine(self,):
        if len(self.ss) > 0: content = self.ss.pop(-1)
        content = 0; # todo
        instra = ["PRINT", content, None, None]
        self.memory.get_pb().add_instruction(instra)  # add instruction to pb
        



    def array_address_subroutine(self):
        t1 = self.memory.get_db().get_temp()
        t2 = self.memory.get_db().get_temp()
        off = self.ss.pop(-1)  # get offset
        base = self.ss.pop(-1)  # get base address

        instra = ('MULT', '#4', off, base) # int as 4
        self.memory.get_pb().add_instruction(instra)  # multiply instruction

        addInstra = None
        if str(base).startswith('@'):
            t3 = self.memory.get_db().get_temp()
            instra = ('ASSIGN', base, t3, '')
            self.memory.get_pb().add_instruction(instra)  # assign instruction

            addInstra = ('ADD', t3, t1, t2)
        else:
            addInstra = ('ADD', '#' + str(base), t1, t2)

        self.memory.get_pb().add_instruction(addInstra)  # add instruction
        self.ss.append('@' + str(t2))


    def multiply_subroutine(self,):
        # todo type matching for semantic analysis
        t = self.memory.get_db().get_temp()  # get temp
        instra = ["MULT",self.ss.pop(-1), self.ss.pop(-1), t]  # multiply instruction]
        self.memory.get_pb().add_instruction(instra)  # add instruction to pb
        self.ss.append(t)  # push temp to stack
        

    def add_sub_subroutine(self, action):
        op1 = self.ss.pop(-1)
        operation = self.ss.pop(-1)
        op2 = self.ss.pop(-1)
        R = self.memory.get_db().get_temp()
        op = "ADD" if operation == '+' else "SUB"
        instruction = [op, op2, op1, R]
        self.memory.get_pb().add_instruction(instruction)
        self.ss.append(R)



   




    def pop_ss_subroutine(self):
        self.ss.pop(-1)

    def write_outputs(self):
        with open(f'output.txt', 'w') as f:
            sortInstructions = sorted(self.memory.get_pb().block.items())
            for items in sortInstructions:
                f.write(str(items[0]) + '\t' + str(items[1]) + '\n')
      





# Namjoo's code:
# class Symbol:
#     def __init__(self, address=None, lexeme=None, symbol_type=None, size=0, param_count=0):
#         self.address = address
#         self.lexeme = lexeme
#         self.symbol_type = symbol_type
#         self.size = size
#         self.param_count = param_count
#         self.param_symbols = []
#         self.is_initialized = False
#         self.is_function = False
#         self.is_array = False
#
#
# class SymbolTable:
#     def __init__(self, codegen: "CodeGen"):
#         self.scopes = [[]]
#         self.codegen = codegen
#
#     def find_address(self, lexeme, check_declaration=False, force_declaration=False):
#         return self.find_symbol(lexeme, check_declaration, force_declaration).address
#
#     def find_symbol(self, lexeme, check_declaration=False, force_declaration=False, prevent_add=False):
#         address = -1
#         result_symbol = None
#         if not force_declaration:
#             for scope in reversed(self.scopes):
#                 for symbol in scope:
#                     if symbol.lexeme == lexeme:
#                         address = symbol.address
#                         result_symbol = symbol
#                         break
#                 if result_symbol:
#                     break
#         if address == -1 and not prevent_add:
#             if check_declaration:
#                 raise SemanticException(SCOPE_SEMANTIC_ERROR.format(lexeme))
#             address = self.codegen.get_next_data_address()
#             result_symbol = self.add_symbol(lexeme=lexeme, address=address)
#         return result_symbol
#
#     def find_symbol_by_address(self, address):
#         result_symbol = None
#         for scope in self.scopes[::-1]:
#             for symbol in scope:
#                 if symbol.address == address:
#                     result_symbol = symbol
#                     break
#         return result_symbol
#
#     def add_symbol(self, lexeme, address):
#         symbol = Symbol(lexeme=lexeme, address=address)
#         self.scopes[-1].append(symbol)
#         return symbol
#
#     def remove_symbol(self, lexeme):
#         i = 0
#         is_found = False
#         for symbol in self.scopes[-1]:
#             if symbol.lexeme == lexeme:
#                 is_found = True
#                 break
#             i += 1
#         if is_found:
#             self.scopes[-1].pop(i)

class Symbol:
    def __init__(self, address = None, lexeme = None,):
        self.address = address
        self.lexeme = lexeme
class SymbolTable:
    def __init__(self,):
        self.scopes = [[]]

    def find_symbol(self, lexeme):
        address = -1
        for scope in reversed(self.scopes):
            for symbol in scope:
                if symbol.lexeme == lexeme:
                    address = symbol.address
                    return address
        return None

    def find_address(self, token): # todo
        return self.find_symbol(token)

    def find_symbol_by_address(self, address):
        for scope in reversed(self.scopes):
            for symbol in scope:
                if symbol.address == address:
                    return symbol
        return None
    def add_symbol(self, address, lexeme):
        symbol = Symbol(address, lexeme)
        self.scopes[-1].append(symbol)
        return symbol

    # def remove_symbol(self, lexeme):
    #   pass

class Memory:
    def __init__(self, program_block, data_block):
        self.pb = program_block
        self.db = data_block

    def get_pb(self):
        return self.pb
    
    def get_db(self):
        return self.db
    


class ProgramBlock:
    def __init__(self, base, limit):
        self.index = 0
        self.base = base
        self.limit = limit
        self.block = {}


    def add_instruction(self, instruction, address=None):
        if address == None:
            self.block[self.index] = instruction
            self.increment_index()
        else:
            self.block[address] = instruction

         # todo


    def get_index(self):
        return self.index
    
    def increment_index(self, num=1):
        if self.index + num < self.limit:
            self.index += num
        else:
            raise Exception("Program block limit exceeded")

    def __repr__(self):
        return f"ProgramBlock(base={self.base}, limit={self.limit}, index={self.index})"


class DATA: 
    def __init__(self, lexeme, type, address, isFunction=False):
        self.lexeme = lexeme
        self.type = type
        self.address = address
        self.isFunction = isFunction
        if type == 'int' or type == 'array':
            self.size = 4
        

class DataBlock:
    def __init__(self, base, limit, isFunction=False):
        self.index = 0
        self.base = base
        self.limit = limit
        self.block = {}

    def add_data(self, lexeme, type, arr_size=1, isFunction=False):
        for i in range(arr_size):
            data= DATA(lexeme, type, self.index, isFunction)
            self.block[lexeme] =   self.base + self.index
            self.index += 4 # assuming int size is 4 bytes; 
            if self.index > self.limit:
                raise Exception("Data block limit exceeded")
        # symbol table todo  
    def get_data(self, lexeme):
        return self.block[lexeme]
        
    def get_temp(self):
        idx = self.index
        self.index += 4
        return idx + self.base
    
    def __repr__(self):
        return f"DataBlock(base={self.base}, limit={self.limit}, data={self.data})"


parser = Parser("input.txt")
parser.getTokens()
parser.write_outputs()
parser.code_generator.write_outputs()

# print(parser.state_machine["Relop"])