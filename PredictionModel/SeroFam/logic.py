import numpy as np

class SeroFAM:
    def __init__(self, input_dim, output_dim, alpha=0.01, beta=0.9, rho=0.75, init_nodes=1):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.rules = []
        for _ in range(init_nodes):
            self.rules.append({
                'w_in': np.ones(input_dim),
                'w_out': np.zeros(output_dim),
                'count': 0
            })
    def _choice(self, x):
        T = []
        for r in self.rules:
            numer = np.sum(np.minimum(x, r['w_in']))
            denom = self.alpha + np.sum(r['w_in'])
            T.append(numer/denom)
        return np.argmax(T), np.max(T)
    def _match(self, x, w):
        return np.sum(np.minimum(x, w))/np.sum(x)
    def train(self, X, Y, epochs=1):
        for _ in range(epochs):
            for i in range(len(X)):
                x = X[i]
                y = Y[i]
                j, val = self._choice(x)
                if self._match(x, self.rules[j]['w_in'])>=self.rho:
                    self.rules[j]['w_in'] = self.beta*np.minimum(x, self.rules[j]['w_in'])+(1-self.beta)*self.rules[j]['w_in']
                    self.rules[j]['w_out']+= self.alpha*(y-self.rules[j]['w_out'])
                    self.rules[j]['count']+=1
                else:
                    self.rules.append({
                        'w_in': x.copy(),
                        'w_out': y.copy(),
                        'count':1
                    })
    def predict(self, x):
        best, val = self._choice(x)
        return self.rules[best]['w_out']
