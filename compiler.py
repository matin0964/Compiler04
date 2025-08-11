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
DeclarationInitial -> #push_ss TypeSpecifier ID\n\
DeclarationPrime -> FunDeclarationPrime | VarDeclarationPrime\n\
VarDeclarationPrime -> ; #dec_var | [ #push_ss NUM ] ; #dec_arr\n\
FunDeclarationPrime -> ( Params ) #param_det CompoundStmt #cls_func\n\
TypeSpecifier -> int | void\n\
Params -> #push_ss int #push_ss ID ParamPrime ParamList | void\n\
ParamList -> , Param ParamList | EPSILON\n\
Param -> DeclarationInitial ParamPrime\n\
ParamPrime -> [ ] #dec_pnt | EPSILON #dec_var \n\
CompoundStmt -> { #save_scope DeclarationList StatementList #back_scope }\n\
StatementList -> Statement StatementList | EPSILON\n\
Statement -> ExpressionStmt | CompoundStmt | SelectionStmt | IterationStmt | ReturnStmt\n\
ExpressionStmt -> Expression ; | break #save_b ; | ;\n\
SelectionStmt -> if ( Expression ) #save Statement else #jpf_save Statement #jp\n\
IterationStmt -> while #while_label ( Expression ) #save_while_jp Statement #end_while \n\
ReturnStmt -> return ReturnStmtPrime\n\
ReturnStmtPrime -> #return_j ; | Expression #save_retval ;\n\
Expression -> SimpleExpressionZegond | $pid ID B #print \n\
B -> = Expression #assign | [ Expression ] #arr_addr H | SimpleExpressionPrime\n\
H -> = Expression #assign | G D C\n\
SimpleExpressionZegond -> AdditiveExpressionZegond C\n\
SimpleExpressionPrime -> AdditiveExpressionPrime C\n\
C -> Relop AdditiveExpression #comp | EPSILON\n\
Relop ->  #push_ss < | #push_ss ==\n\
AdditiveExpression -> Term D\n\
AdditiveExpressionPrime -> TermPrime D\n\
AdditiveExpressionZegond -> TermZegond D\n\
D -> Addop Term #add_sub D | EPSILON\n\
Addop -> #push_ss + | #push_ss -\n\
Term -> SignedFactor G\n\
TermPrime -> SignedFactorPrime G\n\
TermZegond -> SignedFactorZegond G\n\
G -> * SignedFactor #mult G | EPSILON\n\
SignedFactor -> + Factor | - Factor | Factor\n\
SignedFactorPrime -> FactorPrime\n\
SignedFactorZegond -> + Factor | - Factor | FactorZegond\n\
Factor -> ( Expression ) | #pid ID VarCallPrime | #push_num NUM\n\
VarCallPrime -> #args_begin ( Args ) #end_args | VarPrime\n\
VarPrime -> [ Expression ] #arr_addr | EPSILON\n\
FactorPrime -> ( Args ) | EPSILON\n\
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
        self.First_set = first_sets = {
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

                    # action symbol states
                    if len(self.state_machine[self.current_state[0]][self.current_state[1]].transitions.keys()) == 1:
                        next_state = list(self.state_machine[self.current_state[0]][self.current_state[1]].transitions)[0]
                        if next_state.startswith("#"):
                            self.code_generator.code_gen(next_state[1:])
                            number = self.state_machine[self.current_state[0]][self.current_state[1]].transitions[next_state]
                            self.stateList.pop()
                            self.stateList.append((self.current_state[0], number))   
                            self.current_state = self.stateList[-1]

                    state, number = self.call(check_token)
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
 

    def call(self, input_token):

        if len(self.state_machine[self.current_state[0]][self.current_state[1]].transitions.keys()) == 1: 
            next_state = list(parser.state_machine[self.current_state[0]][self.current_state[1]].transitions)[0]
            return next_state, self.state_machine[self.current_state[0]][self.current_state[1]].transitions[next_state]
        for key  in self.state_machine[self.current_state[0]][self.current_state[1]].transitions.keys(): 
            if key in self.terminals:
                if input_token == key: 
                    return key,  self.state_machine[self.current_state[0]][self.current_state[1]].transitions[key]
            elif key != "epsilon" and  (input_token in self.First_set[key] or
                                         (input_token in self.Follow_set[key] and 
                                                                               "EPSILON" in self.First_set[key])) :

                return key,  self.state_machine[self.current_state[0]][self.current_state[1]].transitions[key]
            
            elif key == "epsilon" and input_token in self.Follow_set[self.current_state[0]]:
                return key,  self.state_machine[self.current_state[0]][self.current_state[1]].transitions[key] 
          
          
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
    DECLARE_VAR = "dec_var"
    PARAM_INFO = "param_det"
    CLOSE_FUNC = "cls_func"
    DECLARE_POINTER = "dec_pnt"
    DECLARE_VAR = "dec_var"
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
      

    def code_gen(self, action_symbol):
        print(ActionSymbols(action_symbol).name) 
        

parser = Parser("input.txt")
parser.getTokens()
parser.write_outputs()



