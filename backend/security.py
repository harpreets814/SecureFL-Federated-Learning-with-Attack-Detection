import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def flatten_weights(weights):
    return np.concatenate([w.flatten() for w in weights])

def compute_similarity(updates):
    flattened = [flatten_weights(w) for w in updates]

    sim_matrix = cosine_similarity(flattened)

    return sim_matrix