from utils.import_list import *

class Wilson:
    num = 2

    def __init__(self, params):
        self.params = params
        self.hyperbolic_structure = HyperbolicStructure(params["num_layers"])
        self.simulator = Simulator(self.hyperbolic_structure, typee = params["typee"], name = params["name"], noise = params["noise"], noise_model = params["noise_model"], shots = params["shots"])
        self.runs = list()
        Wilson.num += 1
        

    def run(self):
        alg = Algorithm(Circuit(self.hyperbolic_structure.num_layers), self.simulator, Wilson.num)
        self.runs.append(alg)
        # self.reset_dir()
        os.mkdir("circuit_configs"+ str(Wilson.num)+"/" + alg.name)
        alg.forward_feed(self.params["iterations"], self.params["beta_initial"], self.params["deviation_initial"], self.params["change"])

    def main(self):
        os.mkdir("circuit_configs"+ str(Wilson.num))
        for i in range(self.params["num_attempts"]):
            self.run()

    def remove_dir(self):
        shutil.rmtree(r'circuit_configs'+ str(Wilson.num))
        
    def reset_dir(self):
        shutil.rmtree(r'circuit_configs'+ str(Wilson.num))
        os.mkdir("circuit_configs" + str(Wilson.num))

    def save(self):
        pickle.dump(self, open("total", "wr"))