import numpy as np

from .index import passages_for


def features(encoder, pairs, cache, dim=768):
    rows = []
    for p in pairs:
        ps = passages_for(cache, p["drug_a"], p["drug_b"])
        rows.append(encoder(ps).mean(axis=0) if ps else np.zeros(dim))
    return np.array(rows)


def fit(X, y, seed):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler().fit(X)
    clf = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed)
    clf.fit(scaler.transform(X), y)
    return scaler, clf


def predict(scaler, clf, X):
    return clf.predict(scaler.transform(X)).tolist()
