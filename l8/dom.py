import sys
import json
import copy
import basic_block
import logging
import resource
import cfg as data
from collections import OrderedDict
from treelib import Node, Tree
from subprocess import check_call


def test_dom_front(dom, front, cfg: data.CFG):
    for b, frontiers in front.items():
        # immediate dominance of b
        idom = cfg.succ[b]
        # check f's predecessor is in idom
        for f in frontiers:
            pred = cfg.pred[f]
            check = False
            for fp in pred:
                if fp in idom:
                    check = True

            if check is False:
                logging.debug(f"{f} is not {b} dominate frontiers")
                exit(1)

    logging.debug(f"Every dominate frontier is correct")


def map_inv(succ):
    """Invert a multimap. (From bril example)

    Given a successor edge map, for example, produce an inverted
    predecessor edge map.
    """
    out = {key: [] for key in succ}
    for p, ss in succ.items():
        for s in ss:
            out[s].append(p)

    return out


def get_dom_front_v2(dom, cfg):
    """From bril example"""
    dom_inv = map_inv(dom)
    succ = cfg.succ
    front = OrderedDict()

    for block in dom:
        # Find all successors of dominated blocks.
        dominated_succ = set()
        for dominated in dom_inv[block]:
            dominated_succ.update(succ[dominated])

        front[block] = [
            b for b in dominated_succ if b not in dom_inv[block] or b == block
        ]

    return front


def get_dom_front(dom, cfg: data.CFG):
    """Find dominate frontiers, which are a set of nodes that are one edge away from domination.

    input: map[block] -> block's dominators
    output: map[block] -> block's dom frontiers

    A's dominance frontier contains B iff A does not strictly dominate B,
    but A does dominate some predecessor of B.
    """
    front = OrderedDict()
    all = list(cfg.bb)

    for A in all:
        # A's immediate dominance
        idom = cfg.succ[A]
        # A cannot be A's dominance frontier
        remain = all.copy()
        remain.remove(A)
        # so does A's direct children and A's dominators
        remain = [x for x in remain if (x in idom and x not in dom[A])]
        front[A] = set()

        # B is immediate dominate by A
        # check B's successor if they are frontiers
        for B in remain:
            succ = cfg.succ[B]
            fs = [x for x in succ if (x not in idom)]
            for f in fs:
                front[A].add(f)

    return front


def draw_dom_tree(tree, file):
    input = file + ".dot"
    tree.to_graphviz(input)
    output = file + ".png"
    check_call(["dot", "-Tpng", input, "-o", output])


def form_tree(root, remain, tree, cfg: data.CFG):
    """Form a tree"""
    if remain is []:
        return

    succ = cfg.succ[root]
    if succ is []:
        return

    for node in succ:
        if tree.contains(node) is False:
            tree.create_node(node, node, parent=root)
            remain.remove(node)
            form_tree(node, remain, tree, cfg)


def form_tree_v2(root, nodes, tree, cfg: data.CFG):
    """Form a tree"""
    if nodes is []:
        return tree

    remain = copy.deepcopy(nodes)
    added = set()

    for node in nodes:
        # immediate dominators of node
        idom = cfg.succ[node]

        common = []
        for n in idom:
            if n not in tree[node] and n not in added:
                tree[node].add(n)
                added.add(n)

            common.append(cfg.succ[n])

        if len(common) < 2:
            continue

        result = set(common[0])
        for c in common[1:]:
            result.intersection_update(c)

        for n in result:
            if n not in tree[node] and n not in added:
                tree[node].add(n)
                added.add(n)


def get_dom_tree_v2(dom, cfg: data.CFG):
    # block -> children
    tree = OrderedDict()
    nodes = list(cfg.bb)
    for node in nodes:
        tree[node] = set()

    root = nodes[0]
    form_tree_v2(root, nodes, tree, cfg)

    return tree


def get_dom_tree(dom, cfg: data.CFG):
    """A dominator tree is a tree where each node's children are those
    nodes it immediately dominates. The start node is the root of the tree.

    input: map[block] -> block's dominators
    output: map[block] -> blocks which it dominates

    find every block's direct parent(idom)
    """
    tree = Tree()
    all = list(cfg.bb)
    root = all[0]

    all.remove(root)
    tree.create_node(root, root)
    form_tree(root, all, tree, cfg)

    return tree


def intersect(sets):
    """From bril example"""
    sets = list(sets)
    if not sets:
        return set()
    out = set(sets[0])
    for s in sets[1:]:
        out &= s
    return out


def get_dom_v2(cfg: data.CFG):
    """From bril example"""
    nodes = list(cfg.bb)
    pred = cfg.pred
    succ = cfg.succ
    dom = {v: set(nodes) for v in succ}

    while True:
        changed = False

        for node in nodes:
            new_dom = intersect(dom[p] for p in pred[node])
            new_dom.add(node)

            if dom[node] != new_dom:
                dom[node] = new_dom
                changed = True

        if not changed:
            break

    return dom


def get_dom(cfg: data.CFG):
    """Find dominators within a function
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
    logging.debug(f"initial dom state: {dom}")
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
            logging.debug(f"current dominators for {v}: {v_all_dom}")
            dom[v] = curr_dom

        if old_dom == dom:
            change = False

    return dom


def is_dominator(dom, block, visited, cfg: data.CFG):
    """Check if dom is the dominator of block

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
        logging.debug(f"found {dom} in {parents}")
        return True
    else:
        for parent in parents:
            logging.debug(f"check {dom} in {parent}s predecessor")
            if parent in visited:
                logging.debug(f"enter infinite loop")
                return True

            visited.add(parent)
            return is_dominator(dom, parent, visited, cfg)


def test_dom(dom, cfg: data.CFG):
    """Test the resulting dominators are correct within a function

    input: map[every block] -> a set of dominators
    """
    logging.debug(f"==========test_dom==========")
    for block, dom in dom.items():
        for d in dom:
            visited = set()
            if is_dominator(d, block, visited, cfg) is False:
                logging.error(f"{d} is not the dominator of {block}")
                exit(1)

        logging.debug(f"every dominator of {block} is correct")


def print_dom(dom):
    logging.debug(f"==========print_dom==========")
    for k, v in dom.items():
        logging.debug(f"{k}: {v}")
        print(f"{k}: {v}")


def main():
    args = sys.argv
    logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        func_name = func["name"]
        logging.debug(f"==========func name: {func_name}=========")
        bb = basic_block.form_bb(func["instrs"])
        cfg = data.CFG(bb)
        if len(args) > 1:
            if args[1] == "dom":
                dom = get_dom_v2(cfg)
                # dom = get_dom(cfg)
                test_dom(dom, cfg)
                print_dom(dom)
            elif args[1] == "tree":
                dom = get_dom(cfg)
                tree = get_dom_tree_v2(dom, cfg)
                for k, v in tree.items():
                    print(f"{k}: {v}")
                # Disable draw
                # draw_dom_tree(tree, func_name)
            elif args[1] == "front":
                dom = get_dom_v2(cfg)
                # front = get_dom_front(dom, cfg)
                front = get_dom_front_v2(dom, cfg)
                # test_dom_front(dom, front, cfg)
                for k, v in front.items():
                    print(f"{k}: {v}")
            else:
                print("unknown arg")
                exit(1)

    # json.dump(prog, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
