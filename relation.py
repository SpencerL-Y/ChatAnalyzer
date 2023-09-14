import os, sys

class relation_graph():
    def __init__(self, size, syscall_names) -> None:
        self.influence = {}
        self.influence_by = {}
        
        for syscall in syscall_names:
            self.influence[syscall] = []
            self.influence_by[syscall] = []

    def add_influence(self, syscall_name_from, syscall_name_to, weight):
        influence_found = False
        influence_by_found = False
        for to_weight_pair in self.influence[syscall_name_from]:
            if to_weight_pair.to == syscall_name_to:
                influence_found = True
                to_weight_pair.weight = weight
                break
        if not influence_found:
            self.influence[syscall_name_from].append({"to": syscall_name_to, "weight": weight})
        for from_weight_pair in self.influence_by:
            if from_weight_pair.frrom == syscall_name_from:
                influence_by_found = True
                from_weight_pair.weight = weight
                break
        if not influence_by_found:
            self.influence_by[syscall_name_to].append({"frro": syscall_name_from, "weight": weight})
    
    def print_graph(self):
        for item in self.influence.keys():
            print("syscall: " + item)
            print("influence: ")
            output_str = ""
            for record in self.influence[item]:
                output_str += "(" + record.to + ", " + str(record.weight) + ")"
            print(output_str)
    
            