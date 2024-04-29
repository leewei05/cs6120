import json, sys, copy
import dom as dominator
import basic_block
import cfg as data
import re


def insert_phi(bb, vars, var_type, defs, dom_front):
    """Insert phi nodes when there are different definitions for a variable.

    for v in vars:
     for d in Defs[v]:  # Blocks where v is assigned.
       for block in DF[d]:  # Dominance frontier.
         Add a ϕ-node to block,
           unless we have done so already.
         Add block to Defs[v] (because it now writes to v!),
           unless it's already in there.
    """
    # block -> var
    added = {}

    for v in vars:
        # print(f"var: {v}")
        for d in defs[v]:
            # print(f"{v} block: {d}")
            for block in dom_front[d]:
                # print(f"block: {block}")
                # form phi node
                args = [v] * len(list(defs[v]))
                labels = list(defs[v])
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
                            "type": var_type[v],
                            "dest": v,
                        },
                    )
                    added[block].add(v)

                if block not in defs[v]:
                    defs[v].append(block)


def get_var_def(bb):
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


def form_new_instrs(bb):
    """Form new instrs with phi instructions"""
    final_instrs = []
    for block, instrs in bb.items():
        x = re.search("^b[0-9]+$", block)
        # basic block without label starting
        if x is not None:
            final_instrs.extend(instrs)
        else:
            # insert label
            final_instrs.append({"label": block})
            final_instrs.extend(instrs)

    return final_instrs


def to_ssa(func):
    # init
    bb = basic_block.form_bb(func["instrs"])
    cfg = data.CFG(bb)
    dom = dominator.get_dom(cfg)
    dom_front = dominator.get_dom_front(dom, cfg)

    (vars, var_type, defs) = get_var_def(bb)
    insert_phi(bb, vars, var_type, defs, dom_front)
    instrs = form_new_instrs(bb)

    func["instrs"] = instrs


def main():
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        to_ssa(func)
    json.dump(prog, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
