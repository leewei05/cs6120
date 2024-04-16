import sys
import json
import basic_block
import cfg as data

class DOM():
    """ DOM is a class for dominators.
    """
    dom = {}

    def __init__(self):
        pass

def test_dom_front():
    pass

def get_dom_front():
    """ Find dominate frontiers, which are a set of nodes that are one edge away from domination.

        input: map[block] -> block's dominators
        output: map[block] -> block's dom frontiers
    """

def print_dom_tree():
    # use treelib to print trees
    pass

def get_dom_tree():
    """ A dominator tree is a tree where each node's children are those
        nodes it immediately dominates. The start node is the root of the tree.

        input: map[block] -> block's dominators
        output: map[block] -> blocks which it dominates

        find every block's direct parent(idom)
    """
    pass

def get_dom():
    """ Find dominators within a function

        input: cfg of a function
        output: map[every block] -> block's dominators

        dom = {every block -> all blocks}
        dom[entry] = {entry}
        while dom is still changing:
            for vertex in CFG except entry:
                dom[vertex] = {vertex} union ⋂(dom[p] for p in vertex.preds}
    """
    pass

def test_dom():
    """ Test the resulting dominators are correct within a function

        input: map[every block] -> a set of dominators

        for b in map:
            dom = map[block]

            for d in dom:
                # check if d dominates b using DFS
                if is_dominator(d, b):
                    print(d dominates b)
                else:
                    print(err)
                    exit(1)
    """

def main():
    prog = json.load(sys.stdin)
    for func in prog['functions']:
        func['name']
        bb = basic_block.form_bb(func['instrs'])
        cfg = data.CFG(bb)

    json.dump(prog, sys.stdout, indent=2)

if __name__ == "__main__":
    main()