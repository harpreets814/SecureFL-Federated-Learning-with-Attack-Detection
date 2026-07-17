import flwr as fl
import torch
import numpy as np
from model import SimpleModel

DEVICE = torch.device("cpu")

# ==============================
# CONFIG: CHANGE ATTACK TYPE HERE
# ==============================
ATTACK_TYPE = "poison"  
# Options: "noise", "label_flip", "poison", None


# ==============================
# LOAD DATA
# ==============================
def load_data(path):
    data = np.load(path)
    return (
        torch.tensor(data["X"], dtype=torch.float32),
        torch.tensor(data["y"], dtype=torch.long),
    )


# ==============================
# ATTACK FUNCTIONS
# ==============================

def label_flipping(y, num_classes=2):
    return (y + 1) % num_classes


def add_noise_to_weights(params, scale=0.5):
    return [p + np.random.normal(0, scale, size=p.shape) for p in params]


def scale_poisoning(params, scale=5.0):
    return [p * scale for p in params]


# ==============================
# ATTACKER CLIENT
# ==============================
class AttackerClient(fl.client.NumPyClient):
    def __init__(self):
        self.model = SimpleModel().to(DEVICE)
        self.X, self.y = load_data("../data/processed/attacker.npz")

    def get_parameters(self, config):
        params = [val.cpu().numpy() for val in self.model.state_dict().values()]

        # ===== APPLY ATTACK ON WEIGHTS =====
        if ATTACK_TYPE == "noise":
            params = add_noise_to_weights(params, scale=0.5)

        elif ATTACK_TYPE == "poison":
            params = scale_poisoning(params, scale=5.0)

        return params

    def set_parameters(self, parameters):
        state_dict = zip(self.model.state_dict().keys(), parameters)
        self.model.load_state_dict(
            {k: torch.tensor(v) for k, v in state_dict}
        )

    def fit(self, parameters, config):
        self.set_parameters(parameters)

        # ===== APPLY LABEL ATTACK =====
        X = self.X
        y = self.y

        if ATTACK_TYPE == "label_flip":
            y = label_flipping(y)

        # 🚨 attacker does BAD / fake training
        # (does not actually optimize properly)

        return self.get_parameters(config), len(X), {}

    def evaluate(self, parameters, config):
        # attacker gives misleading evaluation
        return 0.0, len(self.X), {"accuracy": 0.0}


# ==============================
# START CLIENT
# ==============================
fl.client.start_numpy_client(
    server_address="localhost:8080",
    client=AttackerClient(),
)