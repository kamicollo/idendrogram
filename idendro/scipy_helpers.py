import scipy.cluster.hierarchy as sch

class ClusterConfig():
    def __init__(self, linkage_matrix, cluster_assignments, threshold) -> None:
        self.linkage_matrix = linkage_matrix
        self.cluster_assignments = cluster_assignments
        self.threshold = threshold
    

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