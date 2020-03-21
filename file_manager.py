""" Manages getting from file to file and printing results. """

import os.path
import sys
import checker
from fixer import file_to_fix_selector

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

def file_selector(directory):
    ''' calls get file list to obtain a list of all the files in
    subdirectories and then calls coding_styler to run on each
    individual file. '''
    print("= Coding style checks " + 58*"=")
    style_errors = 0
    all_files = get_file_list(directory)
    for filename in all_files:
        if os.path.isfile(filename):
            if filename[len(filename)-2:len(filename)]==".c" or \
                filename[len(filename)-2:len(filename)]==".h":
                with open(filename, 'r') as file:
                    file = file.read()
                    filename = filename.replace(directory, "")
                    style_errors += checker.coding_styler(file, filename)
                
    print(str(style_errors) + " coding style error(s) found.")
    if style_errors > 0:
        answer = input("Do you want to try and fix them? (y/n)\n")
        if answer == "y" or answer == "yes":
            file_to_fix_selector()
        return 1
    else:
        return 0

def print_help():
    hp = "There are two ways to use the coding style checker: \n"
    hp += "1)   Give it no arguments and it will search for files recursively in the directory it is in. \n"
    hp += "2)   Give it a path as argument and it will search for files recursively in that directory."
    print(hp)

def main():
    if len(sys.argv) == 1:
        file_selector(os.path.dirname(os.path.abspath(__file__)))
    if len(sys.argv) == 2:
        if sys.argv[1] == "help":
            print_help()
        else:
            file_selector(sys.argv[1])
    if len(sys.argv) > 2:
        print("ERROR: too many arguments.")
main()