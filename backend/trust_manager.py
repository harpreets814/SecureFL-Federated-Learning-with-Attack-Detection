class TrustManager:
    def __init__(self):
        self.trust_scores = {}

    def init_client(self, client_id):
        if client_id not in self.trust_scores:
            self.trust_scores[client_id] = 1.0

    def update_trust(self, client_id, suspicious):
        if suspicious:
            self.trust_scores[client_id] -= 0.5
        else:
            self.trust_scores[client_id] += 0.05

        # clamp
        self.trust_scores[client_id] = max(0.0, min(1.0, self.trust_scores[client_id]))

    def is_blocked(self, client_id):
        return self.trust_scores.get(client_id, 1.0) < 0.3