from utils.import_list import *
import itertools

class Algorithm:
    
    
    def __init__(self, circuit, simulator, parent_num):
        self.qc_list = list()
        self.energy_distribution = list()
        self.simulator = simulator
        self.initial_circuit = circuit
        self.current_circuit = self.initial_circuit.circuit
        self.energy_initial = self.simulator.accept(self.current_circuit)
        self.number_operators = len(self.current_circuit.data)
        self.iteration = 0
        self.acceptance = 0
        self.name = "attempt_" + str(Algorithm.number)
        self.parent_num = parent_num
        Algorithm.number += 1
        
    def smallrot(mat, dt):
        n = mat.shape[0]
        z = mat + (np.random.normal(size=(n,n), scale=dt)
                    + 1j*np.random.normal(size=(n,n), scale=dt))/np.sqrt(2)
        q,r = np.linalg.qr(z)
        d = np.diag(r)
        ph = d/np.abs(d)
        q = np.multiply(q,ph,q)
        return q

    def save_circuit(self):
      file_name = open("circuit_configs" + str(self.parent_num) + "/" + self.name + "/qc_" + str(self.iteration) + ".qc", "wb")
      pickle.dump(self.current_circuit, file_name)

    def forward_feed(self, iterations, beta_initial, deviation_initial, change):
        
        while self.iteration <= iterations:
            if self.iteration % change == 0:
                self.qc_list.append(self.current_circuit)
                self.save_circuit()
                self.alpha = np.random.choice(list(np.arange(0.80, 0.99, 0.01)))
                self.beta = beta_initial * (1 + (self.alpha * int(self.iteration/change)))
                self.deviation = deviation_initial / (int(self.iteration/change) + 1)
                print("Iterations")
                print(self.iteration)
                print("Accepted")
                print(self.acceptance)
                if self.iteration != 0:
                    print("Acceptance rate")
                    print(float(self.acceptance) / float(self.iteration))
                print("Deviation")
                print(self.deviation)
                print("Beta")
                print(self.beta)
                print("Lowest Energy")
                print(self.energy_initial)

            index = self.iteration % self.initial_circuit.circuit_depth - 1
            circuit_propose = self.current_circuit.copy()
            size_random_operator = circuit_propose.data[index][0].num_qubits
            circuit_name = circuit_propose.data[index][0].name
            if circuit_name == "state_preparation" or circuit_name == "reset" or circuit_name == "barrier":
                continue
            operator_proposed = ext.UnitaryGate(Algorithm.smallrot(circuit_propose.data[index][0].to_matrix(), self.deviation))
            circuit_propose.data[index] = [operator_proposed, circuit_propose.data[index][1], circuit_propose.data[index][2]]
            randomized_circuit = self.randomize_circuit(circuit_propose)
            energy_propose = self.simulator.accept(circuit_propose)
            energy_diff = energy_propose - self.energy_initial
            prob = np.exp(-1 * self.beta * energy_diff)
            prob_accept = min(1, prob)
            if prob_accept > np.random.random():
                self.current_circuit = circuit_propose
                self.energy_initial = energy_propose
                self.energy_distribution.append(energy_propose)
                self.iteration += 1
                self.acceptance += 1
            else:
                self.iteration += 1

    


    def plot(self):
        plt.plot(range(len(self.energy_distribution)), self.energy_distribution)


