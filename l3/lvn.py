import json
import sys
from collections import OrderedDict

class Optimizer:
    name_num = 0
    local_num = 0
    table = OrderedDict()
    var2num = {}

    def __init__(self):
        self.local_num = 0
        self.table.clear()
        self.var2num.clear()

    def reset(self):
        self.local_num = 0
        self.table.clear()
        self.var2num.clear()

    def new_var(self):
        new_name = "lvn." + str(self.name_num)
        self.name_num += 1
        return new_name

    def get_num(self, s):
        s = s.replace("v", "")
        return int(s)

    # check if var is rewritten afterwards
    def check_var_remaining(self, var, instrs):
        for instr in instrs:
            if 'op' in instr and instr['op'] in ["jmp", "ret", "br"]:
                return False
            if 'label' in instr:
                return False
            if 'args' in instr and var in instr['args']:
                return False
            if 'dest' in instr and instr['dest'] == var:
                return True

        return False

    # map arguments to value number
    def args2valnum(self, args):
        out = []
        for arg in args:
            if arg not in self.var2num:
                out.append(arg)
            else:
                out.append(self.var2num[arg])

        return out

    def is_commutative(self, op):
        match op:
            case "add" | "mul" | "fadd" | "fmul" | "eq" | "and" | "or":
                return True
            case _:
                return False

    def create_tup(self, instr):
        dest = instr.get('dest')
        op = instr.get('op')
        args = instr.get('args')
        tup = ()
        if op is not None:
            match op:
                case "const":
                    val = instr.get('value')
                    tup = (op, val)
                case "add" | "sub" | "mul" | "div" | "fadd" | "fsub" | "fmul" | "fdiv" | "ptradd" | "alloc" | "free" | "store" | "load":
                    out = self.args2valnum(args)
                    if self.is_commutative(op):
                        tup = (op, tuple(sorted(out)))
                    else:
                        tup = (op, tuple(out))
                case "eq" | "le" | "lt" | "gt" | "ge" | "not" | "and" | "or":
                    out = self.args2valnum(args)
                    if self.is_commutative(op):
                        tup = (op, tuple(sorted(out)))
                    else:
                        tup = (op, tuple(out))
                case "id" | "print":
                    out = self.args2valnum(args)
                    tup = (op, tuple(out))
                case "call":
                    out = self.args2valnum(args)
                    out.append(instr["funcs"][0])
                    tup = (op, tuple(out))
        return tup

    def dump(self):
        print("------table---------")
        c = 0
        for k, v in self.table.items():
            print(f'{c}: {k}:{v}')
            c += 1
        print("------var2num-------")
        c = 0
        for k, v in self.var2num.items():
            print(f'{c}: {k}:{v}')
            c += 1
        print("--------------------")

    # TODO: instrs should be a basic block
    def lvn(self, instrs):
        self.reset()
        for i, instr in enumerate(instrs):
            if 'op' in instr and instr['op'] in ["jmp", "ret", "br"]:
                self.reset()
                continue
            # label
            elif 'label' in instr:
                self.reset()
                continue

            tup = self.create_tup(instr)
            dest = instr.get('dest')
            curr_type = instr.get('type')
            # redefinition

            # replace expr
            if tup in self.table and instr['op'] not in ["free", "alloc", "load", "store", "ptrAdd"]:
            #if tup in self.table:
                num, var, type = self.table[tup]
                #instr['dest'] = var
                if type == curr_type:
                    instr['op'] = 'id'
                    instr['args'] = [var]
            else:
                num = self.local_num
                self.local_num += 1
                num = "v" + str(num)
                self.table[tup] = num, dest, curr_type

            #  if instr will be overwritten later:
            if self.check_var_remaining(dest, instrs[i+1:]):
                tmp_dest = self.new_var()
                instr['dest'] = tmp_dest

            if 'args' in instr and instr['op'] not in ["free", "alloc", "load", "store", "ptrAdd", "call"]:
                # TODO: check if both args are constant
                # evaluate lhs op rhs -> c
                # replace instr with dest -> const c
                # store c in table
                new_args = []
                for arg in instr.get('args'):
                    # replace arg with the newest arg
                    if arg in self.var2num:
                        tup = list(self.table.items())[self.get_num(self.var2num[arg])]
                        _, (_, var, type) = tup
                        if instr['op'] not in ["not", "and", "or"]:
                            # instr like add, sub, mul, div
                            # arg type must be int
                            if type == "int":
                                new_args.append(var)
                            else:
                                new_args.append(arg)
                        else:
                            if type == "bool":
                                new_args.append(var)
                            else:
                                new_args.append(arg)
                    else:
                        new_args.append(arg)

                instr['args'] = new_args

            if dest is not None:
                self.var2num[dest] = num

        #self.dump()

if __name__ == '__main__':
    opt = Optimizer()
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        opt.lvn(func['instrs'])
    json.dump(prog, sys.stdout, indent=2)
