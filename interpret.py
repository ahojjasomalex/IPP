import argparse
import sys
import os.path
import xml.etree.ElementTree as ET
import re
from globals import *
from collections import Counter

from instruction import Instruction
from instruction_handler import ih


class DummyInstruction:
    """
    Class for dummy instruction in the beginning and end of the instruction list
    """

    def __init__(self):
        self.name = None
        self.order = 0


def checkFile(file):
    """
    Helper function to check if given file path is valid
    :param file: File to check
    :return: True if path is valid
    """
    if os.path.exists(file) and os.path.isfile(file) and os.access(file, os.R_OK):
        return True
    else:
        return False


# helper function to sort and check if order is valid
def checkAndSortOrder(instructions):
    # try sorting instructions by order attribute
    try:
        instructions.sort(key=lambda x: int(x.order))
    except ValueError:
        sys.exit(32)

    orderList = []
    for ins in instructions:
        if int(ins.order) >= 1:
            orderList.append(int(ins.order))
        else:
            sys.exit(32)

    #  check if order numbers are unique
    counter = Counter(orderList)
    for values in counter.values():
        if values > 1:
            sys.exit(32)

        #  reorder instructions from 1 by step 1
    for i in range(len(instructions)):
        instructions[i].order = i + 1

    return instructions


def main():
    # global variables
    INSTRUCTIONS = []  # list of all instructions
    global source  # XML source
    global input  # program input

    parse = argparse.ArgumentParser(add_help=False)
    parse.add_argument('--source', help='XML source')
    parse.add_argument('--input', help='input data')
    parse.add_argument('--help', required=False, action='store_true')
    args = parse.parse_args()

    # if --help is selected with other args
    if args.help and (args.source or args.input):
        sys.exit(10)
    # help only
    elif args.help:
        print(f"usage: interpret.py [-h] [--source SOURCE] [--input INPUT]"
              f"\n"
              f"\n"
              f"optional arguments:\n"
              f"--help           show this help message and exit\n"
              f"--source SOURCE  XML source\n"
              f"--input INPUT    input data\n")
        sys.exit(0)

    # determining where to read from for source and input
    if args.source is not None and args.input is not None:
        if checkFile(args.source) and checkFile(args.input):
            source = args.source
            input = args.input
        else:
            sys.exit(11)

    elif args.source is None and args.input is not None:
        source = "stdin"
        if checkFile(args.input):
            input = args.input
        else:
            sys.exit(11)

    elif args.input is None and args.source is not None:
        input = "stdin"
        if checkFile(args.source):
            source = args.source
        else:
            sys.exit(11)

    elif args.source is None and args.input is None:
        sys.exit(10)  # bad parameters

    # try to parse XML file
    # source file not specified -> source = stdin
    if source == "stdin":
        try:
            xmltree = ET.parse(sys.stdin)
        except ET.ParseError:
            sys.exit(31)
    # source file specified -> source = filepath
    else:
        try:
            xmltree = ET.parse(source)
        except ET.ParseError:
            sys.exit(31)

    root = xmltree.getroot()
    # print(root.attrib["language"])
    if root.tag != "program":
        sys.exit(32)

    # check for 'IPPcode22' attribute
    try:
        if re.match('^ippcode22$', root.attrib["language"], re.IGNORECASE) is None:
            sys.exit(32)
    except KeyError:
        sys.exit(31)

    for instruction in xmltree.findall("./"):
        # make new object for instruction and insert it into instruction list
        ins = Instruction(instruction)
        INSTRUCTIONS.append(ins)

    INSTRUCTIONS = checkAndSortOrder(INSTRUCTIONS)

    dummy_start = DummyInstruction()
    dummy_end = DummyInstruction()
    dummy_start.name = "DUMMY_START"
    dummy_start.order = 0
    dummy_end.name = "DUMMY_END"
    dummy_start.order = len(INSTRUCTIONS)

    INSTRUCTIONS = [dummy_start] + INSTRUCTIONS + [dummy_end]

    ih.start(INSTRUCTIONS)


if __name__ == '__main__':
    main()
