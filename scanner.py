# scanner
def input_reader(file_addr):
    with open(file_addr, 'r') as file:
        return file.read()

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
    while input_program[dummy_loc] >= '0' and input_program[dummy_loc] <= '9':
        
        
