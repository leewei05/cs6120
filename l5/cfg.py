import sys
import json
import basic_block
from collections import OrderedDict

TERMINATORS = ["jmp", "ret", "br"]

class CFG():
    # predecessor
    pred = {}
    # successor
    succ = {}
    bb = OrderedDict()

    def __init__(self, bb) -> None:
        self.pred.clear()
        self.succ.clear()
        self.bb.clear()
        self.bb = bb
        self.form_cfg()

    def last_key(self):
        return next(reversed(self.bb))

    def form_cfg(self):
        """ Forms control flow graph from a series of basic blocks.
        """
        for i, (k, bb) in enumerate(self.bb.items()):
            # intialize pred map
            self.pred[k] = []

            if len(bb) == 0:
                self.succ[k] = []
                continue
            else:
                last_instr = bb[-1]

            if 'op' in last_instr and last_instr['op'] in TERMINATORS:
                match last_instr['op']:
                    case "jmp" | "br":
                        self.succ[k] = last_instr['labels']
                    case "ret":
                        self.succ[k] = []
                    case _:
                        print("not a terminator!")
            else:
                # check curr bb is not last
                if k != self.last_key():
                    next = list(self.bb)[i + 1]
                    self.succ[k] = [next]
                else:
                    self.succ[k] = []

        for k, bbs in self.succ.items():
            for bb in bbs:
                self.pred[bb].append(k)

    def print_cfg(self):
        print("===== succesors =====")
        for k, succ in self.succ.items():
            print(f'{k} succ: {succ}')

        print("")
        print("===== predecessors =====")
        for k, pred in self.pred.items():
            print(f'{k} pred: {pred}')

def main():
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        bb = basic_block.form_bb(func['instrs'])
        cfg = CFG(bb)
        cfg.print_cfg()

if __name__ == "__main__":
    main()