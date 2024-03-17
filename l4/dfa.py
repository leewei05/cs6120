import sys
import json
import basic_block
import cfg as worker
from collections import OrderedDict

class DFA:
    """ Data flow analysis
    """

    # List of cfgs
    cfgs = []

    def __init__(self, prog) -> None:
        for func in prog['functions']:
            bb = basic_block.form_bb(func['instrs'])
            cfg = worker.CFG(bb)
            self.cfgs.append(cfg)

    def live(self):
        print("live")

    def init_input(self, od: OrderedDict):
        input = {}
        entry = list(od)[0]
        input[entry] = []

        return input

    def init_out(self, od: OrderedDict):
        out = {}
        for k, instrs in od.items():
            # analyze logic
            out[k] = set()
            for instr in instrs:
                if 'dest' in instr:
                    out[k].add(instr['dest'])

        return out

    def merge(self, cfg: worker.CFG, curr, out):
        merged = set()
        for p in cfg.pred[curr]:
            # analyze logic
            for dest in list(out[p]):
                merged.add(dest)

        return merged

    def transfer(self, instrs, input: set):
        new_out = input.copy()
        for instr in instrs:
            if 'dest' in instr:
                new_out.add(instr['dest'])

        return new_out

    def defined(self):
        for cfg in self.cfgs:
            (input, out) = self.defined_analyzer(cfg)
            print_analysis(input, out)

    def defined_analyzer(self, cfg: worker.CFG):
        """ Reaching definition analyzer
        """
        input = self.init_input(cfg.bb)
        out = self.init_out(cfg.bb)

        worklist = list(cfg.bb)
        while worklist:
            b = worklist[0]
            input[b] = self.merge(cfg, b, out)
            old = len(out[b])
            out[b] = self.transfer(cfg.bb[b], input[b])

            if old != len(out[b]):
                for succ in cfg.succ[b]:
                    if succ not in worklist:
                        worklist.append(succ)
            else:
                worklist.remove(b)

        return (input, out)

def print_analysis(input, out):
    if len(input) != len(out):
        print("Unmatched data!")
        exit(1)

    for _, k in enumerate(input):
        print(f'{k}:')
        print(f'  in: ', fmt(input[k]))
        print(f'  out:', fmt(out[k]))

def fmt(val):
    if isinstance(val, set):
        if val:
            return ', '.join(sorted(val))
        else:
            return '∅'


def main():
    prog = json.load(sys.stdin)
    argc = sys.argv
    if len(argc) < 2:
        print("Usage: python3 dfa.py <live|defined>")
        sys.exit(1)
    elif sys.argv[1] == "defined":
        dfa = DFA(prog)
        dfa.defined()
        sys.exit(0)
    elif sys.argv[1] == "live":
        sys.exit(0)
    else:
        print("Undefined analysis!")
        sys.exit(1)

if __name__ == "__main__":
    main()
