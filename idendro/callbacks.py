from typing import Callable, Dict
from .clustering_data import ClusteringData


def counts(data: ClusteringData, linkage_id: int) -> str:
    _, nodelist = data.get_tree()
    return str(nodelist[linkage_id].get_count())


def default_hover(data: ClusteringData, linkage_id: int) -> Dict:
    return {
        "# of items": counts(data=data, linkage_id=linkage_id),
        "linkage_id": linkage_id,
    }


def cluster_labeller(
    fmt_string: str = "Cluster {cluster} ({cluster_size} data points)",
) -> Callable[[ClusteringData, int], str]:

    seen_clusters = []

    def labeller(data: ClusteringData, linkage_id: int) -> str:
        _, nodelist = data.get_tree()

        # grab first real leaf node of the passed id
        leaf_nodes = nodelist[linkage_id].pre_order(
            lambda x: x.id if x.is_leaf() else None
        )
        lf_node = leaf_nodes[0]

        # get its cluster assignment
        cluster = data.cluster_assignments[lf_node]

        if cluster not in seen_clusters:
            seen_clusters.append(cluster)
            # get cluster size
            cluster_size = nodelist[linkage_id].get_count()
            return fmt_string.format(
                cluster=cluster, cluster_size=cluster_size, id=linkage_id
            )
        else:
            return " "

    return labeller


def cluster_assignments(data: ClusteringData, linkage_id: int) -> str:
    L, M = data.get_leaders()
    if linkage_id in L:
        return str(M[L == linkage_id][0])
    else:
        return ""


def link_painter(
    colors: Dict[int, str] = {
        1: "#ff7f0e",
        2: "#2ca02c",
        3: "#d62728",
        4: "#9467bd",
        5: "#8c564b",
        6: "#e377c2",
        7: "#7f7f7f",
        8: "#bcbd22",
        9: "#17becf",
    },
    above_threshold: str = "#1f77b4",
) -> Callable[[ClusteringData, int], str]:
    def _get_color(cluster_assignment: int) -> str:
        if cluster_assignment in colors.keys():
            color = colors[cluster_assignment]
        else:
            color_index = cluster_assignment % len(colors)
            color = list(colors.values())[color_index]

        return color

    def link_colors(data: ClusteringData, linkage_id: int) -> str:

        L, M = data.get_leaders()

        # check if we are above leaders already
        if linkage_id > L.max():
            return above_threshold

        # check if this is a leader node
        if linkage_id in L:
            return _get_color(M[L == linkage_id][0])

        _, nodelist = data.get_tree()
        # Finally, if not grab first real leaf node of the passed id
        leaf_nodes = nodelist[linkage_id].pre_order(
            lambda x: x.id if x.is_leaf() else None
        )
        lf_node = leaf_nodes[0]
        # get its cluster assignment
        cluster = data.cluster_assignments[lf_node]
        return _get_color(cluster)

    return link_colors
