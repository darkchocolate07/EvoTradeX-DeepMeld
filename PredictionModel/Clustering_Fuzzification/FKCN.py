import numpy as np

def FCKN(X, c, m, lr, max_iter):
    n, d = X.shape
    V = X[np.random.choice(n, c, replace=False)]
    U = np.zeros((n, c))
    for _ in range(max_iter):
        for i in range(n):
            dist = np.linalg.norm(X[i] - V, axis=1)
            idx = np.argmin(dist)
            num = dist[idx]**(2/(m-1))
            denom = np.sum((dist**(2/(m-1)))**-1)**-1
            alpha = (num**-1)*denom
            V[idx] += lr * alpha * (X[i] - V[idx])
        for i in range(n):
            dist = np.linalg.norm(X[i] - V, axis=1)
            denom = np.sum((dist**(2/(m-1)))**-1)**-1
            for j in range(c):
                num = dist[j]**(2/(m-1))
                U[i,j] = (num**-1)*denom
    return V, U