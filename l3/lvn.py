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

  # check if var is rewritten afterwards
  def check_var_remaining(self, var, instrs):
    for instr in instrs:
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
        case "add" | "sub" | "mul" | "div" | "fadd" | "fsub" | "fmul" | "fdiv" | "print":
          out = self.args2valnum(args)
          # TODO: check commutative operations
          tup = (op, tuple(out))
     #else:
      # label
    return tup

  def dump(self):
    print("--------------------")
    c = 0
    for k, v in self.table.items():
      print(f'{c}: {k}:{v}')
      c += 1
    print("--------------------")
    c = 0
    for k, v in self.var2num.items():
      print(f'{c}: {k}:{v}')
      c += 1
    print("--------------------")

  # TODO: instrs should be a basic block
  def lvn(self, instrs):
    for i, instr in enumerate(instrs):
      # reset current state for new basic block
      if 'op' in instr and instr['op'] in ["jmp", "ret", "br"]:
        self.reset()
        continue
      # label
      elif 'label' in instr:
        continue

      tup = self.create_tup(instr)
      dest = instr.get('dest')
      # redefinition

      # replace expr
      if tup in self.table:
        # TODO: constant folding
        num, var = self.table[tup]
        #instr['dest'] = var
        instr['op'] = 'id'
        instr['args'] = [var]
      else:
        num = self.local_num
        self.local_num += 1
        self.table[tup] = num, dest

      #  if instr will be overwritten later:
      if self.check_var_remaining(dest, instrs[i+1:]):
          tmp_dest = self.new_var()
          #dest = fresh variable name
          instr['dest'] = tmp_dest

      if 'args' in instr:
        # TODO: check if both args are constant
        # evaluate lhs op rhs -> c
        # replace instr with dest -> const c
        # store c in table
        new_args = []
        for arg in instr.get('args'):
          # replace arg with the newest arg
          if arg in self.var2num:
            tup = list(self.table.items())[self.var2num[arg]]
            _, (_, var) = tup
            new_args.append(var)
          else:
            new_args.append(arg)
        # TODO: check algebraic identities

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
