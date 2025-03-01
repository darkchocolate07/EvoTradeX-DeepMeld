import numpy as np

def complement_code(X):
    """
    Perform complement coding on input array X.
    Each sample x becomes [x, 1 - x].
    Ensures each component is in [0,1].
    """
    # X assumed in [0,1]. If not, you must normalize it externally.
    return np.concatenate([X, 1 - X], axis=1)

class TopoARTLayer:
    """
    A single TopoART layer (like Fuzzy ART), but with:
      - candidate nodes (noise handling)
      - optional partial learning for the second best match
      - topology edges
    """

    def __init__(self, vigilance=0.9, beta_sbm=0.5, phi=5, max_min_dist=1.0):
        """
        :param vigilance: 0 < vigilance <= 1. Smaller => bigger categories.
        :param beta_sbm: partial learning rate for second best match in [0..1].
        :param phi: node candidate threshold; if node's counter < phi after some time, remove it.
        :param max_min_dist: maximum complement-coded distance allowed. Usually = 2*d if no normalization is done.
        """
        self.vigilance = vigilance
        self.beta_sbm = beta_sbm
        self.phi = phi
        self.max_min_dist = max_min_dist

        # Each node will store:
        # w   => category weights
        # count => how many samples have been learned by this node
        # edges => set of node indices it connects to
        self.nodes = []  # list of dict: [{'w':..., 'count':..., 'edges':set(...), 'permanent': bool}, ...]
        
    def _choice_function(self, x, w):
        """
        Fuzzy ART choice function: activation = |x AND w| / (alpha + |w|)
        We set alpha = 0.0001
        x AND w => component-wise min
        """
        alpha = 1e-4
        intersection = np.minimum(x, w)
        numer = np.sum(intersection)
        denom = alpha + np.sum(w)
        return numer / denom
    
    def _match_function(self, x, w):
        """
        Fuzzy ART match function:
        match = |x AND w| / |x|
        Must be >= vigilance for resonance.
        """
        intersection = np.minimum(x, w)
        numer = np.sum(intersection)
        denom = np.sum(x) + 1e-12
        return numer / denom

    def _update_weights(self, w, x, full=True, beta=1.0):
        """
        If full=True, it's the best match => w_new = x AND w
        If full=False, partial update => w_new = beta*(x AND w) + (1-beta)*w
        """
        intersection = np.minimum(x, w)
        if full:
            return intersection  # fast learning
        else:
            return beta * intersection + (1.0 - beta) * w

    def insert_node(self, x):
        """
        Insert a brand new node representing x.
        This node is initially a candidate (count=1).
        """
        node_dict = {
            'w': x.copy(),
            'count': 1,
            'edges': set(),
            'permanent': False
        }
        self.nodes.append(node_dict)
        return len(self.nodes) - 1

    def remove_candidate_nodes(self):
        """
        Periodically remove nodes with count < phi.
        """
        new_nodes = []
        for nd in self.nodes:
            # If permanent or count >= phi => keep
            if nd['permanent'] or nd['count'] >= self.phi:
                new_nodes.append(nd)
            # else => remove node + its edges
        self.nodes = new_nodes

    def train_sample(self, x):

        # Step 1: compute activation for all nodes
        if len(self.nodes) == 0:
            # no nodes => create first node
            new_id = self.insert_node(x)
            self.nodes[new_id]['permanent'] = (self.nodes[new_id]['count'] >= self.phi)
            return

        activations = []
        for i, nd in enumerate(self.nodes):
            act = self._choice_function(x, nd['w'])
            activations.append((act, i))
        # sort by activation descending
        activations.sort(key=lambda tup: tup[0], reverse=True)

        # Step 2: find best match that passes vigilance
        best_match_id = None
        for act, idx in activations:
            match_val = self._match_function(x, self.nodes[idx]['w'])
            if match_val >= self.vigilance:
                best_match_id = idx
                break

        if best_match_id is None:
            # no suitable node => create new node
            new_id = self.insert_node(x)
            self.nodes[new_id]['permanent'] = (self.nodes[new_id]['count'] >= self.phi)
            return
        else:
            # full update best match
            old_w = self.nodes[best_match_id]['w']
            new_w = self._update_weights(old_w, x, full=True, beta=1.0)
            self.nodes[best_match_id]['w'] = new_w
            self.nodes[best_match_id]['count'] += 1
            if not self.nodes[best_match_id]['permanent'] and (self.nodes[best_match_id]['count'] >= self.phi):
                self.nodes[best_match_id]['permanent'] = True

            # find second best match that passes vigilance
            second_best_id = None
            for act, idx in activations:
                if idx == best_match_id:
                    continue
                match_val = self._match_function(x, self.nodes[idx]['w'])
                if match_val >= self.vigilance:
                    second_best_id = idx
                    break
            if second_best_id is not None:
                # partial update
                old_w2 = self.nodes[second_best_id]['w']
                new_w2 = self._update_weights(old_w2, x, full=False, beta=self.beta_sbm)
                self.nodes[second_best_id]['w'] = new_w2
                self.nodes[second_best_id]['count'] += 1
                if (not self.nodes[second_best_id]['permanent']) and (self.nodes[second_best_id]['count'] >= self.phi):
                    self.nodes[second_best_id]['permanent'] = True

                # create edges
                self.nodes[best_match_id]['edges'].add(second_best_id)
                self.nodes[second_best_id]['edges'].add(best_match_id)

    def get_clusters(self):

        visited = set()
        clusters = []
        for i, nd in enumerate(self.nodes):
            if nd['permanent'] is False:
                continue
            if i not in visited:
                # BFS or DFS to find all connected permanent nodes
                stack = [i]
                comp = []
                while stack:
                    curr = stack.pop()
                    if curr in visited:
                        continue
                    visited.add(curr)
                    comp.append(curr)
                    # push neighbors if permanent
                    for nb in self.nodes[curr]['edges']:
                        if self.nodes[nb]['permanent']:
                            if nb not in visited:
                                stack.append(nb)
                clusters.append(comp)
        return clusters


class TopoART:
    """
    Two-layer TopoART system:
      - TopoART_a with vigilance rho_a
      - TopoART_b with vigilance rho_b ( > rho_a)
      - Filter mechanism: only samples that resonate in layer_a and layer_a node.count >= phi => go to layer_b
    """
    def __init__(self, 
                 rho_a=0.9, rho_b=None, 
                 beta_sbm=0.5, phi=5, 
                 tau=100):

        self.rho_a = rho_a
        if rho_b is None:
            self.rho_b = 0.5 * (rho_a + 1.0)
        else:
            self.rho_b = rho_b

        self.beta_sbm = beta_sbm
        self.phi = phi
        self.tau = tau

        self.layer_a = TopoARTLayer(vigilance=self.rho_a, beta_sbm=self.beta_sbm, phi=self.phi)
        self.layer_b = TopoARTLayer(vigilance=self.rho_b, beta_sbm=self.beta_sbm, phi=self.phi)

        self.sample_count = 0

    def fit(self, X):

        # complement coding
        X_cc = complement_code(X)

        for i, x in enumerate(X_cc):
            self.sample_count += 1

            # 1) train layer_a
            self.layer_a.train_sample(x)

            # 2) if best match in layer_a is found & node is permanent => pass x to layer_b
            best_id = self._best_match_id(self.layer_a, x)
            if best_id is not None:
                # check if that node is permanent
                if self.layer_a.nodes[best_id]['permanent']:
                    # pass x to layer_b
                    self.layer_b.train_sample(x)

            # remove candidate nodes every tau samples
            if (self.sample_count % self.tau) == 0:
                self.layer_a.remove_candidate_nodes()
                self.layer_b.remove_candidate_nodes()

    def _best_match_id(self, layer, x):
        """Return best match id that passes vigilance, or None if no match found."""
        if len(layer.nodes) == 0:
            return None
        activations = []
        for i, nd in enumerate(layer.nodes):
            act = layer._choice_function(x, nd['w'])
            activations.append((act, i))
        activations.sort(key=lambda tup: tup[0], reverse=True)
        for act, idx in activations:
            match_val = layer._match_function(x, layer.nodes[idx]['w'])
            if match_val >= layer.vigilance:
                return idx
        return None

    def get_clusters_a(self):
        """Return the clusters from layer_a (connected permanent nodes)."""
        return self.layer_a.get_clusters()

    def get_clusters_b(self):
        """Return the clusters from layer_b (connected permanent nodes)."""
        return self.layer_b.get_clusters()
