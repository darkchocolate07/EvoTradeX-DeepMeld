import numpy as np

def DIC(X, IT, SLOPE):
    clusters = []
    n, d = X.shape
    for i in range(n):
        assigned = False
        for c in clusters:
            dist = np.abs(c['kernel'] - X[i])
            mu = np.exp(-dist)
            best = np.min(mu)
            if best>=IT:
                for dim in range(d):
                    if X[i,dim]>c['kernel'][dim]:
                        c['right'][dim] = X[i,dim]+SLOPE*(np.max(X[:,dim])-np.min(X[:,dim]))
                    else:
                        c['left'][dim] = X[i,dim]-SLOPE*(np.max(X[:,dim])-np.min(X[:,dim]))
                c['kernel'] = (c['kernel']+X[i])/2
                assigned = True
                break
        if not assigned:
            left = X[i]-SLOPE*(np.max(X,axis=0)-np.min(X,axis=0))
            right = X[i]+SLOPE*(np.max(X,axis=0)-np.min(X,axis=0))
            clusters.append({'left': left, 'right': right, 'kernel': X[i].copy()})
    return clusters