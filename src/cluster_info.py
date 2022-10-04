from typing import List, Tuple
import numpy as np
from scipy.cluster.hierarchy import leaders, to_tree, ClusterNode as CNode  # type: ignore


class ClusteringData:
    linkage_matrix: np.ndarray
    cluster_assignments: np.ndarray
    threshold: float
    have_leaders: bool = False
    leaders: np.ndarray
    flat_cluster_ids: np.ndarray
    have_tree: bool = False
    rootnode: CNode
    nodelist: List[CNode]

    def __init__(
        self,
        linkage_matrix: np.ndarray,
        cluster_assignments: np.ndarray,
        threshold: float,
        leaders: Tuple[np.ndarray, np.ndarray] = None,
        rootnode: CNode = None,
        nodelist: List[CNode] = None,
    ) -> None:
        """Set underlying clustering data that may be used by callback functions in generating the dendrogram. Ensures expensive operations are calculated only once.

        Args:
            linkage_matrix (np.ndarray): Linkage matrix as produced by scipy.cluster.hierarchy.linkage or equivalent
            cluster_assignments (np.ndarray): A one dimensional array of length N that contains flat cluster assignments for each observation. Produced by scipy.cluster.hierarchy.fcluster or equivalent.
            threshold (float): Cut-off threshold used to form flat clusters in the hierarchical clustering process or equivalent.
            leaders (Tuple[np.ndarray, np.ndarray], optional): Root nodes of the clustering produced by scipy.cluster.hierarchy.leaders(). 
            rootnode (CNode, optional): rootnode produced by scipy.cluster.hierarchy.to_tree(*, rd=True). 
            nodelist (List[CNode], optional): nodelist produced by scipy.cluster.hierarchy.to_tree(*, rd=True)
        """
        self.linkage_matrix = linkage_matrix
        self.cluster_assignments = cluster_assignments
        self.threshold = threshold
        if leaders is not None:
            self.have_leaders = True
            self.leaders = leaders[0]
            self.flat_cluster_ids = leaders[1]
        if rootnode and nodelist:
            self.have_tree = True
            self.rootnode = rootnode
            self.nodelist = nodelist

    def get_leaders(self) -> Tuple[np.ndarray, np.ndarray]:
        """A wrapper for scipy.cluster.hierarchy.leaders()

        Returns:
            Tuple[np.ndarray, np.ndarray]: [L, M]
        """
        if not self.have_leaders:
            L, M = leaders(
                self.linkage_matrix, self.cluster_assignments
            )
            self.leaders = L
            self.flat_cluster_ids = M
            self.have_leaders = True
        return self.leaders, self.flat_cluster_ids

    def get_tree(self) -> Tuple[CNode, List[CNode]]:
        """A wrapper for scipy.cluster.hierarchy.to_tree()

        Returns:
            Tuple[CNode, List[CNode]]: [rootnode, nodelist]
        """
        if not self.have_tree:
            rootnode, nodelist = to_tree(self.linkage_matrix, rd=True)
            self.rootnode = rootnode
            self.nodelist = nodelist
            self.have_tree = True
        return self.rootnode, self.nodelist

    def get_merge_map(self) -> dict:
        """Returns a dictionary that maps pairs of linkage matrix IDs (two clusters) to the linkage matrix ID (one cluster) they get merged into

        Returns:
            dict: Dictionary tuple(ID, ID): merged_ID
        """

        #create keys that are represented by the pairs of cluster_ids to be merged 
        #e.g. component_ids = [(1,2), (3,4), (5,6)]
        component_ids = zip(
            self.linkage_matrix[:, 0].astype(int),
            self.linkage_matrix[:, 1].astype(int),
        )
        #create IDs of the clusters resulting from the merges, i.e. if (1,2) get merged into 5 and (3,4) get merged into 6, 
        # and then (5,6) get merged into 7, this will be [5,6,7]
        merged_ids = np.arange(
            self.linkage_matrix.shape[0] + 1,
            (self.linkage_matrix.shape[0] + 1) * 2 - 1,
        )
        
        #create a dictionary that allows to look up a ID resulting from a merge
        merge_map = dict(zip(component_ids, merged_ids))
        return merge_map