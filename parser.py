import os

class Parser:

    ARITHMETIC_LOGICAL_COMMANDS = [
        "add", "sub", "neg",
        "eq", "gt", "lt",
        "and", "or", "not"
    ]

    def __init__(self, fname):
        try:
            self.f = open(fname, "r")
        except IOError:
            raise IOError

        self.current_command = ""


    def has_more_commands(self):
        return self.f.tell() != os.fstat(self.f.fileno()).st_size


    def advance(self):
        self.current_command = self.f.readline().strip()

        # Skip empty lines and comments
        while not self.current_command or self.current_command[0] == "/":
            self.current_command = self.f.readline().strip()

        # Remove comment if there is any
        comment_index = self.current_command.find("//")
        if comment_index != -1:
            self.current_command = self.current_command[:comment_index]

        self.current_command = self.current_command.strip() # Remove any trailing whitespaces
        return self.current_command


    def command_type(self):
        """Returns the type of the current VM command. C_ARITHMETIC is returned for all the arithmetic commands."""

        if self.current_command in Parser.ARITHMETIC_LOGICAL_COMMANDS:
            return "C_ARITHMETIC"
        elif "push" in self.current_command:
            return "C_PUSH"
        elif "pop" in self.current_command:
            return "C_POP"
        elif "label" in self.current_command:
            return "C_LABEL"
        elif "if" in self.current_command:
            return "C_IF"
        elif "goto" in self.current_command:
            return "C_GOTO"
        elif "function" in self.current_command:
            return "C_FUNCTION"
        elif "return" in self.current_command:
            return "C_RETURN"
        elif "call" in self.current_command:
            return "C_CALL"


    def arg1(self):
        """Returns the first argument of the current command.
        In the case of C_ARITHMETIC, the command itself (sub, add etc.) is returned.
        Should not be called if the current command is C_RETURN."""

        arguments = self.current_command.split(" ")
        if len(arguments) == 1:
            return arguments[0]
        else:
            return arguments[1]


    def arg2(self):
        """Returns the second argument of the current command.
        Should be called only if the current command is C_PUSH, C_POP, C_FUNCTION or C_CALL."""

        arguments = self.current_command.split(" ")
        return arguments[2]


    def close_file(self):
        self.f.close()
