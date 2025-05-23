# Kian Ghassemi 401102264
# Matin Mohammadi 401110329


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
            return ("$", "$"), location + 1
        

        # read first char 
        ch = self.inputProgram[location]

        if ch == '\n': 
            self.lineno += 1
            return None, location + 1

        state = 'START'
        lexeme = ''
   
        while location <= len(self.inputProgram):

            if location >= len(self.inputProgram): 
                return ("DOLLOR", "$"), location + 1
        
            # comment handeling
            if (location + 1) < len(self.inputProgram) and self.inputProgram[location] == '/' and self.inputProgram[location + 1] == '*':
                lineNumber = self.lineno
                comment = ''
                if lexeme != '': break
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




grammar_string = "Program -> DeclarationList\n\
DeclarationList -> Declaration DeclarationList | EPSILON\n\
Declaration -> DeclarationInitial DeclarationPrime\n\
DeclarationInitial -> TypeSpecifier ID\n\
DeclarationPrime -> FunDeclarationPrime | VarDeclarationPrime\n\
VarDeclarationPrime -> ; | [ NUM ] ;\n\
FunDeclarationPrime -> ( Params ) CompoundStmt\n\
TypeSpecifier -> int | void\n\
Params -> int ID ParamPrime ParamList | void\n\
ParamList -> , Param ParamList | EPSILON\n\
Param -> DeclarationInitial ParamPrime\n\
ParamPrime -> [ ] | EPSILON\n\
CompoundStmt -> { DeclarationList StatementList }\n\
StatementList -> Statement StatementList | EPSILON\n\
Statement -> ExpressionStmt | CompoundStmt | SelectionStmt | IterationStmt | ReturnStmt\n\
ExpressionStmt -> Expression ; | break ; | ;\n\
SelectionStmt -> if ( Expression ) Statement else Statement\n\
IterationStmt -> while ( Expression ) Statement\n\
ReturnStmt -> return ReturnStmtPrime\n\
ReturnStmtPrime -> ; | Expression ;\n\
Expression -> SimpleExpressionZegond | ID B\n\
B -> = Expression | [ Expression ] H | SimpleExpressionPrime\n\
H -> = Expression | G D C\n\
SimpleExpressionZegond -> AdditiveExpressionZegond C\n\
SimpleExpressionPrime -> AdditiveExpressionPrime C\n\
C -> Relop AdditiveExpression | EPSILON\n\
Relop -> < | ==\n\
AdditiveExpression -> Term D\n\
AdditiveExpressionPrime -> TermPrime D\n\
AdditiveExpressionZegond -> TermZegond D\n\
D -> Addop Term D | EPSILON\n\
Addop -> + | -\n\
Term -> SignedFactor G\n\
TermPrime -> SignedFactorPrime G\n\
TermZegond -> SignedFactorZegond G\n\
G -> * SignedFactor G | EPSILON\n\
SignedFactor -> + Factor | - Factor | Factor\n\
SignedFactorPrime -> FactorPrime\n\
SignedFactorZegond -> + Factor | - Factor | FactorZegond\n\
Factor -> ( Expression ) | ID VarCallPrime | NUM\n\
VarCallPrime -> ( Args ) | VarPrime\n\
VarPrime -> [ Expression ] | EPSILON\n\
FactorPrime -> ( Args ) | EPSILON\n\
FactorZegond -> ( Expression ) | NUM\n\
Args -> ArgList | EPSILON\n\
ArgList -> Expression ArgListPrime\n\
ArgListPrime -> , Expression ArgListPrime | EPSILON"



        
class Parser:
    def __init__(self, filename):
        self.state_machine = build_state_machines_from_string(grammar_string)
        self.filename  = filename 
        self.scanner  = Scanner(filename)
        self.syntaxErrors = []
        self.parse_tree = []
        self.tree_depth = 0
        self.Frist_set = {}
        self.Follow_set = {}
        self.terminals = self.scanner.KEYWORDS.union(self.scanner.SYMBOLS, {"NUM", "ID"})
        print(self.terminals)
        self.current_state = ("Program", 0)
        self.stateList = [self.current_state] # stack for tokens of Input
        self.add_tree_node("Program")
        

    def getTokens(self): 
        currentIndex = 0
        nextToken = None
        while(nextToken[1] != "$"):
                nextToken, endToken = self.scanner.get_next_token(currentIndex)
                if nextToken: 
                    check_token = nextToken[0]
                    if check_token == "SYMBOL" or check_token == "KEYWORD": 
                        check_token = nextToken[1]

                    state = None
                    while not state in self.terminals: 
                     state, number = self.call(check_token)
                     self.stateList.append((state, number))
                     self.current_state = self.stateList[-1]
                     self.tree_depth += 1 
                     self.add_tree_node(state)
                    
                    if self.match(state, check_token): 
                        while(self.stateList[-1][1] == 1): # final state of diagram
                            self.stateList.pop()
                            self.tree_depth -= 1 

                    self.current_state = self.stateList[-1]
                currentIndex = endToken

    def match(self, token, state): 
        if token == state: return True
        else: return False


    def call(self, input_token): 
        for key  in self.state_machine[self.current_state[0]][self.current_state[1]].transitions.keys(): 
            if key in self.terminals and input_token == key: 
                return key,  self.state_machine[self.current_state[0]][self.current_state[1]].transitions[key]
            elif key != "EPSILON" and  input_token in self.Frist_set[key]  :
                return key,  self.state_machine[self.current_state[0]][self.current_state[1]].transitions[key]
            elif key == "EPSILON" and input_token in self.Follow_set[self.current_state[0]]:
                 return key,  self.state_machine[self.current_state[0]][self.current_state[1]].transitions[key]
        
        return None, None
    
    def add_tree_node(self, node):
        self.parse_tree.append('\t' * self.depth + node)

parser = Parser("input.txt")
# parser.getTokens()
