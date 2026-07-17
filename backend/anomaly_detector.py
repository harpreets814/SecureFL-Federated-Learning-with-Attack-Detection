import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        # Existing model (KEEP THIS)
        self.model = IsolationForest(
            contamination=0.2,
            random_state=42
        )

        # 🔥 NEW: history tracking
        self.history = {}

    # -------------------------------
    # Flatten weights (same as before)
    # -------------------------------
    def flatten(self, weights):
        return np.concatenate([w.flatten() for w in weights])

    # -------------------------------
    # 🔥 Z-score computation (NEW)
    # -------------------------------
    def compute_z_scores(self, values):
        mean = np.mean(values)
        std = np.std(values) + 1e-8
        return (values - mean) / std

    # -------------------------------
    # 🔥 MAIN DETECTION (UPGRADED)
    # -------------------------------
    def detect(self, updates, avg_sim=None, client_ids=None):

        # -------------------------------
        # 1. Isolation Forest (existing)
        # -------------------------------
        flat = [self.flatten(w) for w in updates]
        iso_preds = self.model.fit_predict(flat)   # -1 anomaly, 1 normal

        # -------------------------------
        # 2. Z-score detection (NEW)
        # -------------------------------
        if avg_sim is not None:
            z_scores = self.compute_z_scores(avg_sim)
        else:
            z_scores = np.zeros(len(updates))

        # -------------------------------
        # 3. Combine + history smoothing
        # -------------------------------
        final_preds = []

        for i in range(len(updates)):
            cid = client_ids[i] if client_ids else str(i)

            # init history
            if cid not in self.history:
                self.history[cid] = []

            # store z-score history
            self.history[cid].append(z_scores[i])

            # 🔥 last 3 rounds
            recent = self.history[cid][-3:]
            avg_recent = np.mean(recent)

            # -------------------------------
            # 🔥 FINAL DECISION LOGIC
            # -------------------------------

            iso_flag = iso_preds[i] == -1
            z_flag = z_scores[i] < -1.2
            history_flag = avg_recent < -0.8

            if iso_flag or z_flag or history_flag:
                final_preds.append(-1)   # anomaly
            else:
                final_preds.append(1)    # normal

        return np.array(final_preds)