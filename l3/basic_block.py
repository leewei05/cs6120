def create_bb(prog):
    bb = []

    for func in prog['functions']:
        s = 0
        instrs = func['instrs']
        for i, instr in enumerate(instrs):
            if (instr == instrs[-1]) or ('op' in instr and instr['op'] in ["jmp", "ret", "br"]) or 'label' in instr:
                bb.append(instrs[s:i+1])
                s = i + 1

    return bb