import sys
import re
from globals import *


def checkArgCount(ins):
    if ins.name in ARGC0:
        if ins.arg1.type or ins.arg2.type or ins.arg3.type is not None:
            sys.exit(32)

    if ins.name in ARGC1:
        if ins.arg1.type is None or ins.arg2.type is not None or ins.arg3.type is not None:
            sys.exit(32)

    if ins.name in ARGC2:
        if ins.arg1.type is None or ins.arg2.type is None or ins.arg3.type is not None:
            sys.exit(32)

    if ins.name in ARGC3:
        if ins.arg1.type is None or ins.arg2.type is None or ins.arg3.type is None:
            sys.exit(32)


class Frame:
    def __init__(self):
        self.values = {}

    def push(self, value):
        self.values[value] = None

    def pop(self):
        try:
            for k, v in self.values.items():
                return v.pop()
        except IndexError:
            sys.exit(55)


class FrameStack:
    def __init__(self):
        self.frames = []

    def push(self, frame):
        self.frames.append(frame)

    def pop(self):
        if len(self.frames) <= 0:
            sys.exit(55)
        else:
            return self.frames.pop()


class CallStack:
    def __init__(self):
        self.values = []

    def push(self, v):
        self.values.append(v)

    def pop(self):
        if len(self.values) <= 0:
            sys.exit(55)
        else:
            return self.values.pop()


class DataStack:
    def __init__(self):
        self.values = []

    def push(self, type, val):
        self.values.append((type, val))

    def pop(self):
        if len(self.values) <= 0:
            sys.exit(56)
        else:
            return self.values.pop()


class InstructionHandler:
    def __init__(self):

        self.ins = None

        self.GF = Frame()
        self.LF = None
        self.TF = None

        self.dataStack = DataStack()
        self.callStack = CallStack()
        self.frameStack = FrameStack()

        self.labels = {}
        self.counter = 0
        self.executed = 0
        self.input = None

    def printMemory(self):
        """
        Debug function to print contents of frames and stacks
        :return: Nothing
        """
        tabs = '\t' * 3
        frame = '-' * 60
        print('\n' + frame, file=sys.stderr)
        print("| INS" + tabs + '| ' + self.ins.name, file=sys.stderr)
        print(f"| GF{tabs}| {self.GF.values}", file=sys.stderr)
        try:
            print(f"| LF{tabs}| {self.LF.values}", file=sys.stderr)
        except AttributeError:
            print(f"| LF{tabs}| <EMPTY>", file=sys.stderr)
        try:
            print(f"| TF{tabs}| {self.TF.values}", file=sys.stderr)
        except AttributeError:
            print(f"| TF{tabs}| <EMPTY>", file=sys.stderr)

        print(f"| DataStack\t\t| {self.dataStack.values}", file=sys.stderr)
        print(f"| FrameStack\t| {[self.frameStack.frames[x].values for x in range(len(self.frameStack.frames))]}",
              file=sys.stderr)
        print(f"| CallStack\t\t| {self.callStack.values}", file=sys.stderr)
        print(f"| Labels\t\t| {self.labels}", file=sys.stderr)
        print(f"| Counter\t\t| {self.counter}", file=sys.stderr)
        print(f"| Executed INS\t| {self.executed}", file=sys.stderr)
        print(frame + '\n', file=sys.stderr)

    def checkInstruction(self, ins):
        """
        Calls respective method to handle instruction based on its name
        :param ins: Instruction object
        :return: Nothing
        """
        self.ins = ins
        # call function based on instruction name
        method = getattr(InstructionHandler, self.ins.name)
        method(self)

    def checkDefined(self, arg):
        """
        Checks if argument variable is defined on given frame {GF, LF, TF}
        :param arg: Instruction argument object
        :return: True if present
        """
        try:
            if arg.value in self.__dict__[arg.frame].values:
                return True
            else:
                return False
        except AttributeError:
            sys.exit(55)

    def moveFromFrame(self, arg):
        """
        Returns value of variable in given frame {GF, LF, TF}
        :param arg: Instruction argument object
        :return: Value of variable on given frame
        """
        try:
            return self.__dict__[arg.frame].values[arg.value]
        # nonexistent variable
        except KeyError:
            sys.exit(54)
        # nonexistent frame
        except AttributeError:
            sys.exit(55)

    def checkArg1Var(self):
        """
        Checks if arg1 is type var and calls checkDefined() method to check if variable is defined
        Used in almost every instruction method
        :return: Nothing
        """
        if self.ins.arg1.type != 'var':
            sys.exit(53)
        if not self.checkDefined(self.ins.arg1):
            sys.exit(54)

    def getSymb(self, typeref=None, arg=None):
        """
        Returns either variable or symbol type its value
        :param typeref: Reference type(s)
        :param arg: Instruction argument object
        :return: Type of argument, value of argument
        """
        if typeref is None:
            typeref = []
        if arg is None:
            return None
        if arg.type in typeref or arg.type == 'var':
            if arg.type == 'var':
                try:
                    type, val = self.moveFromFrame(arg)
                except TypeError:
                    type = None
                    val = arg.value
            else:
                try:
                    val = arg.value
                    type = arg.type
                except TypeError:
                    sys.exit(54)
        else:
            sys.exit(53)
        return type, val

    def getSymbs(self, typeref1, typeref2, arg2=None, arg3=None):
        """
        Same as getSymb(), but for 2 arguments at once
        :param typeref1: Reference type(s)
        :param typeref2: Reference type(s)
        :param arg2: Instruction argument object
        :param arg3: Instruction argument object
        :return: Type of argument, value of argument1, value of argument2
        """
        type1, val1 = self.getSymb(typeref1, arg2)
        type2, val2 = self.getSymb(typeref2, arg3)
        #  if types are incompatible -> error
        if type1 is None or type2 is None:
            sys.exit(56)
        if type1 == type2:
            return type1, val1, val2
        else:
            sys.exit(53)

    def moveToVar(self, type, value):
        """
        Moves variable type and its value in form of tuple into variable defined in arg1 of instruction
        :param type: Type of variable
        :param value: Value of variable
        :return: Nothing
        """
        value = str(value)
        try:
            self.checkDefined(self.ins.arg1)
        except AttributeError:
            sys.exit(54)
        self.__dict__[self.ins.arg1.frame].values[self.ins.arg1.value] = (type, value)

    def MOVE(self):
        self.checkArg1Var()
        type, val = self.getSymb(['int', 'string', 'bool', 'nil'], self.ins.arg2)
        if type is None:
            sys.exit(56)
        if type == 'nil':
            val = ''
        self.moveToVar(type, val)

    def CREATEFRAME(self):
        self.TF = Frame()

    def PUSHFRAME(self):
        if self.TF is not None:
            try:
                self.LF = self.TF
                self.frameStack.push(self.LF)
                self.TF = None
            except AttributeError:
                sys.exit(55)
        else:
            sys.exit(55)

    def POPFRAME(self):
        self.TF = self.frameStack.pop()
        try:
            self.LF = self.frameStack.frames[-1]
        except IndexError:
            self.LF = None

    def DEFVAR(self):
        if self.ins.arg1.type == 'var':
            try:
                if not self.checkDefined(self.ins.arg1):
                    self.__dict__[self.ins.arg1.frame].values[self.ins.arg1.value] = None
                else:
                    sys.exit(52)
            except AttributeError:
                sys.exit(55)
        else:
            sys.exit(53)

    def CALL(self):
        self.callStack.push(self.counter)
        self.JUMP()

    def RETURN(self):
        try:
            self.counter = self.labels[self.callStack.pop()]
        except KeyError:
            sys.exit(52)

    def PUSHS(self):
        self.dataStack.push(self.ins.arg1.type, self.ins.arg1.value)

    def POPS(self):
        self.checkArg1Var()
        if self.checkDefined(self.ins.arg1):
            self.__dict__[self.ins.arg1.frame].values[self.ins.arg1.value] = self.dataStack.pop()

    def ADD(self):
        self.checkArg1Var()

        type, val1, val2 = self.getSymbs(['int'], ['int'], self.ins.arg2, self.ins.arg3)

        try:
            val = int(val1) + int(val2)
        except ValueError:
            sys.exit(53)

        self.moveToVar(type, val)

    def SUB(self):
        self.checkArg1Var()

        type, val1, val2 = self.getSymbs(['int'], ['int'], self.ins.arg2, self.ins.arg3)

        try:
            val = int(val1) - int(val2)
        except ValueError:
            sys.exit(53)

        self.moveToVar(type, val)

    def MUL(self):
        self.checkArg1Var()

        type, val1, val2 = self.getSymbs(['int'], ['int'], self.ins.arg2, self.ins.arg3)

        try:
            val = int(val1) * int(val2)
        except ValueError:
            sys.exit(53)

        self.moveToVar(type, val)

    def IDIV(self):
        self.checkArg1Var()

        type, val1, val2 = self.getSymbs(['int'], ['int'], self.ins.arg2, self.ins.arg3)

        try:
            val = int(val1) // int(val2)
        except ValueError:
            sys.exit(53)
        except ZeroDivisionError:
            sys.exit(57)

        self.moveToVar(type, val)

    def LTGT(self):
        self.checkArg1Var()
        if self.ins.arg2.type == 'nil' or self.ins.arg3.type == 'nil':
            sys.exit(53)

        _, val1, val2 = self.getSymbs(['int', 'string', 'bool'], ['int', 'string', 'bool'], self.ins.arg2,
                                      self.ins.arg3)
        return val1, val2

    def LT(self):
        val1, val2 = self.LTGT()
        try:
            val = val1 < val2
        except ValueError:
            sys.exit(53)

        val = str(val).lower()
        self.moveToVar('bool', val)

    def GT(self):
        val1, val2 = self.LTGT()
        try:
            val = val1 > val2
        except ValueError:
            sys.exit(53)

        val = str(val).lower()
        self.moveToVar('bool', val)

    def EQ(self):
        self.checkArg1Var()

        type1, val1 = self.getSymb(['int', 'string', 'bool', 'nil'], self.ins.arg2)
        type2, val2 = self.getSymb(['int', 'string', 'bool', 'nil'], self.ins.arg3)

        if type1 is None or type2 is None:
            sys.exit(56)
        if type1 == type2:
            try:
                val = val1 == val2
            except ValueError:
                sys.exit(53)
            val = str(val).lower()
            self.moveToVar('bool', val)
        elif type1 == 'nil' or type2 == 'nil':
            self.moveToVar('bool', 'false')
        else:
            sys.exit(53)

    def ANDOR(self):
        self.checkArg1Var()

        _, val1, val2 = self.getSymbs(['bool'], ['bool'], self.ins.arg2, self.ins.arg3)

        if val1 == 'true':
            val1 = True
        elif val1 == 'false':
            val1 = False
        if val2 == 'true':
            val2 = True
        elif val2 == 'false':
            val2 = False

        return val1, val2

    def AND(self):
        val1, val2 = self.ANDOR()
        try:
            val = val1 and val2
            val = str(val).lower()
        except ValueError:
            sys.exit(53)

        self.moveToVar('bool', val)

    def OR(self):
        val1, val2 = self.ANDOR()
        try:
            val = val1 or val2
            val = str(val).lower()
        except ValueError:
            sys.exit(53)

        self.moveToVar('bool', val)

    def NOT(self):
        self.checkArg1Var()

        type, val1 = self.getSymb(['bool'], self.ins.arg2)
        if type is None:
            sys.exit(56)
        if type != 'bool':
            sys.exit(53)
        if type is None:
            sys.exit(56)

        if val1 == 'true':
            val1 = True
        elif val1 == 'false':
            val1 = False

        try:
            val = not val1
            val = str(val)
        except ValueError:
            sys.exit(53)

        self.moveToVar('bool', val.lower())

    def INT2CHAR(self):
        self.checkArg1Var()

        type, val1 = self.getSymb(['int'], self.ins.arg2)
        if type is None:
            sys.exit(56)
        try:
            val = chr(int(val1))
        except ValueError:
            sys.exit(58)

        self.moveToVar('string', val)

    def STRI2INT(self):
        self.checkArg1Var()

        type1, val1 = self.getSymb(['string'], self.ins.arg2)
        type2, val2 = self.getSymb(['int'], self.ins.arg3)

        try:
            val = ord(val1[int(val2)])
        except ValueError:
            sys.exit(58)
        except IndexError:
            sys.exit(58)

        self.moveToVar('int', val)

    def READ(self):
        pass

    def WRITE(self):
        type, val1 = self.getSymb(['bool', 'int', 'string', 'nil'], self.ins.arg1)

        if type is None:
            sys.exit(56)
        if type == 'nil':
            print('', end='', sep='')
        print(val1, end='', sep='')

    def CONCAT(self):
        self.checkArg1Var()

        type, val1, val2 = self.getSymbs(['string'], ['string'], self.ins.arg2, self.ins.arg3)

        try:
            val = val1 + val2
            val = str(val)
        except ValueError:
            sys.exit(53)

        self.moveToVar(type, val.lower())

    def STRLEN(self):
        self.checkArg1Var()

        type, val1 = self.getSymb(['string'], self.ins.arg2)

        if type is None:
            sys.exit(56)
        if type != 'int':
            sys.exit(53)
        try:
            val = len(val1)
        except ValueError:
            sys.exit(53)

        self.moveToVar('int', val)

    def GETCHAR(self):  # TODO
        self.checkArg1Var()

        type, val1, val2 = self.getSymbs(['string'], ['int'], self.ins.arg2, self.ins.arg3)

        try:
            val = val1[int(val2)]
            val = str(val)
        except ValueError:
            sys.exit(58)
        except IndexError:
            sys.exit(58)

    def SETCHAR(self):  # TODO
        self.checkArg1Var()

        type, val1, val2 = self.getSymbs(['string'], ['int'], self.ins.arg2, self.ins.arg3)

        try:
            val = val1[int(val2)]
            val = str(val)
        except ValueError:
            sys.exit(58)
        self.moveToVar('string', val.lower())

    def TYPE(self):
        self.checkArg1Var()
        type, val1 = self.getSymb(['int', 'string', 'bool', 'nil'], self.ins.arg2)

        if type is None:
            type = ''

        self.moveToVar('string', type)

    def LABEL(self):
        # all labels are saved at the start of interpreting, so handler method is not needed
        pass

    def JUMP(self):
        try:
            self.counter = self.labels[self.ins.arg1.value]
        except KeyError:
            sys.exit(52)

    def JUMPIFEQ(self):
        type1, val1 = self.getSymb(['int', 'string', 'bool', 'nil'], self.ins.arg2)
        type2, val2 = self.getSymb(['int', 'string', 'bool', 'nil'], self.ins.arg3)

        if type1 is None or type2 is None:
            sys.exit(56)
        if type1 == type2:
            if val1 == val2:
                try:
                    self.counter = self.labels[self.ins.arg1.value]
                except KeyError:
                    sys.exit(52)
        elif type1 == 'nil' or type2 == 'nil':
            return
        else:
            sys.exit(53)

    def JUMPIFNEQ(self):
        type1, val1 = self.getSymb(['int', 'string', 'bool', 'nil'], self.ins.arg2)
        type2, val2 = self.getSymb(['int', 'string', 'bool', 'nil'], self.ins.arg3)

        if type1 is None or type2 is None:
            sys.exit(56)
        if type1 == type2:
            if val1 != val2:
                try:
                    self.counter = self.labels[self.ins.arg1.value]
                except KeyError:
                    sys.exit(52)
        elif type1 == 'nil' or type2 == 'nil':
            try:
                self.counter = self.labels[self.ins.arg1.value]
            except KeyError:
                sys.exit(52)
        else:
            sys.exit(53)

    def EXIT(self):
        if self.ins.arg1.type == 'int':
            if 0 <= int(str(self.ins.arg1.value)) <= 49:
                sys.exit(int(str(self.ins.arg1.value)))
            else:
                sys.exit(57)
        elif self.ins.arg1.type == 'var':
            if self.checkDefined(self.ins.arg1):
                try:
                    type, val = self.__dict__[self.ins.arg1.frame].values[self.ins.arg1.value]
                except TypeError:
                    sys.exit(56)
                if type == 'int':
                    val = int(str(val))
                    if 0 <= val <= 49:
                        sys.exit(val)
                    else:
                        sys.exit(57)
                else:
                    sys.exit(53)
            else:
                sys.exit(54)
        else:
            sys.exit(53)

    def DPRINT(self):
        type, val1 = self.getSymb(['bool', 'int', 'string', 'nil'], self.ins.arg1)

        if type is None:
            sys.exit(56)
        if type == 'nil':
            print('', file=sys.stderr, end='', sep='')
        print(val1, file=sys.stderr, end='', sep='')

    def BREAK(self):
        self.printMemory()

### STACK INSTRUCTIONS ###

    def CLEARS(self):
        self.dataStack.values = []

    def ADDS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 == type2:
            val = int(val1) + int(val2)
            self.dataStack.push(type1, val)
        else:
            sys.exit(53)

    def SUBS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 == type2:
            val = int(val1) - int(val2)
            self.dataStack.push(type1, val)
        else:
            sys.exit(53)

    def MULS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 == type2:
            val = int(val1) * int(val2)
            self.dataStack.push(type1, val)
        else:
            sys.exit(53)

    def IDIVS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 == type2:
            try:
                val = int(val1) // int(val2)
            except ZeroDivisionError:
                sys.exit(57)
            self.dataStack.push(type1, val)
        else:
            sys.exit(53)

    def LTS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 == type2:
            val = val1 < val2
            val = str(val).lower()
            self.dataStack.push('bool', val)
        else:
            sys.exit(53)

    def GTS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 == type2:
            val = val1 > val2
            val = str(val).lower()
            self.dataStack.push('bool', val)
        else:
            sys.exit(53)

    def EQS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 == type2:
            try:
                val = val1 == val2
            except ValueError:
                sys.exit(53)
            val = str(val).lower()
            self.dataStack.push('bool', val)
        elif type1 == 'nil' or type2 == 'nil':
            self.dataStack.push('bool', 'false')
        else:
            sys.exit(53)

    def ANDSORS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 != 'bool' or type2 != 'bool':
            sys.exit(53)

        if val1 == 'true':
            val1 = True
        elif val1 == 'false':
            val1 = False
        if val2 == 'true':
            val2 = True
        elif val2 == 'false':
            val2 = False

        return val1, val2

    def ANDS(self):
        val1, val2 = self.ANDSORS()
        val = val1 and val2
        val = str(val).lower()
        self.dataStack.push('bool', val)

    def ORS(self):
        val1, val2 = self.ANDSORS()
        val = val1 or val2
        val = str(val).lower()
        self.dataStack.push('bool', val)

    def NOTS(self):
        type, val = self.dataStack.pop()
        if type != 'bool':
            sys.exit(53)

        if val == 'true':
            val = True
        elif val == 'false':
            val = False

        val = str(not val).lower()
        self.dataStack.push('bool', val)

    def INT2CHARS(self):
        type, val = self.dataStack.pop()
        if type != 'int':
            sys.exit(53)
        try:
            val = chr(int(val))
        except ValueError:
            sys.exit(58)
        self.dataStack.push('string', val)

    def STRI2INTS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 != 'string' or type2 != 'int':
            sys.exit(53)

        try:
            val = ord(val1[int(val2)])
        except ValueError:
            sys.exit(58)
        except IndexError:
            sys.exit(58)

        self.dataStack.push('int', val)

    def JUMPIFEQS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 == type2:
            if val1 == val2:
                try:
                    self.counter = self.labels[self.ins.arg1.value]
                except KeyError:
                    sys.exit(52)
        elif type1 == 'nil' or type2 == 'nil':
            return
        else:
            sys.exit(53)

    def JUMPIFNEQS(self):
        type2, val2 = self.dataStack.pop()
        type1, val1 = self.dataStack.pop()

        if type1 == type2:
            if val1 != val2:
                try:
                    self.counter = self.labels[self.ins.arg1.value]
                except KeyError:
                    sys.exit(52)
        elif type1 == 'nil' or type2 == 'nil':
            try:
                self.counter = self.labels[self.ins.arg1.value]
            except KeyError:
                sys.exit(52)
        else:
            sys.exit(53)

    def getAllLabels(self, instructions):
        for i in instructions[1:-1]:  # skip dummy instructions
            if re.match('^label$', i.name, re.IGNORECASE):
                if i.arg1.value not in self.labels:
                    self.labels[i.arg1.value] = i.order
                else:
                    sys.exit(52)

    def initInput(self):
        if input == 'stdin':
            self.input = sys.stdin

    def start(self, instructions):
        self.getAllLabels(instructions)

        while True:
            ins = instructions[self.counter]
            if ins.name == "DUMMY_START":
                self.counter += 1
                continue
            if ins.name == "DUMMY_END":
                break

            checkArgCount(ins)
            self.checkInstruction(ins)
            self.counter += 1
            self.executed += 1
            self.printMemory()


ih = InstructionHandler()
