import sys
import json

def count():
    num_op = {}
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        for instr in func['instrs']:
            if 'op' in instr:
                key = instr['op']
                if key not in num_op:
                    num_op[key] = 1
                else:
                    num_op[key] += 1

    for k, i in num_op.items():
        print(f'{k}: {i}')

if __name__ == '__main__':
    count()
