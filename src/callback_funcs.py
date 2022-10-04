def get_counts(self) -> callable:
    _, nodelist = self.get_tree()

    def labeller(id):
        return nodelist[id].get_count()

    return labeller

def show_only_cluster_labels(
    self, fmt_string="Cluster {cluster} ({cluster_size} data points)"
) -> callable:
    leaders, clusters = self.get_leaders()
    _, nodelist = self.get_tree()
    cluster_list = {}
    # for each leader ("cluster"), find the associated data points
    for l, c in zip(leaders, clusters):
        cluster_list[c] = nodelist[l].pre_order(lambda x: x.id)

    seen_clusters = []

    def labeller(id):
        # grab first real leaf node of the passed id
        leaf_nodes = nodelist[id].pre_order(lambda x: x.id if x.is_leaf() else None)
        lf_node = leaf_nodes[0]
        # traverse all leader nodes, checking if they have the leaf node
        for c, nodes in cluster_list.items():
            if lf_node in nodes:
                cluster = c
                cluster_size = len(nodes)
                break

        if cluster not in seen_clusters:
            seen_clusters.append(cluster)
            return fmt_string.format(
                cluster=cluster, cluster_size=cluster_size, id=id
            )
        else:
            return " "

    return labeller

def cluster_labels(x):
    return "" if x["type"] != "cluster" else x["cluster_id"]
        
