import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# -------------------------------
# 1. LOAD DATA (ROBUST)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "MPDD.csv")

df = pd.read_csv(DATA_PATH, encoding="latin-1", low_memory=False)

print("\n✅ Data Loaded")
print("Shape:", df.shape)
print("Columns:", df.columns.tolist())

# -------------------------------
# 2. CLEAN DATA
# -------------------------------

# Normalize column names
df.columns = df.columns.str.strip().str.lower()

if "correct" in df.columns:
    label_map = {
        "true": 1,
        "false": 0,
        "1": 1,
        "0": 0,
        "correct": 1,
        "incorrect": 0,
        "yes": 1,
        "no": 0
    }
    df["label"] = df["correct"].astype(str).str.lower().str.strip().map(label_map)
elif "ismalicious" in df.columns:
    df["label"] = df["ismalicious"].astype(int)
else:
    raise ValueError("No supported label column found")

# Keep only required columns
df = df[["prompt", "label"]]

# Drop missing
df = df.dropna()

print("\n🔍 BEFORE label cleaning:")
print(df["label"].unique()[:20])

# -------------------------------
# 3. FIX LABELS (CRITICAL)
# -------------------------------

# Convert to int
df = df.dropna(subset=["label"])
df["label"] = df["label"].astype(int)

print("\n✅ AFTER label cleaning:")
print(df["label"].value_counts())

# -------------------------------
# 4. CLEAN TEXT
# -------------------------------

df["prompt"] = df["prompt"].astype(str).str.strip()

# Remove very short prompts
df = df[df["prompt"].str.len() > 3]

print("\n✅ Cleaned Data Shape:", df.shape)

# -------------------------------
# 5. FEATURE ENGINEERING (TF-IDF)
# -------------------------------

vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words="english"
)

X = vectorizer.fit_transform(df["prompt"]).toarray()
y = df["label"].values

print("\n✅ TF-IDF Completed")
print("Feature shape:", X.shape)

# -------------------------------
# 6. SPLIT INTO CLIENTS (UPDATED)
# -------------------------------

# Step 1: Separate attacker data (20%)
X_temp, X_attacker, y_temp, y_attacker = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Step 2: Split remaining into 4 clients
X_c1, X_rem, y_c1, y_rem = train_test_split(
    X_temp, y_temp, test_size=0.75, random_state=42
)

X_c2, X_rem, y_c2, y_rem = train_test_split(
    X_rem, y_rem, test_size=0.66, random_state=42
)

X_c3, X_c4, y_c3, y_c4 = train_test_split(
    X_rem, y_rem, test_size=0.5, random_state=42
)

# -------------------------------
# 🔥 CLASS DISTRIBUTION (ADDED)
# -------------------------------

print("\n📊 Class distribution:")
print("Client1:", np.bincount(y_c1))
print("Client2:", np.bincount(y_c2))
print("Client3:", np.bincount(y_c3))
print("Client4:", np.bincount(y_c4))
print("Attacker:", np.bincount(y_attacker))

# -------------------------------
# 7. SAVE
# -------------------------------

SAVE_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(SAVE_DIR, exist_ok=True)

np.savez(os.path.join(SAVE_DIR, "client1.npz"), X=X_c1, y=y_c1)
np.savez(os.path.join(SAVE_DIR, "client2.npz"), X=X_c2, y=y_c2)
np.savez(os.path.join(SAVE_DIR, "client3.npz"), X=X_c3, y=y_c3)  # label flip
np.savez(os.path.join(SAVE_DIR, "client4.npz"), X=X_c4, y=y_c4)  # noise
np.savez(os.path.join(SAVE_DIR, "attacker.npz"), X=X_attacker, y=y_attacker)

print("\n✅ Data saved successfully")

print("\n📊 Final splits:")
print("Client1:", X_c1.shape)
print("Client2:", X_c2.shape)
print("Client3 (label flip):", X_c3.shape)
print("Client4 (noise):", X_c4.shape)
print("Attacker:", X_attacker.shape)