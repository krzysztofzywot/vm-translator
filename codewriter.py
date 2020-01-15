class CodeWriter:

    SEGMENTS = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT"
    }
    # Counters are used to avoid name collisions in labels.
    ARITHMETIC_COUNTER = 0
    RETURN_COUNTER = 0

    def __init__(self, fname):
        try:
            self.f = open(fname + ".asm", "w")
        except IOError:
            raise IOError

        # In case of translating multiple files, name of the directory will be used to determine output file name.
        self.fname = fname
        # Current file name must be set to properly manage static segments (each file needs separate one).
        self.curr_file_name = ""
        # Keep track of currently parsed function (if any) to create correct labels.
        self.curr_function = ""


    def write_arithmetic(self, command):
        """Writes to the output file the assembly code that implements
        the given arithemetic command"""

        if command == "add":
            self.f.write(
                "// add\n"
                "@SP\n"
                "A=M-1\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M-1\n"
                "D=D+M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=D\n"
                "@SP\n"
                "M=M+1\n"
            )
        elif command == "sub":
            self.f.write(
                "// sub\n"
                "@SP\n"
                "A=M-1\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M-1\n"
                "D=M-D\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=D\n"
                "@SP\n"
                "M=M+1\n"
            )
        elif command == "neg":
            self.f.write(
                "// neg\n"
                "@SP\n"
                "A=M-1\n"
                "M=!M\n"
                "M=M+1\n"
            )
        elif command == "eq":
            self.f.write(
                "// eq\n"
                "@SP\n"
                "A=M-1\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M-1\n"
                "D=D-M\n"
                f"@EQUAL{CodeWriter.ARITHMETIC_COUNTER}\n"                                                        
                "D;JEQ\n"
                f"@NOTEQUAL{CodeWriter.ARITHMETIC_COUNTER}\n"                                                   
                "0;JMP\n"
                f"(EQUAL{CodeWriter.ARITHMETIC_COUNTER})\n"                                                
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=-1\n"
                "@SP\n"
                "M=M+1\n"
                f"@EQUEND{CodeWriter.ARITHMETIC_COUNTER}\n"                                                                
                "0;JMP\n"
                f"(NOTEQUAL{CodeWriter.ARITHMETIC_COUNTER})\n"                                                                   
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=0\n"
                "@SP\n"
                "M=M+1\n"
                f"(EQEND{CodeWriter.ARITHMETIC_COUNTER})\n"
            )
        elif command == "gt":
            self.f.write(
                "// gt\n"
                "@SP\n"
                "A=M-1\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M-1\n"
                "D=M-D\n"
                f"@GREATER{CodeWriter.ARITHMETIC_COUNTER}\n"                                                                  
                "D;JGT\n"
                f"@LESS{CodeWriter.ARITHMETIC_COUNTER}\n"                                                               
                "0;JMP\n"
                f"(GREATER{CodeWriter.ARITHMETIC_COUNTER})\n"                                                                  
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=-1\n"
                f"@GTEND{CodeWriter.ARITHMETIC_COUNTER}\n"                                                                
                "0;JMP\n"
                f"(LESS{CodeWriter.ARITHMETIC_COUNTER})\n"                                                               
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=0\n"
                f"@GTEND{CodeWriter.ARITHMETIC_COUNTER}\n"                                                                
                "0;JMP\n"
                f"(GTEND{CodeWriter.ARITHMETIC_COUNTER})\n"                                                                
                "@SP\n"
                "M=M+1\n"
            )
        elif command == "lt":
            self.f.write(
                "// lt\n"
                "@SP\n"
                "A=M-1\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M-1\n"
                "D=M-D\n"
                f"@LESS{CodeWriter.ARITHMETIC_COUNTER}\n"
                "D;JLT\n"
                f"@GREATER{CodeWriter.ARITHMETIC_COUNTER}\n"
                "0;JMP\n"
                f"(LESS{CodeWriter.ARITHMETIC_COUNTER})\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=-1\n"
                f"@GTEND{CodeWriter.ARITHMETIC_COUNTER}\n"
                "0;JMP\n"
                f"(GREATER{CodeWriter.ARITHMETIC_COUNTER})\n"
                "@SP\n"
                "M=M-1\n"
                "A=M\n"
                "M=0\n"
                f"@GTEND{CodeWriter.ARITHMETIC_COUNTER}\n"
                "0;JMP\n"
                f"(GTEND{CodeWriter.ARITHMETIC_COUNTER})\n"
                "@SP\n"
                "M=M+1\n"
            )
        elif command == "and":
            self.f.write(
                "// and\n"
                "@SP\n"
                "A=M-1\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M-1\n"
                "M=D&M\n"
            )
        elif command == "or":
            self.f.write(
                "// or\n"
                "@SP\n"
                "A=M-1\n"
                "D=M\n"
                "@SP\n"
                "M=M-1\n"
                "A=M-1\n"
                "M=D|M\n"
            )
        elif command == "not":
            self.f.write(
                "// not\n"
                "@SP\n"
                "A=M-1\n"
                "M=!M\n"
            )

        if command in ["eq", "gt", "lt"]:
            CodeWriter.ARITHMETIC_COUNTER += 1


    def write_push_pop(self, command, segment, index):
        """Writes to the output file the assembly code that implements the given command,
        where command is either C_PUSH or C_POP."""

        self.f.write(f"// {command} {segment} {index}\n")

        if command == "C_PUSH":
            if segment == "constant":
                self.f.write(
                    f"@{index}\n"
                    "D=A\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
            elif segment == "static":
                self.f.write(
                    f"@{self.curr_file_name}.{index}\n"
                    "D=M\n"
                    "@SP\n"
                    "M=M+1\n"
                    "A=M-1\n"
                    "M=D\n"
                )
            elif segment == "temp" or segment == "pointer":
                temp_address = 5
                pointer_address = 3

                base_address = temp_address if segment == "temp" else pointer_address

                self.f.write(
                    f"@{index}\n"
                    "D=A\n"
                    f"@{base_address}\n"
                    "A=D+A\n"
                    "D=M\n"
                    "@SP\n"
                    "M=M+1\n"
                    "A=M-1\n"
                    "M=D\n"
                )
            else:
                segment_name = CodeWriter.SEGMENTS[segment]

                self.f.write(
                    f"@{index}\n"
                    "D=A\n"
                    f"@{segment_name}\n"
                    "A=D+M\n"
                    "D=M\n"
                    "@SP\n"
                    "A=M\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M+1\n"
                )
        elif command == "C_POP":
            if segment == "static":
                self.f.write(
                    "@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "D=M\n"
                    f"@{self.curr_file_name}.{index}\n"
                    "M=D\n"
                )
            elif segment == "temp" or segment == "pointer":
                temp_address = 5
                pointer_address = 3

                base_address = temp_address if segment == "temp" else pointer_address

                self.f.write(
                    f"@{index}\n"
                    "D=A\n"
                    f"@{base_address}\n"
                    "D=D+A\n"
                    "@temp_address\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "D=M\n"
                    "@temp_address\n"
                    "A=M\n"
                    "M=D\n"
                )
            else:
                segment_name = CodeWriter.SEGMENTS[segment]

                self.f.write(
                    f"@{index}\n"
                    "D=A\n"
                    f"@{segment_name}\n"
                    "D=D+M\n"
                    "@temp_address\n"
                    "M=D\n"
                    "@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "D=M\n"
                    "@temp_address\n"
                    "A=M\n"
                    "M=D\n"
                )


    def write_init(self):
        """Writes the assembly code that effects the VM initialization (also called bootstrap code).
        This code should be placed in the ROM beginning in address 0x0000."""

        self.f.write(
            "// bootstrap code\n"
            "@256\n"
            "D=A\n"
            "@SP\n"
            "M=D\n"
        )

        self.write_call("Sys.init", 0)


    def write_label(self, label):
        """Writes the assembly code that is the translation of the given label command"""

        self.f.write(
            f"// label {label}\n"
            f"({self.curr_function}${label})\n"
        )


    def write_goto(self, label):
        """Writes the assembly code that is the translation of the given goto command."""

        self.f.write(
            f"// goto {label}\n"
            f"@{self.curr_function}${label}\n"
            "0;JMP\n"
        )


    def write_if(self, label):
        """Writes the assembly code that is the translation of the given if-goto command."""

        self.f.write(
            f"// if-goto {label}\n"
            "@SP\n"
            "M=M-1\n"
            "A=M\n"
            "D=M\n"
            f"@{self.curr_function}${label}\n"
            "D;JNE\n"
        )


    def write_call(self, function_name, num_args):
        """Writes the assembly code that is the translation of the given Call command."""

        self.curr_function = function_name # Used to correctly write labels

        self.f.write(
            f"// call {function_name} {num_args}\n"
            f"@{function_name}$ret.{CodeWriter.RETURN_COUNTER}\n" # Push the return address.
            "D=A\n"
            "@SP\n"
            "M=M+1\n"
            "A=M-1\n"
            "M=D\n"
            "@LCL\n" # Push LCL of the caller.
            "D=M\n"
            "@SP\n"
            "M=M+1\n"
            "A=M-1\n"
            "M=D\n"
            "@ARG\n" # Push ARG of the caller.
            "D=M\n"
            "@SP\n"
            "M=M+1\n"
            "A=M-1\n"
            "M=D\n"
            "@THIS\n" # Push THIS of the caller.
            "D=M\n"
            "@SP\n"
            "M=M+1\n"
            "A=M-1\n"
            "M=D\n"
            "@THAT\n" # Push THAT of the caller.
            "D=M\n"
            "@SP\n"
            "M=M+1\n"
            "A=M-1\n"
            "M=D\n"
            f"@{num_args}\n" # Reposition ARG pointer to point to the first pushed argument of this function.
            "D=A\n"
            "@SP\n"
            "D=M-D\n"
            "@5\n"
            "D=D-A\n"
            "@ARG\n"
            "M=D\n"
            "@SP\n" # Reposition LCL. It should point to the same address that SP points to.
            "D=M\n"
            "@LCL\n"
            "M=D\n"
            f"@{function_name}\n" # Go to the called function.
            "0;JMP\n"
            f"({function_name}$ret.{CodeWriter.RETURN_COUNTER})\n" # Declare a label for the return address.
        )

        CodeWriter.RETURN_COUNTER += 1


    def write_function(self, function_name, num_locals):
        """Writes the assembly code that is the trans. of the given Function command."""

        num_locals_int = int(num_locals)
        if num_locals_int > 0:
            push_zero = "@SP\nM=M+1\nA=M-1\nM=0\n" * num_locals_int # Push num_locals number of zeroes to the stack.
        else:
            push_zero = ""

        self.f.write(
            f"// function {function_name} {num_locals}\n"
            f"({function_name})\n"
            f"{push_zero}"
        )


    def write_return(self):
        """Writes the assembly code that is the translation of the given Return command. """

        self.f.write(
            "// return\n"
            "@LCL\n" # Create a temporary variable called endframe and store the value of LCL in it.
            "D=M\n"
            f"@endframe\n"
            "M=D\n"
            "@5\n" # Get the return address and store it in a temporary variable.
            "D=D-A\n"
            "A=D\n"
            "D=M\n"
            f"@returnaddress\n"
            "M=D\n"
            "@SP\n" # Pop the return value from the stack.
            "M=M-1\n"
            "A=M\n"
            "D=M\n"
            "@ARG\n" # Store the return value in ARG[0].
            "A=M\n"
            "M=D\n"
            "@ARG\n" # Position the stack pointer just after the return value (ARG[0]).
            "D=M\n"
            "@SP\n"
            "M=D+1\n"
            f"@endframe\n" # Restore THAT of the caller.
            "M=M-1\n"
            "A=M\n"
            "D=M\n"
            "@THAT\n"
            "M=D\n"
            f"@endframe\n" # Restore THIS of the caller.
            "M=M-1\n"
            "A=M\n"
            "D=M\n"
            "@THIS\n"
            "M=D\n"
            f"@endframe\n" # Restore ARG of the caller.
            "M=M-1\n"
            "A=M\n"
            "D=M\n"
            "@ARG\n"
            "M=D\n"
            f"@endframe\n" # Restore LCL of the caller.
            "M=M-1\n"
            "A=M\n"
            "D=M\n"
            "@LCL\n"
            "M=D\n"
            f"@returnaddress\n" # Go to the return address.
            "A=M\n"
            "0;JMP\n"
        )


    def close_file(self):
        self.f.close()
