import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import classification_report



# -------------------------------
# LOAD DATA
# -------------------------------
data = np.load("../data/processed/client1.npz")

X = torch.tensor(data["X"], dtype=torch.float32)
y = torch.tensor(data["y"], dtype=torch.long)

print("Data shape:", X.shape)

# -------------------------------
# MODEL
# -------------------------------
model = nn.Sequential(
    nn.Linear(1000, 256),
    nn.ReLU(),
    nn.Dropout(0.4),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Linear(128, 2)
)

# Calculate class weights
class_counts = torch.bincount(y)
total = len(y)

weights = total / (2 * class_counts.float())

loss_fn = nn.CrossEntropyLoss(weight=weights)

perm = torch.randperm(X.size(0))
X = X[perm]
y = y[perm]

# -------------------------------
# TRAINING SETUP
# -------------------------------
optimizer = optim.Adam(model.parameters(), lr=0.001)


# -------------------------------
# TRAIN LOOP
# -------------------------------
batch_size = 256

for epoch in range(10):
    perm = torch.randperm(X.size(0))
    X_shuffled = X[perm]
    y_shuffled = y[perm]

    for i in range(0, X.size(0), batch_size):
        xb = X_shuffled[i:i+batch_size]
        yb = y_shuffled[i:i+batch_size]

        optimizer.zero_grad()

        outputs = model(xb)
        loss = loss_fn(outputs, yb)

        loss.backward()
        optimizer.step()

    # evaluate
    with torch.no_grad():
        outputs = model(X)
        preds = outputs.argmax(1)
        acc = (preds == y).float().mean()

    print(f"Epoch {epoch+1} | Loss: {loss.item():.4f} | Acc: {acc:.4f}")

print(classification_report(y.numpy(), preds.numpy()))