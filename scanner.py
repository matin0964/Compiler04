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
def is_white(c):
    match c:
        case ' ':
            return True
        case '\t':
            return True
        case '\n':
            return True
        case '\r':
            return True
        case '\v':
            return True
        case '\f':
            return True
def is_symbol(c):
    match c:
        case ';':
            return True
        case ':':
            return True 
        case ',':
            return True 
        case '[':
            return True 
        case ']':
            return True 
        case '{':
            return True 
        case '}':
            return True
        case '(':
            return True
        case ')':
            return True
        case '+':
            return True
        case '-':
            return True
        case '*':
            return True
        case '/':
            return True
        case '=':
            return True
        case '<':
            return True
        case '>':
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