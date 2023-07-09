import numpy as np
import networkx as nx
import random
import pywt as pywt
from scipy.sparse import csr_matrix
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import squareform


class DemoData():
    no_signals: int
    rnd = None
    ideal_signal = None



    def __init__(self, no_signals = 100, seed = 833142, no_network_clusters = 12) -> None:
        self.rnd = np.random.default_rng(seed=seed)
        self.no_signals = no_signals
        self.no_network_clusters = no_network_clusters


    def generate_raw_data(self):        
        X = np.linspace(1,1000,1000)
        unused = [(0,200), (450,520), (550, 580), (700,850), (940,1000)]
        self.ideal_signal = np.ones(X.shape) * 20
        for start,stop in unused:
            self.ideal_signal[start:stop] = -50        
        noise = self.rnd.normal(0, 1, size=(self.no_signals,1000))
        self.signals = noise + self.ideal_signal
        return self.signals


    def generate_impaired_graph(self, impairments):
        graph = nx.DiGraph()
        
        clusters = np.arange(self.no_network_clusters)    
        cluster_assignments = self.rnd.choice(clusters, self.no_signals, replace=True)
        cluster_set  = set(clusters)
        i = self.no_network_clusters
        while len(cluster_set) > 1:
            c1, c2 = self.rnd.choice(list(cluster_set), 2, replace=False)
            cluster_set.discard(c1)
            cluster_set.discard(c2)
            cluster_set.add(i)
            graph.add_edges_from([(i, c1), (i, c2)])
            i += 1

        nx.set_node_attributes(graph, "blue", "color")
        attrs = {id: {"color": color} for id, color, _, _ in impairments.values()}
        nx.set_node_attributes(graph, attrs)

        imp_signals = self.signals.copy()
        for imp_name, (edge, _, imp_x, imp_y) in impairments.items():
            affected_children = [y for _,y in nx.edge_dfs(graph, edge)]
            affected_clusters = [x for x in affected_children + [edge] if x < self.no_network_clusters]
            for cluster in affected_clusters:
                rel_signals = imp_signals[cluster_assignments == cluster,:]
                rel_signals[:,imp_x] += imp_y
                imp_signals[cluster_assignments == cluster,:] = rel_signals
        
        self.impaired_signals = imp_signals
        self.graph = graph
        self.network_clusters = cluster_assignments

        return (graph, self.impaired_signals, cluster_assignments)


    def get_sparse_wavelet_matrix(self, signals):
        coeffs = pywt.wavedec(signals, "db1", mode='zero', level=7, axis=1) #list of 7 x [100 x #no_coeffs]
        unraveled = coeffs[0]
        for level in coeffs[1:]:
            unraveled = np.concatenate([unraveled, level], axis=1)

        unraveled[np.abs(unraveled) < 30] = 0 #threshold at a hardcoded value of 30 (chosen based on experience)
        sparse_matrix = csr_matrix(unraveled)
        return sparse_matrix

    def get_adjacency_matrix(self, sparse_matrix):
        pdists = pairwise_distances(sparse_matrix, metric='cityblock')            
        dists = squareform(pdists)   
        return dists

    

def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

    '''
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
    Licensed under Creative Commons Attribution-Share Alike 
    
    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.
    
    G: the graph (must be a tree)
    
    root: the root node of current branch 
    - if the tree is directed and this is not given, 
      the root will be found and used
    - if the tree is directed and this is given, then 
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given, 
      then a random choice will be used.
    
    width: horizontal space allocated for this branch - avoids overlap with other branches
    
    vert_gap: gap between levels of hierarchy
    
    vert_loc: vertical location of root
    
    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))




def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

    '''
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
    Licensed under Creative Commons Attribution-Share Alike 
    
    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.
    
    G: the graph (must be a tree)
    
    root: the root node of current branch 
    - if the tree is directed and this is not given, 
      the root will be found and used
    - if the tree is directed and this is given, then 
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given, 
      then a random choice will be used.
    
    width: horizontal space allocated for this branch - avoids overlap with other branches
    
    vert_gap: gap between levels of hierarchy
    
    vert_loc: vertical location of root
    
    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''
    
        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            dx = width/len(children) 
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos

            
    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)
