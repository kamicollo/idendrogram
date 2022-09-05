import scipy.cluster.hierarchy as sch
import numpy as np

class ClusterConfig():
    def __init__(self, linkage_matrix, cluster_assignments, threshold) -> None:
        self.linkage_matrix = linkage_matrix
        self.cluster_assignments = cluster_assignments
        self.threshold = threshold
        self.leaves = None
    
    def show_only_cluster_labels(
        self, 
        fmt_string = "Cluster {cluster} ({cluster_size} data points)"
    ) -> callable:

        leaders, clusters = sch.leaders(self.linkage_matrix, self.cluster_assignments)
        _, nodelist = sch.to_tree(self.linkage_matrix, rd=True)
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
    
    def get_point_locations(self):

        #instantiate a dendrogram if one is not set yet
        if self.leaves is None:
            dd = sch.dendrogram(Z=self.linkage_matrix, truncate_mode='level', p=4, color_threshold=self.threshold, no_plot=True)
            self.set_dendrogram(dd)
        
        component_ids = zip(self.linkage_matrix[:,0].astype(int), self.linkage_matrix[:, 1].astype(int))
        merged_ids = np.arange(self.linkage_matrix.shape[0] + 1, (self.linkage_matrix.shape[0] + 1) * 2 - 1)
        id_dict = dict(zip(component_ids, merged_ids))
        
        xpos = self.get_ordered_leaf_positions()
        ypos = np.zeros(xpos.shape)

        point_coords = zip(xpos, ypos)
        point_dict = dict(zip(point_coords, self.leaves))
        
        for (x, y) in zip(self.icoord, self.dcoord):
            left_leaf = (x[0], y[0])
            right_leaf = (x[3], y[3])
            right_leaf_id = point_dict[right_leaf]
            left_leaf_id = point_dict[left_leaf]

            merged_point = (x[1] + (x[2] - x[1]) / 2.0, y[2])
            merged_id = id_dict[(left_leaf_id, right_leaf_id)]
            point_dict[merged_point] = merged_id   

        return point_dict 

    def get_ordered_leaf_positions(self) -> np.ndarray: 
        "Finds the X-coordinate of the leafs in a dendrogram (Y-coordinate is zero)"
        X = self.icoord.flatten()
        Y = self.dcoord.flatten()
        return np.sort(X[Y == 0.0])

        
