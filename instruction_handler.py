import sys
from globals import *


def splitVar(var):
    try:
        return var.split("@")[1]
    except AttributeError:
        sys.exit(56)


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

    # helper debug function to print contents of frames and stacks
    def printMemory(self):
        print(self.ins.name)
        print(f"GF | {self.GF.values}")
        try:
            print(f"LF | {self.LF.values}")
        except AttributeError:
            print(f"LF | <EMPTY>")
        try:
            print(f"TF | {self.TF.values}")
        except AttributeError:
            print(f"TF | <EMPTY>")

        print(f"DataStack | {self.dataStack.values}")
        print(f"FrameStack | {[self.frameStack.frames[x].values for x in range(len(self.frameStack.frames))]}")
        print(f"CallStack | {self.callStack.values}\n")

    def checkInstruction(self, ins):
        self.ins = ins
        method = getattr(InstructionHandler, self.ins.name)
        method(self)

    def checkDefined(self, arg):
        try:
            if arg.value in self.__dict__[arg.frame].values:
                return True
            else:
                return False
        except AttributeError:
            sys.exit(55)

    def moveFromFrame(self, arg):
        try:
            return self.__dict__[arg.frame].values[arg.value]
        except KeyError:
            sys.exit(54)
        except AttributeError:
            sys.exit(55)

    def checkArg1Var(self):
        if self.ins.arg1.type != 'var':
            sys.exit(53)

    def getSymb(self, typeref, arg=None):
        if arg is None:
            return None
        if arg.type in typeref or arg.type == 'var':
            try:
                type, val = self.__dict__[arg.frame].values[arg.value]
            except KeyError:
                val = arg.value
                type = arg.type
            except TypeError:
                sys.exit(54)
            except AttributeError:
                sys.exit(55)
        else:
            sys.exit(53)
        return type, val

    def getSymbs(self, typeref1, typeref2, arg2=None, arg3=None):
        type1, val1 = self.getSymb(typeref1, arg2)
        type2, val2 = self.getSymb(typeref2, arg3)
        if type1 == type2:
            return type1, val1, val2

    def moveToVar(self, type, value):
        value = str(value)
        try:
            self.checkDefined(self.ins.arg1)
        except AttributeError:
            sys.exit(54)
        self.__dict__[self.ins.arg1.frame].values[self.ins.arg1.value] = (type, value)

    def MOVE(self):
        try:
            self.checkArg1Var()
            if self.checkDefined(self.ins.arg1):
                try:
                    self.checkDefined(self.ins.arg2)
                except KeyError:
                    self.moveToVar(self.ins.arg2.type, self.ins.arg2.value)
                except AttributeError:
                    sys.exit(55)
                else:
                    self.__dict__[self.ins.arg1.frame].values[self.ins.arg1.value] = self.moveFromFrame(
                        self.ins.arg2)
            else:
                sys.exit(52)
        except AttributeError:
            sys.exit(55)

    def CREATEFRAME(self):
        self.TF = Frame()

    def PUSHFRAME(self):
        try:
            self.LF = self.TF
            self.frameStack.push(self.LF)
            self.TF = None
        except AttributeError:
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
        pass

    def RETURN(self):
        pass

    def PUSHS(self):
        self.dataStack.push(self.ins.arg1.type, self.ins.arg1.value)

    def POPS(self):
        self.checkArg1Var()
        if self.checkDefined(self.ins.arg1):
            self.__dict__[self.ins.arg1.frame].values[self.ins.arg1.value] = self.dataStack.pop()

    def ADD(self):
        self.checkArg1Var()
        if not self.checkDefined(self.ins.arg1):
            sys.exit(54)

        type, val1, val2 = self.getSymbs(['int', 'var'], ['int', 'var'], self.ins.arg2, self.ins.arg3)

        try:
            val = int(val1) + int(val2)
        except ValueError:
            sys.exit(53)

        self.moveToVar(type, val)

    def SUB(self):
        self.checkArg1Var()
        if not self.checkDefined(self.ins.arg1):
            sys.exit(54)

        type, val1, val2 = self.getSymbs(['int'], ['int'], self.ins.arg2, self.ins.arg3)

        try:
            val = int(val1) - int(val2)
        except ValueError:
            sys.exit(53)

        self.moveToVar(type, val)

    def MUL(self):
        self.checkArg1Var()
        if not self.checkDefined(self.ins.arg1):
            sys.exit(54)

        type, val1, val2 = self.getSymbs(['int'], ['int'], self.ins.arg2, self.ins.arg3)

        try:
            val = int(val1) * int(val2)
        except ValueError:
            sys.exit(53)

        self.moveToVar(type, val)

    def IDIV(self):
        self.checkArg1Var()
        if not self.checkDefined(self.ins.arg1):
            sys.exit(54)

        type, val1, val2 = self.getSymbs(['int'], ['int'], self.ins.arg2, self.ins.arg3)

        try:
            val = int(val1) // int(val2)
        except ValueError:
            sys.exit(53)
        except ZeroDivisionError:
            sys.exit(57)

        self.moveToVar(type, val)

    def LT(self):

        if self.ins.arg1.type != 'var' or self.ins.arg2.type != self.ins.arg3.type and self.ins.arg2.type != 'nil':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1, val2 = self.getSymbs(['int', 'string', 'bool'], ['int', 'string', 'bool'], self.ins.arg2,
                                         self.ins.arg3)

        try:
            val = val1 < val2
        except ValueError:
            sys.exit(53)
        except ZeroDivisionError:
            sys.exit(57)

        val = str(val).lower()
        self.moveToVar('bool', val)

    def GT(self):
        if self.ins.arg1.type != 'var' or self.ins.arg2.type != self.ins.arg3.type and self.ins.arg2.type != 'nil':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1, val2 = self.getSymbs(['int', 'string', 'bool'], ['int', 'string', 'bool'], self.ins.arg2,
                                         self.ins.arg3)

        try:
            val = val1 > val2
        except ValueError:
            sys.exit(53)
        except ZeroDivisionError:
            sys.exit(57)

        val = str(val).lower()
        self.moveToVar('bool', val)

    def EQ(self):
        if self.ins.arg1.type != 'var' or self.ins.arg2.type != self.ins.arg3.type and self.ins.arg2.type != 'nil':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1, val2 = self.getSymbs(['int', 'string', 'bool'], ['int', 'string', 'bool'], self.ins.arg2,
                                         self.ins.arg3)

        try:
            val = val1 == val2
        except ValueError:
            sys.exit(53)
        except ZeroDivisionError:
            sys.exit(57)

        val = str(val).lower()
        self.moveToVar('bool', val)

    def AND(self):
        self.checkArg1Var()
        self.checkDefined(self.ins.arg1)

        type, val1, val2 = self.getSymbs(['bool'], ['bool'], self.ins.arg2, self.ins.arg3)

        if val1 == 'None' or val2 == 'None':
            sys.exit(53)

        if val1 == 'true':
            val1 = True
        elif val1 == 'false':
            val1 = False
        if val2 == 'true':
            val2 = True
        elif val2 == 'false':
            val2 = False

        try:
            val = val1 and val2
            val = str(val)
        except ValueError:
            sys.exit(53)

        self.moveToVar('bool', val.lower())

    def OR(self):
        if self.ins.arg1.type != 'var':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1, val2 = self.getSymbs(['bool'], ['bool'], self.ins.arg2, self.ins.arg3)

        if val1 == 'None' or val2 == 'None':
            sys.exit(53)

        if val1 == 'true':
            val1 = True
        elif val1 == 'false':
            val1 = False
        if val2 == 'true':
            val2 = True
        elif val2 == 'false':
            val2 = False

        try:
            val = val1 or val2
            val = str(val)
        except ValueError:
            sys.exit(53)

        self.moveToVar('bool', val.lower())

    def NOT(self):
        if self.ins.arg1.type != 'var' and self.ins.arg3 is None:
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1 = self.getSymb(['bool'], self.ins.arg2)

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
        if self.ins.arg1.type != 'var' and self.ins.arg2.type == 'int':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1 = self.getSymb(['int'], self.ins.arg2)

        if val1 == 'None':
            sys.exit(53)

        try:
            val = chr(int(val1))
        except ValueError:
            sys.exit(53)

        self.moveToVar('str', val)

    def STRI2INT(self):
        if self.ins.arg1.type != 'var':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1, val2 = self.getSymbs(['string'], ['int'], self.ins.arg2, self.ins.arg3)

        if val1 == 'None' or val2 == 'None':
            sys.exit(53)

        try:
            val = ord(val1[int(val2)])
        except ValueError:
            sys.exit(53)

        self.moveToVar('int', val)

    def READ(self):
        pass

    def WRITE(self):
        pass

    def CONCAT(self):
        if self.ins.arg1.type != 'var' and self.ins.arg2.type == 'string' and self.ins.arg3.type == 'string':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1, val2 = self.getSymbs(['string'], ['string'], self.ins.arg2, self.ins.arg3)

        if val1 == 'None' or val2 == 'None':
            sys.exit(53)

        try:
            val = val1 + val2
            val = str(val)
        except ValueError:
            sys.exit(53)

        self.moveToVar('string', val.lower())

    def STRLEN(self):
        if self.ins.arg1.type != 'var' and self.ins.arg2.type == 'string':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1, _ = self.getSymbs(['string'], ['string'], self.ins.arg2)

        if val1 == 'None':
            sys.exit(53)

        try:
            val = len(val1)
        except ValueError:
            sys.exit(53)

        self.moveToVar('int', val)

    def GETCHAR(self):  # TODO
        if self.ins.arg1.type != 'var':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1, val2 = self.getSymbs(['string'], ['int'], self.ins.arg2, self.ins.arg3)

        if val1 == 'None' or val2 == 'None':
            sys.exit(53)

        try:
            val = val1[int(val2)]
            val = str(val)
        except ValueError:
            sys.exit(53)
        except IndexError:
            sys.exit(58)

    def SETCHAR(self):  # TODO
        if self.ins.arg1.type != 'var' and self.ins.arg2.type == 'string' and self.ins.arg3.type == 'int':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        type, val1, val2 = self.getSymbs(['string'], ['int'], self.ins.arg2, self.ins.arg3)

        if val1 == 'None' or val2 == 'None':
            sys.exit(53)

        try:
            val = val1[int(val2)]
            val = str(val)
        except ValueError:
            sys.exit(53)
        self.moveToVar('string', val.lower())

    def TYPE(self):
        if self.ins.arg1.type != 'var' and self.ins.arg2.type == 'string':
            sys.exit(53)
        self.checkDefined(self.ins.arg1)

        if self.isInFrames(self.ins.arg2.id):
            val1 = self.locateVariable(self.ins.arg2.frame, self.ins.arg2.id)
            if val1 is not None:
                type, value = val1.split("@")
                if type in ['int', 'string', 'bool', 'nil']:
                    val1 = value
                else:
                    sys.exit(53)
            else:
                sys.exit(56)

        elif self.ins.arg2.type in ['int', 'string', 'bool', 'nil']:
            val1 = self.ins.arg2.value
        else:
            self.checkDefined(self.ins.arg2)
            val1 = "None"

        if val1 == 'None':
            sys.exit(53)
        if type == 'nil':
            type = ''

        self.moveToVar('string', type)

    def LABEL(self):
        pass

    def JUMP(self):
        pass

    def JUMPIFEQ(self):
        pass

    def JUMPIFNEQ(self):
        pass

    def EXIT(self):
        if self.ins.arg1.type == 'int':
            if 0 <= int(str(self.ins.arg1.value)) <= 49:
                sys.exit(int(str(self.ins.arg1.value)))
            else:
                sys.exit(57)
        elif self.ins.arg1.type == 'var':
            if self.checkDefined(self.ins.arg1):
                type, val = self.__dict__[self.ins.arg1.frame].values[self.ins.arg1.value]
                if type == 'int':
                    val = int(str(val))
                    if 0 <= val <= 49:
                        sys.exit(val)
                    else:
                        sys.exit(57)
            else:
                sys.exit(54)
        else:
            sys.exit(53)

    def DPRINT(self):
        pass

    def BREAK(self):
        pass


ih = InstructionHandler()
