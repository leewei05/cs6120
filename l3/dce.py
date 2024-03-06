import json
import sys

class Optimizer:
    # used across the entire function
    used = {} # var -> instr, blk_num
    block_num = 0

    def __init__(self) -> None:
        pass

    def curr_block_num(self):
        blk_num = self.block_num
        self.block_num += 1
        return blk_num

    def not_used_between(self, var, newest_instr, instrs):
        not_used = True
        for instr in instrs:
            if instr == newest_instr:
                break

            if 'args' in instr and var in instr['args']:
                not_used = False

        return not_used

    # dead code elimination with in a basic block
    def dce_bb(self, instrs, blk_num):
        last_def = {} # var, block_num -> instr
        for instr in instrs:
            if 'dest' in instr:
                last_def[(instr['dest'], blk_num)] = instr

        for i, instr in enumerate(instrs):
            if 'dest' in instr:
                # check instr that are not used
                if instr['dest'] not in self.used:
                    instrs.remove(instr)

                # check if this assign is the newest
                # bril function call need one additional copy
                newest_def = last_def[instr['dest'], blk_num]
                if ('op' in instr and instr['op'] != "call") and newest_def != instr:
                    # sum: int = add sum i;
                    # sum: int = add sum qut;
                    if 'args' in newest_def and instr['dest'] not in newest_def['args'] and self.not_used_between(instr['dest'], newest_def, instrs[i+1:]):
                        instrs.remove(instr)
                    if 'args' not in newest_def:
                        instrs.remove(instr)

        return instrs

    def scan_used(self, instrs):
        for instr in instrs:
            # save used args in op
            if 'args' in instr:
                for arg in instr['args']:
                    self.used[arg] = instr

    def rescan_used(self, instrs):
        self.used.clear()
        self.scan_used(instrs)

    def dce(self, instrs):
        s = 0
        self.scan_used(instrs)
        for i, instr in enumerate(instrs):
            if (instr == instrs[-1]) or ('op' in instr and instr['op'] in ["jmp", "br", "ret"]):
                # optimize instrs until no changes
                old_len = len(instrs[s:i+1])
                new_len = 0
                blk_num = self.curr_block_num()
                while old_len != new_len:
                    self.rescan_used(instrs)
                    old_len = len(instrs[s:i+1])
                    opt_instrs = self.dce_bb(instrs[s:i+1], blk_num)
                    new_len = len(opt_instrs)
                    instrs[s:i+1] = opt_instrs

                s = i + 1

if __name__ == '__main__':
    prog = json.load(sys.stdin)
    # optimize within one function
    for func in prog['functions']:
        opt = Optimizer()
        instrs = func['instrs']
        opt.dce(instrs)

    json.dump(prog, sys.stdout, indent=2)
