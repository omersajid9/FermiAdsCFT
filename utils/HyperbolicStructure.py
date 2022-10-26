from utils.import_list import *

class HyperbolicStructure:
    num_triangles = 7
    depth = 14

    def __init__(self, num_layers): # num of layers = 1
        self.num_layers = num_layers
        self.num_qubits = HyperbolicStructure.SumQubitsAllLayer(num_layers)
        self.InitializeHyperbolic()
        self.boundary_layer = num_layers
        self.boundary_qubits = HyperbolicStructure.QubitsInLayer(self.boundary_layer)

    def NumQubitsPerLayer(layer):
        if layer < 0:
            return 0
        elif layer == 0:
            return 1
        elif layer == 1:
            return HyperbolicStructure.num_triangles
        elif layer == 2:
            return (HyperbolicStructure.num_triangles - 4) * HyperbolicStructure.NumQubitsPerLayer(layer - 1)
        else:
            return (HyperbolicStructure.num_triangles - 4) * HyperbolicStructure.NumQubitsPerLayer(layer - 1) - HyperbolicStructure.NumQubitsPerLayer(layer - 2)

    def SumQubitsAllLayer(num_layers):
        return sum([HyperbolicStructure.NumQubitsPerLayer(i) for i in range(num_layers + 1)])

    def QubitsInLayer(layer):
        return range(HyperbolicStructure.SumQubitsAllLayer(layer - 1), HyperbolicStructure.SumQubitsAllLayer(layer))

    def IntoFlat(pair_list):
        pair_list_flat = list()
        for layers in pair_list:
            for pairs in layers:
                pair_list_flat.append(pairs)
        len(pair_list_flat)
        return pair_list_flat

        # return list(np.array(pair_list).reshape(len(pair_list) * len(pair_list[0])))

    def DefineInteractionSite(remaining_connections_list, nex_qubits):
        nex_qubits_copy = copy.deepcopy(list(nex_qubits))
        nex_qubits_copy.append(nex_qubits_copy[0]) ## adding the first element to the end to give a circular characterstic
        interaction_sites_list = list()
        overlap_size = 1
        index = 0
        for qubit in remaining_connections_list:
            interaction_sites_list.append(nex_qubits_copy[index:index + qubit])
            index += qubit - overlap_size
        return interaction_sites_list

    def SearchAdjacentQubits(pair_list, qubit):
        adjacent_list = list()
        pair_list_flat = HyperbolicStructure.IntoFlat(pair_list)
        for pair in pair_list_flat:
            if pair[0] == qubit:
                adjacent_list.append(pair[1])
            elif pair[1] == qubit:
                adjacent_list.append(pair[0])
        return adjacent_list

    def InitializeHyperbolic(self):
        self.inter_pair_list = list()
        self.intra_pair_list = list()
        self.qubit_list = range(HyperbolicStructure.SumQubitsAllLayer(self.num_layers))

        for count, current_layer in enumerate(range(self.num_layers)):
            inter_pair_list_per_layer = list()
            intra_pair_list_per_layer = list()

            prev = HyperbolicStructure.NumQubitsPerLayer(current_layer - 1)
            cur = HyperbolicStructure.NumQubitsPerLayer(current_layer)
            nex = HyperbolicStructure.NumQubitsPerLayer(current_layer + 1)

            cur_qubits = range(prev, prev + cur)
            nex_qubits = range(prev + cur, prev + cur + nex)

            #scanning current layer for previous adjacencies
            remaining_connections_list = list()
            for qubit in cur_qubits:
                adjacent_list = HyperbolicStructure.SearchAdjacentQubits(self.inter_pair_list + self.intra_pair_list, qubit)
                num_connections_remaining = self.num_triangles - len(adjacent_list)
                remaining_connections_list.append(num_connections_remaining)

            interaction_sites = HyperbolicStructure.DefineInteractionSite(remaining_connections_list, nex_qubits)

            #adding connectections the next layer a layer
            for cur_index, cur_qubit in enumerate(cur_qubits):
                for nex_qubit in interaction_sites[cur_index]:
                    inter_layer_pair = (cur_qubit, nex_qubit)
                    inter_pair_list_per_layer.append(inter_layer_pair)
            self.inter_pair_list.append(inter_pair_list_per_layer)

            for nex_index, nex_qubit in enumerate(nex_qubits):
                if nex_qubits[nex_index - 1] != nex_qubits[nex_index]:
                    intra_layer_pair = (nex_qubits[nex_index], nex_qubits[nex_index - 1])
                    intra_pair_list_per_layer.append(intra_layer_pair)
            self.intra_pair_list.append(intra_pair_list_per_layer)
