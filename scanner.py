# scanner
class Scanner:
    def __init__(self, filename):
        self.KEYWORDS = {"if", "else", "void", "int", "while", "break", "return"}
        self.SYMBOLS = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<'}
        self.filename  = filename 
        self.tokens = []
        self.errors = []
        self.symoblTable = []
        
        with open(filename, encoding='utf-8') as f:
            self.setOfLines = f.readlines()
     
    def get_next_token(input_program, location):
        # recognizing SYMBOL
        ans= is_symbol(input_program[location])
        if ans:
            if input_program[location] == '/' and input_program[location + 1] == '*':
                # comment 
                return
            if input_program[location] == '=' and input_program[location+1] == '=':
                # logical equality
                return
            # return the symbol token
            return 
        # recognizing NUM
        loc_dummy = location
        tk = ''
        if is_digit(input_program[location]):
            while is_digit(input_program[loc_dummy]):
                tk += input_program[loc_dummy]
                loc_dummy += 1
            if is_white(input_program[loc_dummy]) or is_symbol(input_program[loc_dummy]) or input_program[loc_dummy] == 'EOF':
                # means that it is a correct number
                return 
            else:
                # means that there's an error
                return
            return
        elif is_letter(input_program[location]):
            while is_letter(input_program[loc_dummy]) or is_digit(input_program[loc_dummy]):
                tk += input_program[loc_dummy]
                loc_dummy += 1
            if is_keyword(tk):
                # means that it is a keyword
                return
            else:
                # the word is an ID and not a keyword
                return
            return 
        else:
            return
    
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
            for no, lexeme in enumerate(self.symbol_table, 1):
                f.write(f"{no}.\t{lexeme}\n")


if __name__ == '__main__':
    scanner = Scanner('input.txt')

