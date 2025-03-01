import numpy as np

def EFCM(X, Dthr):
    c = [X[0].copy()]
    r = [0.]
    n, d = X.shape
    M = np.zeros((n,1))
    M[0,0] = 1
    for i in range(1,n):
        x = X[i]
        dist = np.sqrt(np.sum((x - np.array(c))**2, axis=1))
        found = False
        for j in range(len(c)):
            if dist[j] <= r[j]:
                found = True
                break
        if not found:
            idx = np.argmin(dist)
            if dist[idx] + r[idx] > 2*Dthr:
                c.append(x.copy())
                r.append(0.)
                M = np.hstack((M, np.zeros((n,1))))
                M[i,-1] = 1
            else:
                S = dist[idx] + r[idx]
                r[idx] = S/2
                direction = x - c[idx]
                normd = np.linalg.norm(direction)
                if normd>1e-12:
                    direction *= (r[idx]/normd)
                c[idx] = x - direction
                M[i,idx] = 1
    U = np.zeros((n,len(c)))
    for i in range(n):
        denom = 0
        dvals = []
        for j in range(len(c)):
            dvals.append(np.linalg.norm(X[i]-c[j]))
        dvals = np.array(dvals)
        for j in range(len(c)):
            if dvals[j]<1e-12:
                U[i,:] = 0
                U[i,j] = 1
                denom=1
                break
            else:
                denom += (1.0/dvals[j])**2
        if denom<1e-12:
            continue
        for j in range(len(c)):
            if dvals[j]<1e-12:
                continue
            U[i,j] = ((1.0/dvals[j])**2)/denom
    return c, r, U

def EFCM_objective(X, c, U):
    val=0
    for i in range(X.shape[0]):
        for j in range(len(c)):
            val+=U[i,j]*np.linalg.norm(X[i]-c[j])
    return val
