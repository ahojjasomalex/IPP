import sys
import re
from globals import *


#  object for representing instruction
class Instruction:
    def __init__(self, ins):
        try:
            #  check if opcode is valid
            opcode = ins.attrib["opcode"].upper()
            if opcode in OPCODES:
                self.name = opcode
            else:
                sys.exit(32)
            self.order = ins.attrib["order"]
        except KeyError:  # key doesn't exist
            sys.exit(32)

        #  check if element tag is 'instruction'
        if ins.tag == 'instruction':
            args = list(ins)  # get args into list
        else:
            sys.exit(32)
        # arguments can be unsorted, so sort them
        args.sort(key=lambda x: x.tag)

        # if arg doesn't exist, insert None, so empty object can be created
        if len(args) == 0:
            args = [None] * 3
        elif len(args) == 1:
            args = args + [None] * 2
        elif len(args) == 2:
            args = args + [None]

        #  arg presence flags
        arg1 = False
        arg2 = False
        arg3 = False

        i = 1  # counter for args

        # creating arg objects for every instruction
        for item in args:
            if item is not None:
                if item.tag == "arg1" and arg2 is False and arg3 is False:
                    # print("CREATING ARG1 OBJECT\n")
                    self.arg1 = Argument(item)
                    arg1 = True
                    i += 1
                    continue

                elif item.tag == "arg2" and arg1 is True and arg3 is False:
                    # print("CREATING ARG2 OBJECT\n")
                    self.arg2 = Argument(item)
                    arg2 = True
                    i += 1
                    continue

                elif item.tag == "arg3" and arg1 is True and arg2 is True:
                    # print("CREATING ARG3 OBJECT\n")
                    self.arg3 = Argument(item)
                    arg3 = True
                    i += 1
                    continue

                else:
                    sys.exit(32)

            elif i == 1:
                self.arg1 = Argument(None)
                # print("CREATING EMPTY ARG1 OBJECT\n")
            elif i == 2:
                self.arg2 = Argument(None)
                # print("CREATING EMPTY ARG2 OBJECT\n")
            elif i == 3:
                self.arg3 = Argument(None)
                # print("CREATING EMPTY ARG3 OBJECT\n")
            i += 1


#  object for representing instruction arguments
class Argument:
    def __init__(self, arg=None):  # default is None so empty object can be created
        self.frame = None  # frame init to None, will be rewritten if arg type is var

        if arg is None:
            self.type = None
            self.value = None
            self.id = None
        else:
            self.type = arg.attrib['type']
            self.value = arg.text
            # string is empty not None
            if self.type == "string" and self.value is None:
                self.value = ""

        if self.type is not None:
            if self.typeCheck() is None:
                sys.exit(32)

    def typeCheck(self):
        if self.type == 'label':
            if re.match('^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([0-9]|[a-zA-Z]|_|-|\$|&|%|\*|!|\?)*$', self.value):
                self.id = self.type + "@" + self.value
                return True
        elif self.type == 'var':
            if re.match('^(GF|LF|TF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([0-9]|[a-zA-Z]|_|-|\$|&|%|\*|!|\?)*$', self.value):
                self.frame, self.value = self.value.split("@")  # split variable into frame and value
                self.id = self.frame + "@" + self.value
                return True
        elif self.type == 'string':
            # check if string contains escape sequences
            if re.search('(((([^\\\\]*)((\\[0-9]{3})*))[^\\\\]*)*)', self.value) is None:
                return None
            else:
                # if yes, un-escape escape sequences
                self.value = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x.group(1))), self.value)
                self.id = self.type + "@" + self.value
                return True
        elif self.type == 'bool':
            if re.match('^(true|false)$', self.value):
                self.id = self.type + "@" + self.value
                return True
        elif self.type == 'int':
            if re.match('^[+-]{0,1}[0-9]+$', self.value):
                self.id = self.type + "@" + self.value
                return True
        elif self.type == 'nil':
            if re.match('^nil$', self.value):
                self.id = self.type + "@" + self.value
                return True
        elif self.type == 'type':
            if re.match('^(label|var|string|bool|int|nil)$', self.value):
                self.id = self.type + "@" + self.value
                return True
        else:
            return None
