# scanner
def input_reader(file_addr):
    with open(file_addr, 'r') as file:
        return file.read()
def is_letter(c):
    if c >= 'a' and c <= 'z':
        return True
    if c >= 'A' and c <= 'Z':
        return True
    return False

def is_digit(c):
    if c >= '0' and c <= '9':
        return True
    return False
def is_keyword(token):
    match token:
        case "if":
            return 
        case "else":
            return 
        case "void":
            return
        case "while":
            return
        case "int":
            return
        case "break":
            return
        case "return":
            return
def get_next_token(input_program, location):
    # recognizing SYMBOL
    match input_program[location]:
        case ';':
            return
        case ':':
            return
        case ',':
            return
        case '[':
            return
        case ']':
            return
        case '{':
            return
        case '}':
            return
        case '(':
            return
        case ')':
            return
        case '+':
            return
        case '-':
            return
        case '*':
            return
        case '/':
            if input_program[location+1] == '*':
                # comment
                return
            else:
                return
        case '=':
            if input_program[location+1] == '=':
                # equality
                return
            else:
                # assignment
                return
        case '<':
            return
        case '>':
            return
        
    # recognizing NUM
    dummy_loc = location
    tk = ''
    is_Number = False
    while is_digit(input_program[dummy_loc]):
         is_Number = True
         tk = tk + input_program[dummy_loc]
         dummy_loc = dummy_loc+1
    if is_Number:
        return
    
    # recognizing ID
    tk = ''
    is_ID = False
    dummy_loc = location
    if is_digit(input_program[dummy_loc]):
        # can't start an ID
        return
    elif is_letter(input_program[dummy_loc]):
        tk = tk + input_program[dummy_loc]
        dummy_loc = dummy_loc+1
    else: 
        return 
    while is_digit(input_program[dummy_loc]) or is_letter(input_program[dummy_loc]):
        tk = tk + input_program[dummy_loc]
        dummy_loc = dummy_loc+1
    # recognize difference between ID and KEYWORD
    
    is_ID = True
