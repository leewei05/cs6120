import sys
import json
from collections import OrderedDict

TERMINATORS = ["jmp", "ret", "br"]

def new_bb_name(num):
    return "b" + str(num)

# input func['instrs']
def form_bb(instrs):
    """ Creates basic blocks within a single function.
    """
    # name2bb maps basic block name to list of instructions
    name2bb = OrderedDict()
    num = 0
    curr_bb = []
    old_bb = []
    # temporary basic block name
    name = ""
    for i, instr in enumerate(instrs):
        if 'label' in instr and i == 0:
            name = instr['label']
            continue
        elif 'label' in instr and i != 0:
            if name == "":
               name = new_bb_name(num)
               num += 1

            old_bb = curr_bb
            name2bb[name] = curr_bb
            curr_bb = []
            name = instr['label']
        elif instr in TERMINATORS or instr == instrs[-1]:
            if name == "":
               name = new_bb_name(num)
               num += 1

            curr_bb.append(instr)
            name2bb[name] = curr_bb
            curr_bb = []
        else:
            curr_bb.append(instr)

    name2bb[name] = curr_bb

    return name2bb

def main():
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        bb = form_bb(func['instrs'])
        print(bb)

if __name__ == "__main__":
    main()