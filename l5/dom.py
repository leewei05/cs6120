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

def get_dom(cfg: data.CFG):
    """ Find dominators within a function

        input: cfg of a function
        output: map[every block] -> block's dominators

        dom = {every block -> set of all blocks}
        dom[entry] = {entry}
        while dom is still changing:
            for vertex in CFG except entry:
                dom[vertex] = {vertex} union ⋂(dom[p] for p in vertex.preds}
    """
    dom = {}
    # map every block to a set of all blocks
    all = list(cfg.bb)
    for b in all:
        dom[b] = set(all)

    # entry block
    entry = all[0]
    vertices = all
    vertices.remove(entry)

    # self's dominators include itself
    change = True
    dom[entry] = {entry}
    # converge until dom doesn't change
    while change and len(vertices) != 0:
        for v in vertices:
            curr_dom = dom[v]
            # add v as its own dominator
            curr_dom.add(v)

            # v's first predecessor
            first_pred = list(cfg.pred[v])[0]
            # first predecessor's dominators
            first_dom = set(dom[first_pred])

            # sets of every predecessor's dominators
            sets = []
            for p in cfg.pred[v]:
                pred_dom = set(dom[p])
                sets.append(pred_dom)

            # use this sets to intersect to get common dominators
            first_dom.intersection(*sets)
            # {v} union with its dominators
            curr_dom.union(first_dom)
            old_dom = dom[v]
            if old_dom == curr_dom:
                change = False

            dom[v] = curr_dom

    return dom

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
        print(f'func name: {func['name']}')
        bb = basic_block.form_bb(func['instrs'])
        cfg = data.CFG(bb)
        dom = get_dom(cfg)
        for k, v in dom.items():
            print(f'{k}: {v}')

if __name__ == "__main__":
    main()