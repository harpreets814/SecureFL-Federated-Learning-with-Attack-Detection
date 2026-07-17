import flwr as fl
import torch
import numpy as np
from model import SimpleModel

DEVICE = torch.device("cpu")

def load_data(path):
    data = np.load(path)
    return (
        torch.tensor(data["X"], dtype=torch.float32),
        torch.tensor(data["y"], dtype=torch.long),
    )

# 🔥 Noise injection
def add_noise(x, noise_level=0.5):
    noise = torch.randn_like(x) * noise_level
    return x + noise


class FLClient(fl.client.NumPyClient):
    def __init__(self):
        self.model = SimpleModel().to(DEVICE)
        self.X, self.y = load_data("../data/processed/client4.npz")

    def get_parameters(self, config):
        params = [val.cpu().numpy() for val in self.model.state_dict().values()]

        # 🚨 ADD NOISE TO WEIGHTS
        noisy = [p + np.random.normal(0, 0.3, size=p.shape) for p in params]
        return noisy

    def set_parameters(self, parameters):
        state_dict = zip(self.model.state_dict().keys(), parameters)
        self.model.load_state_dict({k: torch.tensor(v) for k, v in state_dict})

    def fit(self, parameters, config):
        self.set_parameters(parameters)

        # 🚨 APPLY INPUT NOISE
        X_noisy = add_noise(self.X)

        class_counts = torch.bincount(self.y)
        total = len(self.y)
        weights = total / (2 * class_counts.float())

        loss_fn = torch.nn.CrossEntropyLoss(weight=weights)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)

        batch_size = 256
        self.model.train()

        for _ in range(2):
            perm = torch.randperm(X_noisy.size(0))
            X_shuffled = X_noisy[perm]
            y_shuffled = self.y[perm]

            for i in range(0, X_noisy.size(0), batch_size):
                xb = X_shuffled[i:i+batch_size]
                yb = y_shuffled[i:i+batch_size]

                optimizer.zero_grad()
                outputs = self.model(xb)
                loss = loss_fn(outputs, yb)
                loss.backward()
                optimizer.step()

        return self.get_parameters(config), len(self.X), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(self.X)
            preds = outputs.argmax(1)
            acc = (preds == self.y).float().mean()

        return 0.0, len(self.X), {"accuracy": float(acc)}


fl.client.start_numpy_client(
    server_address="localhost:8080",
    client=FLClient(),
)