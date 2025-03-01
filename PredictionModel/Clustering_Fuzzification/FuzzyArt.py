import numpy as np
def FuzzyART(X, alpha, rho, beta, epochs):
    n, d = X.shape
    w = []
    categories = []
    for _ in range(epochs):
        for i in range(n):
            T = []
            for j in range(len(w)):
                numer = np.sum(np.minimum(X[i], w[j]))
                denom = alpha + np.sum(w[j])
                T.append(numer/denom)
            if len(T)==0:
                w.append(X[i].copy())
                categories.append([i])
                continue
            jdx = np.argmax(T)
            if np.sum(np.minimum(X[i], w[jdx]))/np.sum(X[i]) >= rho:
                w[jdx] = beta*np.minimum(X[i], w[jdx]) + (1-beta)*w[jdx]
                categories[jdx].append(i)
            else:
                w.append(X[i].copy())
                categories.append([i])
    return w, categories
