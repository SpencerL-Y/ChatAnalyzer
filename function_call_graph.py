import os, sys


class Func_call_graph():
    def __init__(self, syscall_bodies) -> None:
        self.func_nodes = set()
        for syscall in syscall_bodies:
            self.func_nodes.add(syscall)
        self.call_edges = {}

    def add_func_node(self, func_body):
        self.func_nodes.add(func_body)
        self.call_edges[func_body] = []

    def add_func_call_edge(self, from_func, to_func):
        if not from_func in self.func_nodes:
            self.func_nodes.add(from_func)
        if not to_func in self.func_nodes:
            self.func_nodes.add(to_func)
        self.call_edges[from_func].append(to_func)

    def get_roots(self):
        candidates_roots = self.func_nodes.copy()
        for i, j in enumerate(self.call_edges.values):
            for to_node in j:
                candidates_roots.remove(to_node)
        return candidates_roots
    
    def get_funcs_called_by_node(self, func_body):
        if not func_body in self.func_nodes:
            
        
if __name__ == "__main__":
