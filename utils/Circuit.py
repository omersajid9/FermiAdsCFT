from utils.import_list import *
from utils.HyperbolicStructure import HyperbolicStructure

class Circuit:

    def __init__(self, num_layers):
        self.hyperbolic_structure = HyperbolicStructure(num_layers)
        self.num_qubits = self.hyperbolic_structure.num_qubits
        self.pair_list = [self.hyperbolic_structure.inter_pair_list, self.hyperbolic_structure.intra_pair_list]
        self.circuit = QuantumCircuit(self.num_qubits)
        for cur_depth in range(self.hyperbolic_structure.depth):
            self.DefineAnsantz(cur_depth)
        self.circuit_depth = len(self.circuit.data)

    def draw(self):
        self.circuit.draw()

    def DefineAnsantz(self, depth):
        seed = 10
        if depth == 0:
            all_qubits = self.hyperbolic_structure.num_qubits
            single_qubit_gate_size = 2 ** 1
            for single_operator_index in range(all_qubits):
                unitary_random_single = qInfo.random_unitary(single_qubit_gate_size, seed)
                self.circuit.append(unitary_random_single, [single_operator_index])

        if depth % 2 == 1:
            (inter_gates, intra_gates) = copy.deepcopy(self.pair_list)
            double_qubit_gate_size = 2 ** 2
            for cur_layer in range(self.hyperbolic_structure.num_layers):
                num_operator_as_per_depth = (int(depth/2)) % self.hyperbolic_structure.num_triangles # systematically, deterministically putting in gates
                current_qubits = HyperbolicStructure.QubitsInLayer(cur_layer)
                num_intra_layers_gates = len(list(intra_gates[cur_layer]))
                num_intra_layers_gates_per_depth = int(num_intra_layers_gates / self.hyperbolic_structure.num_triangles)
                num_inter_layers_gates = len(list(inter_gates[cur_layer]))
                num_inter_layers_gates_per_depth = int(num_inter_layers_gates / self.hyperbolic_structure.num_triangles)


                for intra_gate in range(num_intra_layers_gates_per_depth):
                    unitary_random_double = qInfo.random_unitary(double_qubit_gate_size, seed)
                    index_a = num_operator_as_per_depth + intra_gate * self.hyperbolic_structure.num_triangles
                    self.circuit.append(unitary_random_double, list(intra_gates[cur_layer][index_a]))
                index_diff = 2 # so that no one qubit has two gates acting on it in a single layer
                for inter_gate in range(num_inter_layers_gates_per_depth):
                    unitary_random_double = qInfo.random_unitary(double_qubit_gate_size, seed)
                    index_b = num_operator_as_per_depth + inter_gate * self.hyperbolic_structure.num_triangles
                    self.circuit.append(unitary_random_double, list(inter_gates[cur_layer][index_b - index_diff]))
