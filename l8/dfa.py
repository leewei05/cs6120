import sys
import json
import basic_block
import cfg as data
from collections import OrderedDict
from abc import ABC, abstractmethod


class Defined:
    # Forward: 0
    # Backward: -1

    def __init__(self, cfg):
        self.cfg = cfg
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
        """A general data flow analysis solver using the worklist algorithm."""
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

    def analyze(self):
        (input, out) = self.analyze_cfg(self.cfg, self.cfg.succ)
        # print_analysis(input, out)
        return (input, out)

    def init_out(self, od: OrderedDict):
        out = {}
        for k, instrs in od.items():
            out[k] = set()
            for instr in instrs:
                if "dest" in instr:
                    out[k].add(instr["dest"])

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
            if "dest" in instr:
                new_out.add(instr["dest"])

        return new_out


def print_analysis(input, out):
    if len(input) != len(out):
        print("Unmatched data!")
        exit(1)

    for _, k in enumerate(input):
        print(f"{k}:")
        print(f"  in: ", fmt(input[k]))
        print(f"  out:", fmt(out[k]))


def fmt(val):
    if isinstance(val, set):
        if val:
            return ", ".join(sorted(val))
        else:
            return "∅"


def main():
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        bb = basic_block.form_bb(func["instrs"])
        cfg = data.CFG(bb)
        defined = Defined(cfg)
        defined.analyze()


if __name__ == "__main__":
    main()
