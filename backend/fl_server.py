import flwr as fl
import numpy as np
from flwr.common import FitRes, Status, Code
from security import compute_similarity
from trust_manager import TrustManager
from anomaly_detector import AnomalyDetector
import json
import os

metrics_history = []

def compute_metrics(client_ids, predictions, attacker_index):
    y_true = []
    y_pred = []

    for i, (cid, pred) in enumerate(zip(client_ids, predictions)):

        # 🔥 Ground truth based on BEHAVIOR
        if i == attacker_index:
            y_true.append(1)
        else:
            y_true.append(0)

        # Prediction
        y_pred.append(1 if pred == -1 else 0)

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    TP = np.sum((y_true == 1) & (y_pred == 1))
    TN = np.sum((y_true == 0) & (y_pred == 0))
    FP = np.sum((y_true == 0) & (y_pred == 1))
    FN = np.sum((y_true == 1) & (y_pred == 0))

    precision = TP / (TP + FP + 1e-8)
    recall = TP / (TP + FN + 1e-8)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-8)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "TP": int(TP),
        "FP": int(FP),
        "TN": int(TN),
        "FN": int(FN),
    }



def compute_asr(blocked_clients, attacker_index, client_ids):
    if attacker_index >= len(client_ids):
        return 0.0

    attacker_id = client_ids[attacker_index]

    if attacker_id in blocked_clients:
        return 0.0  # attack failed
    else:
        return 1.0  # attack succeeded

# -------------------------------
# GRADIENT CLIPPING FUNCTION
# -------------------------------
def clip_updates(updates, clip_value=1.0):
    clipped = []
    for update in updates:
        norm = np.linalg.norm(update)
        if norm > clip_value:
            update = update * (clip_value / norm)
        clipped.append(update)
    return clipped


# -------------------------------
# LOGGING SETUP
# -------------------------------
LOG_FILE = "logs.json"

def save_log(data):
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump({"metrics": []}, f)

    with open(LOG_FILE, "r") as f:
        existing = json.load(f)

    # append metrics history
    if "metrics" not in existing:
        existing["metrics"] = []

    if "metrics" in data:
        existing["metrics"].extend(data["metrics"])

    # overwrite alerts + trust each round
    existing["alerts"] = data.get("alerts", [])
    existing["trust"] = data.get("trust", {})
    existing["round"] = data.get("round", 0)

    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

print("🚀 Secure FL Server starting...")

trust_manager = TrustManager()
anomaly_detector = AnomalyDetector()

# -------------------------------
# CUSTOM STRATEGY
# -------------------------------
class SecureFedAvg(fl.server.strategy.FedAvg):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_accuracy = None

    # -------------------------------
    # CAPTURE ACCURACY
    # -------------------------------
    def aggregate_evaluate(self, server_round, results, failures):
        aggregated = super().aggregate_evaluate(server_round, results, failures)

        if aggregated is not None:
            loss, metrics = aggregated
            if "accuracy" in metrics:
                self.last_accuracy = metrics["accuracy"]

        return aggregated

    # -------------------------------
    # TRAINING AGGREGATION
    # -------------------------------
    def aggregate_fit(self, server_round, results, failures):

        if not results:
            return None, {}

        updates = []
        client_ids = []
        original_ndarrays = []

        for client, fit_res in results:
            ndarrays = fl.common.parameters_to_ndarrays(fit_res.parameters)
            original_ndarrays.append(ndarrays)

            flat = np.concatenate([p.flatten() for p in ndarrays])
            updates.append(flat)

            client_ids.append(client.cid)
            trust_manager.init_client(client.cid)

        # -------------------------------
        # 🔥 APPLY GRADIENT CLIPPING
        # -------------------------------
        updates = clip_updates(updates, clip_value=1.0)

        # -------------------------------
        # DETECTION
        # -------------------------------
        sim_matrix = compute_similarity(updates)
        avg_sim = sim_matrix.mean(axis=1)
        iso_preds = anomaly_detector.detect(
            updates, 
            avg_sim=avg_sim,
            client_ids=client_ids)
        
        # ===============================
        # EVALUATION METRICS (NEW)
        # ===============================
        
        # 🔥 Identify attacker (lowest similarity)
        attacker_index = np.argmin(avg_sim)

        # 🔥 Compute metrics
        metrics_eval = compute_metrics(client_ids, iso_preds, attacker_index)

        print("\n==============================", flush=True)
        print("\n📊 Detection Metrics:", flush=True)
        for k, v in metrics_eval.items():
            print(f"{k}: {v}", flush=True)
        print("==============================", flush=True)

        threshold = np.mean(avg_sim) - 0.1
        

        print(f"\n🔍 Round {server_round} similarity scores:")
        for cid, sim in zip(client_ids, avg_sim):
            print(f"Client {cid[:6]} → similarity: {sim:.4f}")
        print(f"Threshold: {threshold:.4f}")

        # -------------------------------
        # FILTERING
        # -------------------------------
        filtered_results = []

        for i, (client, fit_res) in enumerate(results):
            client_id = client_ids[i]

            cosine_flag = avg_sim[i] < threshold
            iso_flag = iso_preds[i] == -1
            suspicious = cosine_flag or iso_flag

            trust_manager.update_trust(client_id, suspicious)

            if trust_manager.is_blocked(client_id):
                print(f"🚫 BLOCKED client {client_id}")
                continue

            if suspicious:
                print(f"⚠️ Down-weighting client {client_id}")

                new_fit_res = FitRes(
                    status=Status(code=Code.OK, message="Down-weighted"),
                    parameters=fit_res.parameters,
                    num_examples=int(fit_res.num_examples * 0.3),
                    metrics=fit_res.metrics,
                )

                filtered_results.append((client, new_fit_res))
            else:
                filtered_results.append((client, fit_res))

        if len(filtered_results) == 0:
            print("⚠️ All clients suspicious — keeping best one")
            best_idx = np.argmax(avg_sim)
            filtered_results.append(results[best_idx])

        # ===============================
        # ATTACK SUCCESS RATE (ASR)
        # ===============================
        blocked_clients = [
            cid for cid in client_ids
            if trust_manager.is_blocked(cid)
        ]

        asr = compute_asr(blocked_clients, attacker_index, client_ids)

        # ===============================
        # 🔥 STORE METRICS FOR DASHBOARD
        # ===============================
        metrics_history.append({
            "round": server_round,
            "accuracy": float(self.last_accuracy) if self.last_accuracy else 0.0,
            "precision": float(metrics_eval.get("precision", 0.0)) if metrics_eval else 0.0,
            "recall": float(metrics_eval.get("recall", 0.0)) if metrics_eval else 0.0,
            "f1": float(metrics_eval.get("f1", 0.0)) if metrics_eval else 0.0,
            "asr": float(asr) if asr is not None else 0.0
        })
        
        if len(metrics_history) > 20:
            metrics_history[:] = metrics_history[-20:]

        print(f"🚨 Attack Success Rate: {asr}", flush=True)
        print("==============================\n", flush=True)


        # -------------------------------
        # 🔥 LOGGING WITH METRICS
        # -------------------------------
        log_data = {
            "round": server_round,
            "alerts": [],
            "trust": trust_manager.trust_scores,
            "metrics": []
        }

        # store accuracy
        if self.last_accuracy is not None:
            log_data["metrics"].append({
                "round": server_round,
                "accuracy": self.last_accuracy
            })

        for i in range(len(results)):
            client_id = client_ids[i]

            cosine_flag = avg_sim[i] < threshold
            iso_flag = iso_preds[i] == -1
            suspicious = cosine_flag or iso_flag

            if suspicious:
                log_data["alerts"].append(f"⚠️ Suspicious client {client_id[:6]}")

            if trust_manager.is_blocked(client_id):
                log_data["alerts"].append(f"🚫 Blocked client {client_id[:6]}")

        save_log(log_data)

        # -------------------------------
        # ROLLBACK PROTECTION
        # -------------------------------
        num_suspicious = sum(
            1 for i in range(len(results))
            if avg_sim[i] < threshold
        )

        if num_suspicious > len(results) // 2:
            print("🚨 Too many suspicious clients — SKIPPING ROUND")
            return None, {}

        return super().aggregate_fit(server_round, filtered_results, failures)


# -------------------------------
# METRICS
# -------------------------------
def weighted_average(metrics):
    valid_metrics = [
        (num_examples, m)
        for num_examples, m in metrics
        if "accuracy" in m
    ]

    if len(valid_metrics) == 0:
        return {"accuracy": 0.0}

    accuracies = [
        num_examples * m["accuracy"]
        for num_examples, m in valid_metrics
    ]

    examples = [num_examples for num_examples, _ in valid_metrics]

    return {"accuracy": sum(accuracies) / sum(examples)}


# -------------------------------
# START SERVER
# -------------------------------
strategy = SecureFedAvg(
    fraction_fit=0.8,   # slightly higher = better detection
    fraction_evaluate=0.8,
    min_fit_clients=2,
    min_available_clients=2,
    evaluate_metrics_aggregation_fn=weighted_average
)


fl.server.start_server(
    server_address="localhost:8080",
    config=fl.server.ServerConfig(num_rounds=12),
    strategy=strategy,
)