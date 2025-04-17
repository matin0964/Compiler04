
import re 

KEYWORDS = {"if", "else", "void", "int", "while", "break", "return"}
SYMBOLS = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<'}
DOUBLE_SYMBOLS = {'==', '<=', '>='}
WHITESPACE = {' ','\t','\r','\v','\f'}


class Scanner:
    def __init__(self, filename):

        self.filename  = filename 
        self.tokens = []
        self.errors = []
        self.symoblTable = set()
        self.lineno = 0
  

        with open(filename, encoding='utf-8') as f:
            self.setOfLines = f.readlines()
     
    def get_next_token(self, input_program, location):
        while location < len(input_program) and input_program[location] in WHITESPACE:
            location += 1

        if location > len(input_program): 
            return None, location
        

        # read first char 
        ch = input_program[location]


        # recognize Command 


        # recognizing KEYWORDS and Identifiers
        if ch.isalpha(): 
            match = re.match(r'[A-Za-z][A-Za-z0-9]*', input_program[location:])
            lexeme = match.group()

            if lexeme not in self.symoblTable:
                self.symoblTable.add(lexeme)


            if lexeme in KEYWORDS: 
                return ('KEYWORD', lexeme), location + len(lexeme)
            else:
                return ('ID', lexeme), location + len(lexeme)
            
            

        # recognizing NUMBER
        if ch.isdigit(): 
            match = re.match(r'\d+[A-Za-z]*', input_program[location:])
            lexeme = match.group()

            if re.fullmatch(r'\d+', lexeme):
                return ('NUM', lexeme), location + len(lexeme)
            else:
                self.errors.append((self.lineno, lexeme, 'Invalid number'))
                return None, location + len(lexeme)
            
        # recognizing SYMBOL (lookahead approach)
        if location + 1 < len(input_program) and input_program[location:location+2] in DOUBLE_SYMBOLS:
            return ('SYMBOL', input_program[location:location+2]), location + 2

        if ch in SYMBOLS:
            return ('SYMBOL', ch), location + 1
        
         # Invalid Char
        if ch == '\n': 
            # self.lineno += 1
            return None, location + 1
        
        self.errors.append((self.lineno, ch, 'Invalid input'))
        return None, location + 1
    
    
        
    def scanning(self): 
        tempLineno = self.lineno
        for _, line in enumerate(self.setOfLines): 
            self.lineno += 1
            lineTokenList = []
            currentIndex = 0
            while currentIndex < len(line): 
                nextToken, endToken = self.get_next_token(line, currentIndex)
                if nextToken: 
                    lineTokenList.append(nextToken)
                currentIndex = endToken
            if lineTokenList:
                self.tokens.append((self.lineno, lineTokenList))

    def generateOutputs(self): 
        with open('token.txt', 'w', encoding='utf-8') as f: 
            for lineno, tokenPair in self.tokens:
                lineToken = f"{lineno}\t" + ' '.join(f"({type}, {value})" for type, value in tokenPair)
                f.write(lineToken + '\n')

        with open('lexical_errors.txt', 'w', encoding='utf-8') as f:
            if not self.errors:
                f.write('There is no lexical error.\n')
            else:
                for lineno, errorCode, errorType in self.errors:
                    f.write(f"{lineno}\t({errorCode}, {errorType})\n")


        with open('symbol_table.txt', 'w', encoding='utf-8') as f:
            for no, lexeme in enumerate(self.symoblTable, 1):
                f.write(f"{no}.\t{lexeme}\n")


if __name__ == '__main__':
    scanner = Scanner('input.txt')
    scanner.scanning()
    scanner.generateOutputs()

