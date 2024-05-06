import json, sys
import basic_block
import cfg as data
import dom as dominator
import copy


class NLoop:
    """Natural loop"""

    def __init__(self, cfg: data.CFG, dom) -> None:
        self.cfg = cfg
        self.dom = dom
        # head block is the entry of the natural loop
        # header dominates all blocks in the loop
        self.head = set()
        self.prehead = ""
        self.body = self.form_loop(dom, cfg)
        self.form_prehead(dom, cfg)

    def form_prehead(self, dom, cfg: data.CFG):
        # no natural loop
        if len(self.head) == 0:
            return

        if len(self.head) == 1:
            head = list(self.head)[0]
            pred = [x for x in cfg.pred[head] if x in dom[head]]
            if len(pred) > 1 or len(pred) == 0:
                # create a new prehead
                new_name = "pre" + head
                cfg.succ[new_name] = [head]
                for new_pred in cfg.pred[head]:
                    cfg.succ[new_pred].remove(head)
                    cfg.succ[new_pred].add(new_name)

                cfg.pred[head] = [new_name]
                # empty prehead
                cfg.bb[new_name] = []
            elif len(pred) == 1:
                self.prehead = list(pred)[0]
        else:
            # TODO: multiple head
            pass

    def form_loop(self, dom, cfg: data.CFG):
        """Form natural loop
        1. Find dominators in CFG
        2. Identify back edges
        3. Find natural loops associated with back edges
        """

        # back_edges is the head of the back_edges
        back_edges = set()
        entry = list(cfg.bb)[0]
        visited = set()
        self.dfs(entry, visited, back_edges)
        # Not every graph is connected!
        unvisited = [b for b in list(cfg.bb) if b not in visited]
        while unvisited:
            self.dfs(unvisited[0], visited, back_edges)
            unvisited = [b for b in list(cfg.bb) if b not in visited]

        # every block is visited
        assert visited == set(cfg.bb)

        # body includes every block in a natural loop
        body = set()
        stk = []
        for node in back_edges:
            h = cfg.succ[node]
            self.head |= set(h)

            body |= set(h)
            if node not in stk:
                stk.append(node)

        while stk:
            d = stk.pop(-1)
            if d not in body:
                body |= set({d})
                for pred in cfg.pred[d]:
                    stk.append(pred)

        return body

    def dfs(self, block, visited, back_edges):
        if block in visited:
            return

        visited.add(block)
        # block -> next_block
        succ = self.cfg.succ[block]
        for e in succ:
            # block is the head of a back edge
            if e in self.dom[block]:
                back_edges.add(block)

            self.dfs(e, visited, back_edges)

    def print(self, name):
        print(f"function name: {name}")
        print(f"loop pre-header: {self.prehead}")
        print(f"loop header: {self.head}")
        print(f"loop body: {self.body}")


def licm(loop: NLoop):
    """Loop-Invariant Code Motion"""

    pass


def init(func):
    bb = basic_block.form_bb(func["instrs"])
    cfg = data.CFG(bb)
    dom = dominator.get_dom_v2(cfg)
    # natural loop for optimization
    loop = NLoop(cfg, dom)
    # loop.print(func["name"])
    return loop


def main():
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        loop = init(func)
        licm(loop)
    json.dump(prog, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
