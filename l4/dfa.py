import sys
import json
import basic_block
import cfg as data
from collections import OrderedDict
from abc import ABC, abstractmethod

def form_cfgs(prog):
    cfgs = []
    for func in prog['functions']:
        bb = basic_block.form_bb(func['instrs'])
        cfg = data.CFG(bb)
        cfgs.append(cfg)

    return cfgs

class Analyzer(ABC):
    """Analyzer is a base class for specific analysis.
    """
    cfgs = []
    # Forward: 0
    # Backward: -1
    start = 0

    def __init__(self, cfgs):
        self.cfgs = cfgs
        self.start = 0

    def init_input(self, od: OrderedDict):
        input = {}
        entry = list(od)[self.start]
        input[entry] = []

        return input

    # to_update is a predecessor or successor map.
    # If 'out' is changed, then the current basic block's pred or succ needs to be updated.
    # Forward: succ
    # Backward: pred
    def analyze_cfg(self, cfg: data.CFG, to_update):
        """A general data flow analysis solver using the worklist algorithm.
        """
        input = self.init_input(cfg.bb)
        out = self.init_out(cfg.bb)

        worklist = list(cfg.bb)
        while worklist:
            b = worklist[self.start]
            input[b] = self.merge(cfg, b, out)
            old = len(out[b])
            out[b] = self.transfer(cfg.bb[b], input[b])

            if old != len(out[b]):
                for bb in to_update[b]:
                    if bb not in worklist:
                        worklist.append(bb)
            else:
                worklist.remove(b)

        return (input, out)

    @abstractmethod
    def analyze(self):
        raise NotImplementedError("analyze() must be implemented")

    @abstractmethod
    def init_out(self, od: OrderedDict):
        raise NotImplementedError("init_out() must be implemented")

    @abstractmethod
    def transfer(self, instrs, input):
        raise NotImplementedError("transfer() must be implemented")

    @abstractmethod
    def merge(self, cfg, curr, out):
        raise NotImplementedError("merge() must be implemented")

class Live(Analyzer):
    """Live variable analysis
    """
    def __init__(self, cfgs):
        self.cfgs = cfgs
        # Backward data flow analysis
        self.start = -1

    def analyze(self):
        for cfg in self.cfgs:
            (input, out) = self.analyze_cfg(cfg, cfg.pred)
            # We need to swap input and out because we're analyzing in backwards.
            print_analysis(out, input)

    def init_out(self, od: OrderedDict):
        out = {}
        for k, instrs in od.items():
            out[k] = set()
            for instr in reversed(instrs):
                # Don't want to remove variable i in the following example
                # i: int = sub i one
                # Thus, we check dest first before adding i
                if 'dest' in instr and instr['dest'] in out[k]:
                    out[k].remove(instr['dest'])

                if 'args' in instr:
                    for arg in instr['args']:
                        out[k].add(arg)

        return out

    def merge(self, cfg: data.CFG, curr_bb, out):
        merged = set()
        for s in cfg.succ[curr_bb]:
            for arg in list(out[s]):
                merged.add(arg)

        return merged

    def transfer(self, instrs, input: set):
        new_out = input.copy()
        for instr in reversed(instrs):
            if 'dest' in instr and instr['dest'] in new_out:
                new_out.remove(instr['dest'])

            if 'args' in instr:
                for arg in instr['args']:
                    new_out.add(arg)

        return new_out

class Defined(Analyzer):
    """Reaching definition analysis
    """
    def __init__(self, cfgs):
        self.cfgs = cfgs
        self.start = 0

    def analyze(self):
        for cfg in self.cfgs:
            (input, out) = self.analyze_cfg(cfg, cfg.succ)
            print_analysis(input, out)

    def init_out(self, od: OrderedDict):
        out = {}
        for k, instrs in od.items():
            out[k] = set()
            for instr in instrs:
                if 'dest' in instr:
                    out[k].add(instr['dest'])

        return out

    def merge(self, cfg: data.CFG, curr_bb, out):
        merged = set()
        for p in cfg.pred[curr_bb]:
            for dest in list(out[p]):
                merged.add(dest)

        return merged

    def transfer(self, instrs, input: set):
        new_out = input.copy()
        for instr in instrs:
            if 'dest' in instr:
                new_out.add(instr['dest'])

        return new_out

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
        defined = Defined(form_cfgs(prog))
        defined.analyze()
        sys.exit(0)
    elif sys.argv[1] == "live":
        live_var = Live(form_cfgs(prog))
        live_var.analyze()
        sys.exit(0)
    else:
        print("Undefined analysis!")
        sys.exit(1)

if __name__ == "__main__":
    main()
