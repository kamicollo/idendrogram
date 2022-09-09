import scipy.cluster.hierarchy as sch
import numpy as np

class BaseDendro():
    def __init__(self, linkage_matrix, cluster_assignments, threshold, dendrogram_kwargs={}) -> None:
        self.linkage_matrix = linkage_matrix
        self.cluster_assignments = cluster_assignments
        self.threshold = threshold
        self.dendrogram_kwargs = dendrogram_kwargs

        self.icoord = None
        self.dcoord = None
        self.link_colors = None
        self.ordered_leaf_labels = None
        self.leaves = None
        self.leaves_color_list = None

        self.leaders = None
        self.flat_cluster_ids = None

        self.rootnode = None
        self.nodelist = None

        self.points = None

    def get_leaders(self):
        if self.leaders is None:
            leaders, clusters = sch.leaders(self.linkage_matrix, self.cluster_assignments)
            self.leaders = leaders
            self.flat_cluster_ids = clusters    
        return self.leaders, self.flat_cluster_ids

    def get_tree(self):
        if self.rootnode is None:
            rootnode, nodelist = sch.to_tree(self.linkage_matrix, rd=True)
            self.rootnode = rootnode
            self.nodelist = nodelist
        return self.rootnode, self.nodelist

    def get_counts(self) -> callable:
        _, nodelist = self.get_tree()
        
        def labeller(id):        
            return nodelist[id].get_count()
            
        return labeller


    
    def show_only_cluster_labels(
        self, 
        fmt_string = "Cluster {cluster} ({cluster_size} data points)"
    ) -> callable:
        leaders, clusters = self.get_leaders()
        _, nodelist = self.get_tree()
        cluster_list = {}
        #for each leader ("cluster"), find the associated data points
        for l, c in zip(leaders, clusters):
            cluster_list[c] = nodelist[l].pre_order(lambda x: x.id)

        seen_clusters = []
        def labeller(id):        
            #grab first real leaf node of the passed id	
            leaf_nodes = nodelist[id].pre_order(lambda x: x.id if x.is_leaf() else None)	
            lf_node = leaf_nodes[0]	
            #traverse all leader nodes, checking if they have the leaf node	
            for c, nodes in cluster_list.items():                	
                if lf_node in nodes:	
                    cluster = c	
                    cluster_size = len(nodes)	
                    break	
                        
            if cluster not in seen_clusters:
                seen_clusters.append(cluster)
                return fmt_string.format(cluster=cluster, cluster_size=cluster_size,id=id)
            else:
                return " "
        return labeller

    def set_dendrogram(self, dendrogram):
        self.icoord = np.array(dendrogram['icoord'])
        self.dcoord = np.array(dendrogram['dcoord'])
        self.link_colors = np.array(dendrogram['color_list'])
        self.ordered_leaf_labels = np.array(dendrogram['ivl']) 
        self.leaves = np.array(dendrogram['leaves']) 
        self.leaves_color_list = np.array(dendrogram['leaves_color_list'])

    def set_default_dendrogram(self):
        default_kwargs = {
            'truncate_mode': 'level',
            'p': 4,
            'color_threshold': self.threshold,
            'leaf_label_func': None
        }
        default_kwargs.update(self.dendrogram_kwargs)
        dd = sch.dendrogram(
            Z=self.linkage_matrix, 
            no_plot=True,
            **default_kwargs
        )
        self.set_dendrogram(dd)
    
    def get_points(self):

        if self.points is None:

            #instantiate a dendrogram if one is not set yet
            if self.icoord is None:
                self.set_default_dendrogram()
            
            component_ids = zip(self.linkage_matrix[:,0].astype(int), self.linkage_matrix[:, 1].astype(int))
            merged_ids = np.arange(self.linkage_matrix.shape[0] + 1, (self.linkage_matrix.shape[0] + 1) * 2 - 1)
            id_dict = dict(zip(component_ids, merged_ids))

            leaders, flat_cluster_ids = self.get_leaders()
            
            xpos = self.get_ordered_leaf_positions()
            ypos = np.zeros(xpos.shape)

            point_dict = {}
            for coords, leaf_id, color in zip(zip(xpos, ypos), self.leaves, self.leaves_color_list):
                point_dict[coords] = {
                    'id': leaf_id,
                    'color': color,
                    'type': 'leaf',
                    'cluster_id': None
                } 
            
            for x, y, color in zip(self.icoord, self.dcoord, self.link_colors):
                left_coords = (x[0], y[0])
                right_coords = (x[3], y[3])
                right_leaf = point_dict[right_coords]
                left_leaf = point_dict[left_coords]
                merged_id = id_dict[(left_leaf['id'], right_leaf['id'])]

                cluster_id = None
                if merged_id in leaders:
                    type = 'cluster'
                    cluster_id = flat_cluster_ids[leaders == merged_id][0]
                elif right_leaf['type'] in ['leaf', 'subcluster'] and left_leaf['type'] in ['leaf', 'subcluster']:
                    type = 'subcluster'
                else:
                    type = 'supercluster'

                merged_coords = (x[1] + (x[2] - x[1]) / 2.0, y[2])
                point_dict[merged_coords] = {
                    'id': merged_id,
                    'color': color,
                    'type': type,
                    'cluster_id':  cluster_id,
                }   

            self.points = point_dict 

        return point_dict 

    def get_ordered_leaf_positions(self) -> np.ndarray: 
        "Finds the X-coordinate of the leafs in a dendrogram (Y-coordinate is zero)"
        X = self.icoord.flatten()
        Y = self.dcoord.flatten()
        return np.sort(X[Y == 0.0])