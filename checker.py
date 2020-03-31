""" Includes all implemented rule checks and when to call them """

def coding_styler(file, filename):
    """ loops through each character of given file and calls coding style rules
    depending on what character is at current index. """
    line_number = 1
    style_errors = 0
    col_err = False
    style_errors += blank_start(file, filename)
    for index in range(0, len(file)-1):
        if file[index:index+10] == "#include \"":
            style_errors += include_priority(index, file, line_number, filename)
        if file[index:index+2] == "if":
            style_errors += if_space(index+1, file, line_number, filename)
        if file[index:index+3] == "for":
            style_errors += for_space(index+2, file, line_number, filename)
        if file[index:index+5] == "while":
            style_errors += while_space(index+4, file, line_number, filename)
        if file[index] == '#':
            style_errors += pre_proc_directive(index, file, line_number, filename)
        if file[index] == '\t':
            style_errors += forbidden_tab(index, file, line_number, filename)
        if file[index] == ';' and index != len(file):
            style_errors += dead_code(index, file, line_number, filename)
        if file[index] == '\n':
            style_errors += trailing_spaces(index, file, line_number, filename)
        if not col_err:
            if eighty_columns(index, file, line_number, filename):
                style_errors+=1
                col_err = True
        if file[index:index+2] == "()":
            style_errors += void_function(index, file, line_number, filename)
        if file[index:index+2] == " (":
            style_errors += function_args_whitespace(index, file, line_number, filename)
        if file[index] == "(":
            style_errors += open_parenthesis_space(index, file, line_number, filename)
        if file[index] == ")":
            style_errors += close_parenthesis_space(index, file, line_number, filename)
        if file[index:index+2] == "/*":
            style_errors += long_dead_code(index, file, line_number, filename)
        if file[index:index+5] == "#else":
            style_errors += else_comment(index, file, line_number, filename)
        if file[index] == '*':
            style_errors += sticky_star(index, file, line_number, filename)
        if file[index] == '+' or file[index] == '-' or file[index] == '*':
            style_errors += operation_spacing(index, file, line_number, filename)
        if file[index] == '{' or file[index] == '}':
            style_errors += solo_braces(index, file, line_number, filename)
        if file[index] == '{':
            style_errors += indentation_check(index, file, line_number, filename)
        if file[index] == ';':
            style_errors += semicolon_space(index, file, line_number, filename)
        if file[index] == ',':
            style_errors += comma_space(index, file, line_number, filename)
        if file[index] == '\n':
            col_err = False
            line_number+=1
    style_errors += blank_end(index, file, filename)
    return style_errors

def find_line(index, file):
    """ returns line in which an index is """
    line_start = file[0:index].rfind('\n')
    line_end = file[index:len(file)].find('\n')+index
    return [line_start, line_end]

# coding style rules:

def open_parenthesis_space(index, file, line_number, filename):
    """ Checks if there is a space after an open parenthesis """
    if file[index+1] is " ":
        print_error("Space after opening parenthesis", index, line_number, file, filename)
        return 1
    return 0

def close_parenthesis_space(index, file, line_number, filename):
    """ Checks if there is a space after an closing parenthesis """
    if file[index-1] is " ":
        print_error("Space before closing parenthesis", index, line_number, file, filename)
        return 1
    return 0

def void_function(index, file, line_number, filename):
    """ Checks if function has input or not """
    [line_start, line_end] = find_line(index, file)
    if "if" in file[line_start:index]:
        return 0
    if '"' in file[line_start:index] and '"' in file[index:line_end]:
        return 0
    if "'" in file[line_start:index] and "'" in file[index:line_end]:
        return 0
    if file[index+2] is ';':
        return 0
    print_error("Void missing", index, line_number, file, filename)
    return 1
        
def long_dead_code(index, file, line_number, filename):
    """ Checks if there is dead code in long comment format """
    while file[index:index+2] != "*/":
        # If comment is doxygen, presence of ; is acceptable.
        if "**" in file[index:index+3]:
            return 0
        if file[index] == ';':
            print(file[index])
            print("Long dead code at line " + str(line_number)
                  + " in file " + filename)
            return 1
        index+=1
    return 0

def blank_start(file, filename):
    """ Checks if first line is blank """
    if file[0] == '\n':
        print("First line is blank in file " + filename + "\n")
        return 1
    return 0

def blank_end(index, file, filename):
    """ Checks if last line is blank """
    if file[index+1] == '\n':
        print("Last line is blank in file " + filename + "\n")
        return 1
    return 0

def forbidden_tab(index, file, line_number, filename):
    """ Is only called if a tab was used """
    print_error("Tab used", index, line_number, file, filename)
    return 1

def else_comment(index, file, line_number, filename):
    """ Checks if there is a comment after an else """
    [line_start, line_end] = find_line(index, file)
    if "//" in file[line_start, line_end]:
        return 0
    print_error("Pre-proc else lacks comment", index, line_number, file, filename)
    return 1

def pre_proc_directive(index, file, line_number, filename):
    """ Checks if the pre-processor directive is on the first column """
    [line_start, line_end] = find_line(index, file)
    if index-line_start != 2:
        return 0
    print_error("Misplaced Pre-Proc directive", index, line_number, file, filename)
    return 1

def include_priority(index, file, line_number, filename):
    """ Checks if includes are in the right order """
    [line_start, line_end] = find_line(index, file)
    [next_line_start, next_line_end] = find_line(line_end+1, file)
    if "#include <" in file[next_line_start:next_line_end]:
        print("Bad include priority at line " + str(line_number)
              + " in file " + filename)
        print(file[line_start+1:line_end])
        print(file[next_line_start+1:next_line_end]+'\n')
        return 1
    return 0

def eighty_columns(index, file, line_number, filename):
    """ Checks if there are more than 80 characters in a single line """
    [line_start, line_end] = find_line(index, file)
    if index-line_start > 80:
        index = index-2
        print_error("More than 80 columns", index, line_number, file, filename)
        return 1
    return 0

def operation_spacing(index, file, line_number, filename):
    """ Checks if there are spaces around binary operators """
    [line_start, line_end] = find_line(index, file)
    if "= -1" in file[line_start:line_end]:
        return 0
    if file[index-1].isnumeric() or file[index+1].isnumeric():
        print_error("Missing space around operator", index, line_number, file, filename)
        return 1
    return 0

def indentation_check(index, file, line_number, filename):
    """ Checks if there is an indent after anopening brace """
    [line_start, line_end] = find_line(index, file)
    if "struct" in file[line_start:line_end]:
        return 0
    if '"' in file[line_start:index] and '"' in file[index:line_end]:
        return 0
    if "'" in file[index-2:index] and "'" in file[index:index+2]:
        return 0
    [prev_line_start, prev_line_end] = find_line(line_start-3, file)
    if "switch" in file[prev_line_start:prev_line_end]:
        return 0
    preceding_spaces = index-file[0:index].rfind('\n')-1
    if file[index+preceding_spaces+2] == '}':
        return 0
    succeeding_spaces = 0
    special_index = index+1
    while file[special_index+1] == ' ':
        succeeding_spaces += 1
        special_index += 1
    if succeeding_spaces == preceding_spaces:
        print("Badly indented code at line "+str(line_number+1)
                + " of file " + filename)
        [line_start, line_end] = find_line(line_end+3, file)
        print(file[line_start+1:line_end])
        print(" "*(succeeding_spaces) + "^")
        return 1
    return 0

def dead_code(index, file, line_number, filename):
    """ Checks if there is dead code in the code """
    [line_start, line_end] = find_line(index, file)
    if "'" in file[index-2:index] and "'" in file[index:index+2]:
        return 0
    if "//" in file[line_start:index]:
        print_error("Dead code", index, line_number, file, filename)
        return 1
    return 0

def sticky_star(index, file, line_number, filename):
    """ Checks if pointers are spaced correctly """
    [line_start, line_end] = find_line(index, file)
    is_comment = False
    if not ';' in file[line_start:line_end]:
        is_comment = True
    if file[index-2] == ')':
        return 0
    if "**" in file[line_start:line_start + 5]:
        return 0
    if file[index+2].isalpha() and not is_comment:
        #print(file[index+2])
        if file[index+1] == " ":
            print_error("Potential pointer style error", index, line_number, file, filename)
            return 1
    return 0

def trailing_spaces(index, file, line_number, filename):
    """ Checks if there are any trailing spaces at the end of a line """
    [line_start, line_end] = find_line(index-1, file)
    # check if line is comment
    if "//" in file[line_start:index]:
        return 0
    # check if line is a multiline statement 
    if '**' in file[index:line_end]:
        return 0
    # check if space is part of string
    if '"' in file[line_start:index] and '"' in file[index:line_end]:
        return 0
    if file[index - 1] == " ":
        print_error("Trailing space", index, line_number, file, filename)
        return 1
    return 0

def function_args_whitespace(index, file, line_number, filename):
    """ Checks if there is a whitespace between function name and arguments """
    [line_start, line_end] = find_line(index, file)
    if "for" in file[line_start:line_end] or "while" in file[line_start:line_end] or "if" in file[line_start:line_end]:
        return 0
    if file[index-1].isalpha():
        print_error("Potential whitespace between function name and args", index-1, line_number, file, filename)
        return 1
    return 0

def semicolon_space(index, file, line_number, filename):
    """ Checks if there is no space before and one after a semi-column """
    [line_start, line_end] = find_line(index, file)
    is_empty_before_semi_column = True
    for char in file[line_start+1:index]:
        if char != " ":
            is_empty_before_semi_column = False
    if file[index+1] == '\n' and is_empty_before_semi_column:
        print_error("Semi-column alone on its line", index-1, line_number, file, filename)
        return 1
    if file[index-1] == ' ':
        print_error("Space before semi-column", index-2, line_number, file, filename)
        return 1
    if file[index+1] != ' ' and file[index+1] != '\n':
        print_error("No space after semi-column", index, line_number, file, filename)
        return 1
    return 0

def comma_space(index, file, line_number, filename):
    """ Checks if there is a space after a comma """
    if file[index+1] == '\n':
        return 0
    if file[index+1] != ' ':
        print_error("Missing space after comma", index, line_number, file, filename)
        return 1
    return 0

def solo_braces(index, file, line_number, filename):
    """ Checks that { and } are on their own line """
    [line_start, line_end] = find_line(index, file)
    if '"' in file[line_start:index] and '"' in file[index:line_end]:
        return 0
    if "'" in file[index-2:index] and "'" in file[index:index+2]:
        return 0
    if "parser.h" in filename:
        return 0
    for character in file[line_start:line_end]:
        if character.isalpha() or character == ")" or character == "(":
            print_error("Badly indented brace", index, line_number, file, filename)
            return 1
    return 0

def if_space(index, file, line_number, filename):
    """ Checks if there is a space after an if statement """
    if file[index+1] == ' ':
        return 0
    if file[index-2] != ' ' or file[index-3] != ' ':
        return 0
    else:
        print_error("Missing space after if", index, line_number, file, filename)
        return 1

def for_space(index, file, line_number, filename):
    """ Checks if there is a space after an if statement """
    if file[index+1] == ' ':
        return 0
    if file[index-3] != ' ' or file[index-4] != ' ':
        return 0
    else:
        print_error("Missing space after for", index, line_number, file, filename)
        return 1

def while_space(index, file, line_number, filename):
    """ Checks if there is a space after an if statement """
    if file[index+1] == ' ':
        return 0
    if file[index-5] != ' ' or file[index-6] != ' ':
        return 0
    else:
        print_error("Missing space after while", index, line_number, file, filename)
        return 1

def print_error(error_type, index, line_number, file, filename):
    [line_start, line_end] = find_line(index, file)
    print(error_type + " at line " + str(line_number)
          + " of file " + filename)
    print(file[line_start+1:line_end])
    print(" "*(index-line_start) + "^")