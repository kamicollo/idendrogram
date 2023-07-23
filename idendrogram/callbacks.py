from typing import Callable, Dict
from .clustering_data import ClusteringData


def counts(data: ClusteringData, linkage_id: int) -> str:
    """Returns the number of original observations associated with the linkage ID. Used as the default for axis label callback.

    Args:
        data (ClusteringData): [idendrogram.ClusteringData][] object
        linkage_id (int): linkage ID

    Returns:
        str: number of original observations (as string)
    """
    _, nodelist = data.get_tree()
    return str(nodelist[linkage_id].get_count())


def default_hover(data: ClusteringData, linkage_id: int) -> Dict:
    """For a given linkage ID, returns a dictionary with two keys: linkage id and # of items. Used as the default for tooltips.


    Args:
        data (ClusteringData): [idendrogram.ClusteringData][] object
        linkage_id (int): linkage ID

    Returns:
        Dict: Dictionary with attributes
    """
    return {
        "# of items": counts(data=data, linkage_id=linkage_id),
        "linkage id": linkage_id,
    }


def cluster_labeller(
    fmt_string: str = "Cluster {cluster} ({cluster_size} data points)",
) -> Callable[[ClusteringData, int], str]:
    """Returns a callable designed to be used as a callback to `axis_label_func` parameter of [idendrogram.idendrogram.create_dendrogram][]. 
    Returns a formatted string for the first encountered node in a cluster, otherwise an empty string.

    Args:
        fmt_string (str, optional): Formatting string. Variables available at the time of evaluation are `cluster`, `cluster_size` and `linkage_id`.

    Returns:
        Callable[[ClusteringData, int], str]: Callable designed to be used as a callback to to `axis_label_func` parameter of [idendrogram.idendrogram.create_dendrogram][].
    """

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


def cluster_id_if_cluster(data: ClusteringData, linkage_id: int) -> str:
    """Returns cluster ID if a node belongs to one cluster, otherwise an empty string.

    Args:
        data (ClusteringData): [idendrogram.ClusteringData][] object
        linkage_id (int): linkage ID

    Returns:
        str: Cluster ID or empty string.
    """
    L, M = data.get_leaders()
    if linkage_id in L:
        return str(M[L == linkage_id][0])
    else:
        return ""


def link_painter(
    colors: Dict[int, str] = dict(),
    above_threshold: str = "#1f77b4",
) -> Callable[[ClusteringData, int], str]:
    """Creates a callable compatible with `link_color_func` argument of [idendrogram.idendrogram][] 
        that will color nodes based on the cluster they belong to, with a separate color for nodes containing multiple clusters. 

    Args:
        colors (Dict, optional): Dictionary mapping cluster IDs to colors. Defaults to Matplotlib 10-color scheme.
        above_threshold (str, optional): Color to be used for nodes containing multiple clusters.

    Returns:
        Callable[[ClusteringData, int], str]: Callable to be used as `link_color_func` argument of [idendrogram.idendrogram][].

    Example:
        ```
            #your clustering workflow
            Z = scipy.cluster.hierarchy.linkage(...)
            cluster_assignments =  scipy.cluster.hierarchy.fcluster(Z, threshold=threshold, ...) 
            
            # let's assume clustering resulted in 3 clusters and we want to have them as red/blue/green
            # cluster_assignments.unique == 3

            # define a custom coloring function
            painter = idendrogram.callbacks.link_painter(
                colors={
                    1: 'red',
                    2: 'blue',
                    3: 'green',
                }, 
                above_threshold='black'
            )

            #create the dendrogram
            dd = idendrogram.idendrogram()            
            dd.set_cluster_info(
                idendrogram.ClusteringData(
                    linkage_matrix=Z, 
                    cluster_assignments=cluster_assignments, 
                    threshold=threshold 
                )
            )
            dd.create_dendrogram(link_color_func = painter).to_plotly()
        ```
    """
    if len(colors) == 0:
        colors = {
            1: "#ff7f0e",
            2: "#2ca02c",
            3: "#d62728",
            4: "#9467bd",
            5: "#8c564b",
            6: "#e377c2",
            7: "#7f7f7f",
            8: "#bcbd22",
            9: "#17becf",
        }
    def _get_color(cluster_assignment: int) -> str:
        if cluster_assignment in colors.keys():
            color = colors[cluster_assignment]
        else:
            color_index = cluster_assignment % len(colors)
            color = list(colors.values())[color_index]

        return color

    def link_colors(data: ClusteringData, linkage_id: int) -> str:

        cluster_id = data.get_cluster_id(linkage_id=linkage_id)
        if cluster_id is None:
            return above_threshold
        else:
            return _get_color(cluster_id)

    return link_colors

def cluster_assignments(data: ClusteringData, linkage_id: int) -> str:
    cluster_id = data.get_cluster_id(linkage_id=linkage_id)
    if cluster_id is None:
        return "multiple clusters"
    else:
        return f"Cluster {cluster_id}"
