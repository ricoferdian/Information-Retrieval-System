import numpy as np

def euclideanDistance(query,preloaded_features):
    features = {}
    i = 0
    for key, value in preloaded_features.items():
        features[i] = value
        i += 1

    print("query", query)
    print("features extracted",features)

    distance_matrix = {}
    i = 0
    for key, value in features.items():
        distance_matrix[i] = np.linalg.norm(query-value)
        i += 1

    print("Euclidean Distance",distance_matrix)

    rank = rank_docs(distance_matrix)
    return rank

def rank_docs(score_matrix):
    return {k: v for k, v in sorted(score_matrix.items(), key=lambda item: item[1], reverse=False)}