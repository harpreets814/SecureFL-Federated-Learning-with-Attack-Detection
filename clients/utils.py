import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

def load_data(path):
    df = pd.read_csv(path)

    # Assume last column is label
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values

    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(y)

    # Normalize
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2
    )

    return (
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long),
        torch.tensor(X_test, dtype=torch.float32),
        torch.tensor(y_test, dtype=torch.long),
    )