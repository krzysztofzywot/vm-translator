import sys
import glob
from parser import Parser
from codewriter import CodeWriter

def main():
    # Quit if no file name has been provided or if the file extension isn't .vm
    if len(sys.argv) == 1:
        print("You must provide a valid file or directory name.")
        sys.exit(1)

    user_input = sys.argv[1]

    files_to_translate = []
    is_directory = ".vm" not in user_input
    # If user provided directory name, iterate over each vm file in it and add it's name to the list
    if is_directory:
        for file_name in glob.glob(f"{user_input}/*.vm"):
            files_to_translate.append(file_name)
    else:
        files_to_translate.append(user_input)

    output_file_name = user_input if is_directory else user_input[:-3]

    code_writer = get_code_writer(output_file_name)

    # Start by inserting the bootstrap code
    code_writer.write_init()
    # Run the translator for each vm file
    for file_name in files_to_translate:
        parser = get_parser(file_name)
        set_codewriter_current_fname(code_writer, file_name)
        run_translator(parser, code_writer)

    code_writer.close_file()


def run_translator(parser, code_writer):
    while parser.has_more_commands():
        command = parser.advance()
        command_type = parser.command_type()

        if command_type == "C_ARITHMETIC":
            command = parser.arg1()
            code_writer.write_arithmetic(command)
        elif command_type == "C_PUSH" or command_type == "C_POP":
            segment = parser.arg1()
            index = parser.arg2()
            code_writer.write_push_pop(command_type, segment, index)
        elif command_type == "C_LABEL":
            label_name = parser.arg1()
            code_writer.write_label(label_name)
        elif command_type == "C_GOTO":
            label_name = parser.arg1()
            code_writer.write_goto(label_name)
        elif command_type == "C_IF":
            label_name = parser.arg1()
            code_writer.write_if(label_name)
        elif command_type == "C_CALL":
            function_name = parser.arg1()
            num_args = parser.arg2()
            code_writer.write_call(function_name, num_args)
        elif command_type == "C_FUNCTION":
            function_name = parser.arg1()
            num_locals = parser.arg2()
            code_writer.write_function(function_name, num_locals)
        elif command_type == "C_RETURN":
            code_writer.write_return()


    parser.close_file()


def get_parser(vm_file_name):
    try:
        parser = Parser(vm_file_name)
    except IOError:
        print("Invalid file name or file cannot be accessed.")
        sys.exit(2)

    return parser


def get_code_writer(output_file_name):
    try:
        code_writer = CodeWriter(output_file_name)
    except IOError:
        print("Cannot create an output asm file.")
        sys.exit(3)

    return code_writer


def set_codewriter_current_fname(code_writer, file_name):
    """Change codewriters current file name after opening a new file to properly handle static segments."""

    last_forward_slash = file_name.rfind("/")
    last_back_slash = file_name.rfind("\\")
    if last_forward_slash != -1:
        file_name = file_name[last_forward_slash+1:]
    elif last_back_slash != -1:
        file_name = file_name[last_back_slash+1:]
    code_writer.curr_file_name = file_name


if __name__ == "__main__":
    main()
