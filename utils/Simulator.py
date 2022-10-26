from typing import Sized
from utils.import_list import *

class Simulator:
    number = 0
    pauli_list = ["X", "Z", "Y", "I"]
    
    pauli_double = list()

    for comb in itertools.product(pauli_list, repeat=2):
        a = Operator(Pauli(comb[0])).expand(Operator(Pauli(comb[1])))
        b = Operator(a.compose(Operator(CXGate())))
        for com in itertools.product(pauli_list, repeat=2):
            c = Operator(Pauli(com[0])).expand(Operator(Pauli(com[1])))
            d = Operator(b.compose(c))
            if process_fidelity(d, Operator(CXGate())) == 1:
                pauli_double.append([[comb[0], comb[1]], [com[0], com[1]]])
                continue
    def __init__(self, hyperbolic_structure,  typee="sim", name="automatic", noise=False, noise_model="ibmq_lima", shots=20000):
        self.provider = IBMQ.load_account()
        # self.prov = IBMQ.save_account("0ea99e7d8d139cef33eac1bd2308f07feb01109b30856ef05f5c7b5fe2176fc4c20263c7fb90ed4aef345e43e895414fa5b4eb7c81a6978cf5b97212846e419c")
        # self.provider = IBMQ.save_account("0ea99e7d8d139cef33eac1bd2308f07feb01109b30856ef05f5c7b5fe2176fc4c20263c7fb90ed4aef345e43e895414fa5b4eb7c81a6978cf5b97212846e419c")
        self.shots = shots
        self.hyperbolic_structure = hyperbolic_structure
        
        if noise:
            backend_error = self.provider.get_backend(noise_model)
            noise_model = NoiseModel.from_backend(backend_error)
            
            if typee == "sim":
                self.machine = AerSimulator(method = name, noise_model = noise_model)
            else:
                self.machine = self.provider.get_backend(name, noise_model = noise_model)
        else:
            if typee == "sim":
                self.machine = AerSimulator(method = name)
            else:
                self.machine = self.provider.get_backend(name)

    def accept(self, circuit_quantum):
        self.circuit_quantum = circuit_quantum.copy()
        # self.circuit_quantum = self.randomize_circuit(self.circuit_quantum)
        self.size = len(list(self.hyperbolic_structure.boundary_qubits))
        cr = ClassicalRegister(self.size)
        self.circuit_quantum.add_register(cr)
        average_x = self.HermitianX()
        average_zz = self.HermitianZZ()
        return - average_x - average_zz

    def error_correction(self, circuit_quantum, M=2, shots=20000):
        cirx_list = list()
        cirzz_list = list()
        shots = shots/M
        size = circuit_quantum.num_qubits

        circuit_measure_zz = QuantumCircuit(circuit_quantum.num_qubits, len(self.hyperbolic_structure.boundary_qubits))
        circuit_measure_zz.measure(list(self.hyperbolic_structure.boundary_qubits), list(range(size - 1)))
        circuit_measure_x = QuantumCircuit(circuit_quantum.num_qubits, len(self.hyperbolic_structure.boundary_qubits))
        for i in range(circuit_measure_x.num_qubits):
            circuit_measure_x.h(i)
        circuit_measure_x.measure(list(self.hyperbolic_structure.boundary_qubits), list(range(size - 1)))
        

        
        # print("Start")
        for i in range(M):
            circuit = circuit_quantum.copy()
            # print("before")
            # print(transpile(circuit, basis_gates=["cx", "rx", "rz", "id", "barrier"]).count_ops())
            circ = qiskit.transpiler.passes.RemoveBarriers()(self.randomize_circuit(circuit))
            circ.add_register(ClassicalRegister(size - 1))
            # print("after")
            # print(transpile(circ, basis_gates=["cx", "rx", "rz", "id", "barrier"], optimization_level=3).count_ops())
            circ_x = transpile(circ.copy().compose(circuit_measure_x))
            circ_zz = transpile(circ.copy().compose(circuit_measure_zz))
            cirx_list.append(circ_x)
            cirzz_list.append(circ_zz)
        # start = time.time()
        result_x = execute(cirx_list, self.machine, shots = shots).result().get_counts()
        result_zz = execute(cirzz_list, self.machine, shots = shots).result().get_counts()
        # print("Time to execute")
        # print(time.time() - start)
        count_x = np.array([Simulator.MeasureX(resultx) for resultx in result_x])
        count_zz = np.array([Simulator.MeasureZZ(resultzz) for resultzz in result_zz])
        average = - np.mean(count_x) - np.mean(count_zz)
        # average = - count_x - count_zz
        # average = np.mean(average)
        return average

    def multiple_circuits(self, circuit_list):
        pass
            

    def MeasureZZ(counts_zz):
        int2D = 1 - np.array(list(map(list, list(counts_zz.keys()))), dtype=int) * 2
        temp = np.roll(int2D, 1, 1)
        val = np.einsum('ij, ij->i', int2D, temp) # einsum('i, i', int2D, temp)
        freq = np.array(list(counts_zz.values()))
        energy_average_z = val.T.dot(freq)/sum(freq)
        return energy_average_z
        

    def HermitianZZ(self):
        circuit_zz = self.circuit_quantum.copy()
        circuit_measure_zz = QuantumCircuit(circuit_zz.num_qubits, len(self.hyperbolic_structure.boundary_qubits))
        circuit_measure_zz.measure(list(self.hyperbolic_structure.boundary_qubits), list(range(self.size)))
        circuit_transpile_zz = transpile(circuit_zz.compose(circuit_measure_zz), self.machine)
        results_zz = self.machine.run(circuit_transpile_zz, shots=self.shots).result()
        counts_zz = results_zz.get_counts()
        average_zz = Simulator.MeasureZZ(counts_zz)
        return average_zz


    def MeasureX(counts_x):
        int2D = 1 - np.array(list(map(list, list(counts_x.keys()))), dtype=int) * 2
        val = np.einsum('ij->i', int2D)
        freq = np.array(list(counts_x.values()))
        energy_average_x = val.T.dot(freq)/sum(freq)
        return energy_average_x

    def HermitianX(self):
        circuit_x = self.circuit_quantum.copy()
        circuit_measure_x = QuantumCircuit(circuit_x.num_qubits, len(self.hyperbolic_structure.boundary_qubits))
        for i in range(circuit_measure_x.num_qubits):
            circuit_measure_x.h(i)
        circuit_measure_x.measure(list(self.hyperbolic_structure.boundary_qubits), list(range(self.size)))
        circuit_transpile_x = transpile(circuit_x.compose(circuit_measure_x), self.machine)
        results_x = self.machine.run(circuit_transpile_x, shots=self.shots).result()
        counts_x = results_x.get_counts()
        average_x = Simulator.MeasureX(counts_x)
        return average_x

    def correspondance_with_error (self, circuit_quantum, M=2, shots=20000):
        self.M = M
        self.shots = shots
        circuit = circuit_quantum.copy()
        size = circuit_quantum.num_qubits

        circuit_measure_zz = QuantumCircuit(circuit_quantum.num_qubits, size-1)
        circuit_measure_zz.measure(list(self.hyperbolic_structure.boundary_qubits), list(range(size - 1)))
        corr_zz = list()
        for i in range(M):
            circ = circuit.copy()
            circ = qiskit.transpiler.passes.RemoveBarriers()(self.randomize_circuit(circ))
            circ.add_register(ClassicalRegister(size - 1))
            circ_zz = transpile(circ.compose(circuit_measure_zz))
            corr_zz.append(circ_zz)
        result_zz = execute(corr_zz, self.machine, shots = self.shots/self.M).result().get_counts()

        res = [list(self.correspondance(a).values()) for a in result_zz]
        res = np.array(res)
        return np.mean(res, axis=0)

        # print(len(result_zz))

    def correspondance(self, result):
        self.correlation_list = list()
        dic = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        size = 7
        for count in result:
            counta = count[len(count)-7:len(count)]
            arr = 1 - np.array(list(map(int, counta))) * 2
            for i in range(size):
                for j in range(i-1, i+ round(size)):
                    if i != j:
                        distance = j -i
                        corr = arr[i%size] * arr[j%size] * result[count]/ (self.shots/self.M)
                        self.correlation_list.append(corr)
                        dic[distance] = corr + dic[abs(distance)]
        return dic



    
    def CalculateCorrespondance(self, circuit_quantum):
        self.correlation_list = list()
        self.correlation_circuit = circuit_quantum.copy()
        self.size = len(list(self.hyperbolic_structure.boundary_qubits))
        cr = ClassicalRegister(self.size)
        self.correlation_circuit.add_register(cr)
        circuit_measure_cor = QuantumCircuit(self.correlation_circuit.num_qubits, self.size)
        circuit_measure_cor.measure(list(self.hyperbolic_structure.boundary_qubits), list(range(self.size)))


        circuit_transpile_cor = transpile(self.correlation_circuit.compose(circuit_measure_cor), self.machine)
        counts_cor = self.machine.run(circuit_transpile_cor, shots = self.shots).result().get_counts()
        self.dic = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        for count in counts_cor:
            counta = count[len(count)-7:len(count)]
            arr = 1 - np.array(list(map(int, counta))) * 2
            for i in range(self.size):
                for j in range(i-1, i+ round(self.size)):
                    if i != j:
                        distance = j -i
                        corr = arr[i%self.size] * arr[j%self.size] * counts_cor[count]/self.shots
                        self.correlation_list.append(corr)
                        self.dic[distance] = corr + self.dic[abs(distance)]

    def plotCorrespondance(self, circuit_quantum):
        self.CalculateCorrespondance(circuit_quantum)
        corLis = list()
        cordLis = list()
        for i in self.dic:
            if i > 0:
                corLis.append(i)
                cordLis.append(self.dic[i])
        plt.scatter(corLis, cordLis)

    def check_initial(qc, index):
            for oper in qc.data: 
                if (oper.qubits[0].index == index): 
                    return False
            return True
    

    def randomize_circuit(self, circuit):
        circuit = transpile(circuit, basis_gates=["rz", "rx", "cx"])
        numQubits = circuit.num_qubits
        cx_apply = {}
        for i in range(numQubits):
            cx_apply[i] = False
        qc = QuantumCircuit(numQubits)
        # start = time.time()
        for index, operator in enumerate(circuit.data):
            num_qubits = len(operator.qubits)
            if num_qubits == 1:
                operating_qubit = int(operator.qubits[0].index)
                if cx_apply[operator.qubits[0].index]:
                    qc.append(operator.operation, [operating_qubit])
                    cx_apply[operator.qubits[0].index] = False
                else:
                    if Simulator.check_initial(qc, operating_qubit) and index < 50:
                        qc.append(operator.operation, [operating_qubit])
                        continue
                    random_pauli = np.random.choice(Simulator.pauli_list)
                    qc.append(Pauli(random_pauli), [operating_qubit])
                    qc.barrier(operating_qubit)
                    qc.append(Pauli(random_pauli), [operating_qubit])
                    qc.append(operator.operation, [operating_qubit])
            if num_qubits == 2:
                control_qubit = operator.qubits[0].index
                target_qubit = operator.qubits[1].index
                random_pauli_double = np.random.choice(range(len(Simulator.pauli_double)))
                random_pauli_double = Simulator.pauli_double[random_pauli_double]
                qc.append(Pauli(random_pauli_double[0][0]), [control_qubit])
                qc.append(Pauli(random_pauli_double[0][1]), [target_qubit])
                qc.append(operator.operation, [control_qubit, target_qubit])
                qc.barrier([control_qubit, target_qubit])
                qc.append(Pauli(random_pauli_double[1][0]), [control_qubit])
                qc.append(Pauli(random_pauli_double[1][1]), [target_qubit])
                cx_apply[control_qubit] = True
                cx_apply[target_qubit] = True
        # print(time.time() - start)
        return qc