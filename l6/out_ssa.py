import json, sys, re


def out_ssa(func):
    new_instrs = []
    for instr in func["instrs"]:
        # skip label
        if "label" in instr:
            new_instrs.append(instr)
            continue

        if "dest" in instr:
            s = instr["dest"].split(".")
            instr["dest"] = s[0]

        if "args" in instr:
            for i, arg in enumerate(instr["args"]):
                s = arg.split(".")
                instr["args"][i] = s[0]

        # print(f"new: {func["instrs"][j]}")

        # remove single arg phi
        if "op" in instr and instr["op"] == "phi":
            if len(instr["args"]) < 2:
                continue
            # args all the same
            elif len(set(instr["args"])) == 1:
                continue
            else:
                new_instrs.append(instr)
        else:
            new_instrs.append(instr)

    # print(new_instrs)
    func["instrs"].clear()
    func["instrs"] = new_instrs


def main():
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        out_ssa(func)
    json.dump(prog, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
