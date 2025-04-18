
import re 

KEYWORDS = {"if", "else", "void", "int", "while", "break", "return"}
SYMBOLS = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<', '>'}
WHITESPACE = {' ','\t','\r','\v','\f'}


class Scanner:
    def __init__(self, filename):

        self.filename  = filename 
        self.tokens = []
        self.errors = []
        self.symbolTable = set()
        self.symbolTable.update(KEYWORDS)
        self.lineno = 0
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
        ('ID', 'LETTER'): 'ID',
        ('ID', 'DIGIT'): 'ID',
        ('ID', 'OTHER'): 'INV_IN',
        ('NUM', 'DIGIT'): 'NUM',
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
        elif ch in SYMBOLS: return 'SYMBOL'  # Use char itself for symbols
        elif ch in WHITESPACE: return 'WHITESPACE'
        elif ch in '=/*': return ch 
        elif ch == '\n': 'NEWLINE'
        else: return 'OTHER'



     

    def get_next_token(self, location):
        while location < len(self.inputProgram) and self.inputProgram[location] in WHITESPACE:
            location += 1

        if location >= len(self.inputProgram): 
            return None, location
        

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
                comment = ''
                while(True):
                    if (location + 1) < len(self.inputProgram) and self.inputProgram[location] == '*' and self.inputProgram[location + 1] == '/':
                        break
                    else:
                        if location + 1 == len(self.inputProgram): 
                            if len(comment) > 7:  
                                comment = f'{comment[:7]}...'
                            self.errors.append((self.lineno + 1,  comment, 'Unclosed comment'))
                            return None, location + 1
                    comment += self.inputProgram[location]
                    location += 1
                location += 2
                break

            elif (location + 1) < len(self.inputProgram) and self.inputProgram[location] == '*' and self.inputProgram[location + 1] == '/':
                self.errors.append((self.lineno + 1, '*/', 'Unmatched comment'))
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
            if lexeme in KEYWORDS:
                tokenType = 'KEYWORD'
            if tokenType == 'ID':
                 if lexeme not in self.symbolTable:
                    self.symbolTable.add(lexeme)

            if (tokenType == 'INV_IN'): 
                self.errors.append((self.lineno + 1, lexeme, 'Invalid input'))
                return None, location 
            
            if (tokenType == 'INV_NUM'):
                self.errors.append((self.lineno + 1, lexeme, 'Invalid number'))
                return None, location 
            
            return (tokenType, lexeme), location
        else:
            return None, location 


     
    def scanning(self): 
        tempLineno = 0
        currentIndex = 0
        while(currentIndex < len(self.inputProgram)):
            lineTokenList = []
            while(self.lineno == tempLineno and currentIndex <  len(self.inputProgram)): 
                nextToken, endToken = self.get_next_token(currentIndex)
                if nextToken: 
                    lineTokenList.append(nextToken)
                currentIndex = endToken
            tempLineno += 1
            if lineTokenList:
                self.tokens.append((tempLineno, lineTokenList))
    
    
        
  
    def generateOutputs(self): 
        with open('tokens.txt', 'w', encoding='utf-8') as f: 
            for lineno, tokenPair in self.tokens:
                lineToken = f"{lineno}.\t" + ' '.join(f"({type}, {value})" for type, value in tokenPair)
                f.write(lineToken + '\n')

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


if __name__ == '__main__':
    scanner = Scanner('input.txt')
    scanner.scanning()
    scanner.generateOutputs()

