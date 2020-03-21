import os.path

##
# \file coding_style_checker.py
# \brief Separate test file that manages coding style errors.
# A file whose functions are called by the main test suite when 
# the --style flag is set. Contains more than than a dozen checks
# concerning coding style.
# \author Daniel
# \version v0.5
# \date March 2019
def get_file_list(given_path):
    ''' iterates recursively through subdirectories to get a list of
    them and returns it '''
    list_of_files = os.listdir(given_path)
    all_files = list()
    for entry in list_of_files:
        full_path = os.path.join(given_path, entry)
        if os.path.isdir(full_path):
            all_files = all_files + get_file_list(full_path)
        else:
            all_files.append(full_path)
    return all_files

def file_to_fix_selector():
    ''' calls get file list to obtain a list of all the files in
    subdirectories and then calls coding_styler to run on each
    individual file.
    This function is the one that is called by test_suite.py'''
    print("= Coding style fixes " + 59*"=")
    total_fixed_errors = 0
    directory = os.path.dirname(os.path.abspath(__file__))
    all_files = get_file_list(directory)
    directory = directory.replace("/tests","/src")
    all_files = get_file_list(directory) + all_files
    for file_path in all_files:
        fixed_errors = 0
        if os.path.isfile(file_path):
            if file_path[len(file_path)-2:len(file_path)]==".c" or \
                file_path[len(file_path)-2:len(file_path)]==".h":
                with open(file_path, 'r') as file:
                    file = file.read()
                keep = file_path.find("42sh")
                filename = file_path[keep:]
                [file, fixed_errors] = coding_fixer(file, filename)
                if fixed_errors>0:
                    file_to_fix = open(file_path, 'w')
                    file_to_fix.write(file)
                    total_fixed_errors += fixed_errors
    print(str(total_fixed_errors) + " coding style error(s) fixed.")
    return

def coding_fixer(file, filename):
    """ loops through each character of given file and calls coding style rules
    depending on what character is at current index. """
    line_number = 1
    fixed_errors = 0
    col_err = False
    if ".h" in filename and "pragma" not in file:
        [fixed_errors, file] = header_guard(file, filename, fixed_errors)
    if file[0] == '\n':
        [fixed_errors, file] = blank_start(file, filename, fixed_errors)
    index=0
    while index < len(file)-1:
        if file[index:index+10] == "#include \"":
            [fixed_errors, file] = include_priority(index, file, filename, fixed_errors)
        if file[index] == '\t':
            [fixed_errors, file] = forbidden_tab(index, file, filename, fixed_errors)
        if file[index] == '\n':
            [fixed_errors, file] = trailing_spaces(index, file, filename, fixed_errors)
        if file[index:index+2] == "()":
            [fixed_errors, file] = void_function(index, file, filename, fixed_errors)
        index+=1
    if file[len(file)-1] == '\n':
        [fixed_errors, file] = blank_end(index, file, filename, fixed_errors)
        
    
    return [file, fixed_errors]



def find_line(index, file):
    """ returns line in which an index is """
    line_start = file[0:index].rfind('\n')
    line_end = file[index:len(file)].find('\n')+index
    return [line_start, line_end]

# coding style rules:

def header_guard(file, filename, fixed_errors):
    """ Checks if header files are guarded """
    file = "#pragma once\n" + file
    fixed_errors += 1
    print("Added header guard to file "+filename)
    return [fixed_errors, file]

def blank_start(file, filename, fixed_errors):
    """ Checks if first line is blank """
    file = file[1:len(file)]
    print("Starting blank line removed in file " + filename + "\n")
    fixed_errors += 1
    return [fixed_errors, file]

def blank_end(index, file, filename, fixed_errors):
    file = file[0:len(file)-1]
    print("Ending blank line removed in file " + filename + "\n")
    fixed_errors += 1
    return [fixed_errors, file]

def forbidden_tab(index, file, filename, fixed_errors):
    """ Is only called if a tab was used """
    file = file.replace("\t", "    ")
    print("Tab removed in file " + filename)
    fixed_errors+=1
    return [fixed_errors, file]

def trailing_spaces(index, file, filename, fixed_errors):
    """ Checks if there are any trailing spaces at the end of a line """
    [line_start, line_end] = find_line(index-1, file)
    # check if line is comment
    if "//" in file[line_start:line_end]:
        return [fixed_errors, file]
    # check if line is a multiline statement 
    if '**' in file[index:line_end]:
        return [fixed_errors, file]
    # check if space is part of string
    if '"' in file[line_start:index] and '"' in file[index:line_end]:
        return [fixed_errors, file]
    if file[index - 1] != " ":
        return [fixed_errors, file]
    i = index-1
    number_of_trails = 0
    while file[i] == " ":
        number_of_trails+=1
        i-=1
    print("number of trails: " + str(number_of_trails))
    fixed_file = file[:index-number_of_trails] + file[index:]
    print("Trailing space removed in file "+ filename)
    fixed_errors+=1
    return [fixed_errors, fixed_file]

def include_priority(index, file, filename, fixed_errors):
    """ Checks if includes are in the right order """
    [line_start, line_end] = find_line(index, file)
    [next_line_start, next_line_end] = find_line(line_end+1, file)
    if "#include <" in file[next_line_start:next_line_end]:
        first_line = file[line_start+1:line_end]
        second_line = file[next_line_start+1:next_line_end]
        fixed_file = file[:line_start+1] + second_line +"\n"+ first_line + file[next_line_end:]
        print("Fixed include priority in file " + filename)
        fixed_errors+=1
        return [fixed_errors, fixed_file]
    return [fixed_errors, file]

def void_function(index, file, filename, fixed_errors):
    """ Checks if function has input or not """
    [line_start, line_end] = find_line(index, file)
    if "if" in file[line_start:index]:
        return [fixed_errors, file]
    if '"' in file[line_start:index] and '"' in file[index:line_end]:
        return [fixed_errors, file]
    if "'" in file[line_start:index] and "'" in file[index:line_end]:
        return [fixed_errors, file]
    if file[index+2] is ';':
        return [fixed_errors, file]
    index+=1
    file = file[:index]+ "void" + file[index:]
    #print(file)
    print("Void added in file "+filename) 
    fixed_errors+=1 
    return [fixed_errors, file]

def operation_spacing(index, file, line_number, filename):
    """ Checks if there are spaces around binary operators """
    [line_start, line_end] = find_line(index, file)
    if "= -1" in file[line_start:line_end]:
        return 0
    if file[index-1].isnumeric() or file[index+1].isnumeric():
        print_error("Missing space around operator", index, line_number, file, filename)
        return 1
    return 0

def comma_space(index, file, line_number, filename):
    """ Checks if there is a space after a comma """
    [line_start, line_end] = find_line(index, file)
    if file[index+1] == '\n':
        return 0
    if file[index+1] != ' ':
        print_error("Missing space after comma", index, line_number, file, filename)
        return 1
    return 0

def solo_braces(index, file, line_number, filename):
    """ Checks that { and } are on their own line """
    [line_start, line_end] = find_line(index, file)
    if "struct" in file[line_start:line_end]:
        return 0
    if '"' in file[index-30:index] and '"' in file[index:index+20]:
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
    [line_start, line_end] = find_line(index, file)
    if file[index+1] == ' ':
        return 0
    if file[index-2] != ' ' or file[index-3] != ' ':
        return 0
    else:
        print_error("Missing space after if", index, line_number, file, filename)
        return 1

def for_space(index, file, line_number, filename):
    """ Checks if there is a space after an if statement """
    [line_start, line_end] = find_line(index, file)
    if file[index+1] == ' ':
        return 0
    if file[index-3] != ' ' or file[index-4] != ' ':
        return 0
    else:
        print_error("Missing space after for", index, line_number, file, filename)
        return 1

def while_space(index, file, line_number, filename):
    """ Checks if there is a space after an if statement """
    [line_start, line_end] = find_line(index, file)
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