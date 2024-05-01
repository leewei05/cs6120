import json, sys, copy
import dom as dominator
import basic_block
import cfg as data
import re


class Var:
    vars = []
    defs = {}
    var_type = {}

    def __init__(self, bb) -> None:
        (vars, var_type, defs) = self.get_var_def(bb)
        self.vars = vars
        self.defs = defs
        self.var_type = var_type

    def get_var_def(self, bb):
        """Get all variables and variable definition's block

        input: basic_blocks within a function
        output: vars contains all variables, defs[v] is the block where variable is defined
        """

        vars = []
        defs = {}
        var_type = {}
        for block in list(bb):
            for instr in bb[block]:
                # variable definition
                if "dest" in instr:
                    var = instr["dest"]
                    # create empty list if var not exists
                    if var not in defs:
                        defs[var] = []
                    if var not in var_type:
                        var_type[var] = instr["type"]

                    if var not in vars:
                        vars.append(instr["dest"])
                    if block not in defs[var]:
                        defs[var].append(block)

        # check vars, defs
        for var in vars:
            if var not in defs:
                print(f"{var} is not in defs!")
                exit(1)

        return (vars, var_type, defs)


def rename_var(block, bb, succ, stack, stack_num, tree, visited):
    """Rename phi nodes' name.

    stack[v] is a stack of variable names (for every variable v)

    for instr in block:
      replace each argument to instr with stack[old name]

      replace instr's destination with a new name
      push that new name onto stack[old name]

    for s in block's successors:
      for p in s's ϕ-nodes:
        Assuming p is for a variable v, make it read from stack[v].

    for b in blocks immediately dominated by block:
      # That is, children in the dominance tree.
      rename(b)

    pop all the names we just pushed onto the stack
    """
    if block in visited:
        return

    instrs = bb[block]
    push_count = {}
    visited.add(block)

    for instr in instrs:
        if "args" in instr:
            for i, arg in enumerate(instr["args"]):
                if arg not in stack:
                    continue

                if not stack[arg]:
                    continue

                replaced_name = stack[arg][-1]
                instr["args"][i] = replaced_name

        if "dest" in instr:
            var = instr["dest"]
            if var not in stack_num:
                continue

            new_name = var + "." + str(stack_num[var])
            instr["dest"] = new_name

            stack[var].append(new_name)
            stack_num[var] += 1

            # keep track how many new names
            if var not in push_count:
                push_count[var] = 1
            else:
                push_count[var] += 1

    for s in succ[block]:
        added = set()
        for instr in bb[s]:
            if "op" in instr and instr["op"] != "phi":
                continue

            for i, arg in enumerate(instr["args"]):
                if arg not in stack:
                    continue

                if not stack[arg]:
                    continue

                replace = stack[arg][-1]
                if replace not in added:
                    instr["args"][i] = replace
                    added.add(replace)

    children = tree[block]
    for b in sorted(list(children)):
        rename_var(b, bb, succ, stack, stack_num, tree, visited)

    for var, count in push_count.items():
        c = count
        while c > 0:
            stack[var].pop()
            c -= 1


def insert_phi(bb, vobject: Var, dom_front, cfg: data.CFG):
    """Insert phi nodes when there are different definitions for a variable.

    for v in vars:
     for d in Defs[v]:  # Blocks where v is assigned.
       for block in DF[d]:  # Dominance frontier.
         Add a ϕ-node to block,
           unless we have done so already.
         Add block to Defs[v] (because it now writes to v!),
           unless it's already in there.
    """
    vars = vobject.vars
    defs = vobject.defs
    pred = cfg.pred
    # block -> var
    added = {}

    for v in vars:
        for d in defs[v]:
            for block in dom_front[d]:
                prev = [b for b in list(defs[v]) if b in pred[block]]
                args = [v] * len(prev)
                labels = list(prev)
                if block not in added:
                    added[block] = set()

                if v not in added[block]:
                    # insert phi node
                    bb[block].insert(
                        0,
                        {
                            "args": args,
                            "labels": labels,
                            "op": "phi",
                            "type": vobject.var_type[v],
                            "dest": v,
                        },
                    )
                    added[block].add(v)

                if block not in defs[v]:
                    defs[v].append(block)


def form_new_instrs(bb):
    """Form new instrs with phi instructions"""
    final_instrs = []
    for block, instrs in bb.items():
        # print(block)
        final_instrs.append({"label": block})
        final_instrs.extend(instrs)

    return final_instrs


def form_stack_var(vobject: Var):
    # var name -> stacks of var name
    stack = {}
    stack_num = {}

    for var in vobject.vars:
        stack[var] = []
        stack_num[var] = 0

    return stack, stack_num


def to_ssa(func):
    # init
    bb = basic_block.form_bb(func["instrs"])
    cfg = data.CFG(bb)
    dom = dominator.get_dom_v2(cfg)
    dom_front = dominator.get_dom_front_v2(dom, cfg)
    dom_tree = dominator.get_dom_tree_v2(dom, cfg)

    vobject = Var(bb)
    insert_phi(bb, vobject, dom_front, cfg)
    stack, stack_num = form_stack_var(vobject)
    entry = list(bb)[0]
    visited = set()
    rename_var(entry, bb, cfg.succ, stack, stack_num, dom_tree, visited)

    # some basic blocks may not be the succ nor children of entry
    unvisited = [b for b in list(bb) if b not in visited]
    while unvisited:
        rename_var(unvisited[0], bb, cfg.succ, stack, stack_num, dom_tree, visited)
        unvisited = [b for b in list(bb) if b not in visited]

    instrs = form_new_instrs(bb)
    func["instrs"] = instrs


def main():
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        to_ssa(func)
    json.dump(prog, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
