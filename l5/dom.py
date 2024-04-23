import sys
import json
import basic_block
import logging
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
        Def: A dominates B iff: all paths from the entry to B include A

        input: cfg of a function
        output: map[every block] -> block's dominators
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

    change = True
    # self's dominators include itself
    old_dom = dom.copy()
    dom[entry] = {entry}
    logging.debug(f'initial dom state: {dom}')
    # converge until dom doesn't change
    while change and len(vertices) != 0:
        old_dom = dom.copy()
        for v in vertices:
            # add v as its own dominator
            curr_dom = set()
            curr_dom.add(v)

            # v's first predecessor
            if cfg.pred[v] == []:
                continue

            first_pred = list(cfg.pred[v])[0]
            # first predecessor's dominators
            v_all_dom = set(dom[first_pred])

            # sets of every predecessor's dominators
            sets = []
            for p in cfg.pred[v]:
                pred_dom = set(dom[p])
                sets.append(pred_dom)

            # use this sets to intersect to get common dominators
            v_all_dom.intersection(*sets)
            # {v} union with its dominators
            curr_dom = curr_dom.union(v_all_dom)
            logging.debug(f'current dominators for {v}: {v_all_dom}')
            dom[v] = curr_dom

        if old_dom == dom:
            change = False

    return dom

def is_dominator(dom, block, cfg: data.CFG):
    """ Check if dom is the dominator of block

        1. dom == block, return True
        2. dom is the direct parent of block, return True
        3. dom is the grandparents of block, return True

        check until parents is empty, it means that dom is not the dominator of block
    """
    if dom == block:
        return True

    parents = cfg.pred[block]
    if parents is []:
        return False

    if dom in parents:
        logging.debug(f'found {dom} in {parents}')
        return True
    else:
        for parent in parents:
            logging.debug(f'check {dom} in {parent}s predecessor')
            return is_dominator(dom, parent, cfg)

def test_dom(dom, cfg: data.CFG):
    """ Test the resulting dominators are correct within a function

        input: map[every block] -> a set of dominators
    """
    logging.debug(f'==========test_dom==========')
    for block, dom in dom.items():
        for d in dom:
            if is_dominator(d, block, cfg) is False:
                logging.error(f'{d} is not the dominator of {block}')
                exit(1)

        logging.debug(f'Every dominator of {block} is correct')

def print_dom(dom):
    logging.debug(f'==========print_dom==========')
    for k, v in dom.items():
        logging.debug(f'{k}: {v}')

def main():
    args = sys.argv
    if (len(args) < 2):
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    elif args[1] == "debug":
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    prog = json.load(sys.stdin)
    for func in prog['functions']:
        logging.debug(f'==========func name: {func['name']}=========')
        bb = basic_block.form_bb(func['instrs'])
        cfg = data.CFG(bb)
        dom = get_dom(cfg)
        if len(args) > 1 and args[1] == "test":
            test_dom(dom, cfg)

    json.dump(prog, sys.stdout, indent=2)

if __name__ == "__main__":
    main()