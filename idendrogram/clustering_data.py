from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np
import scipy.cluster.hierarchy as sch # type: ignore
import scipy # type: ignore

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sklearn #type: ignore
    import hdbscan #type: ignore


class ClusteringData:
    """This class is used as a container to store underlying clustering data which may be used by callback functions 
        in generating the dendrogram. Ensures expensive operations are calculated only once.  

        Example:

            ```
            #your clustering workflow
            Z = scipy.cluster.hierarchy.linkage(...)
            threshold = 42
            cluster_assignments =  scipy.cluster.hierarchy.fcluster(Z, threshold=threshold, ...)        

            #dendrogram creation
            dd = idendrogram.idendrogram()
            cdata = idendrogram.ClusteringData(
                linkage_matrix=Z, 
                cluster_assignments=cluster_assignments                
            )
            dd.set_cluster_info(cdata)
            ```        
        """

    have_leaders: bool = False
    leaders: np.ndarray
    flat_cluster_ids: np.ndarray
    have_tree: bool = False
    rootnode: sch.ClusterNode      
    nodelist: List[sch.ClusterNode]    
    linkage_matrix: np.ndarray     
    cluster_assignments: np.ndarray


    def __init__(
        self,
        linkage_matrix: np.ndarray,
        cluster_assignments: np.ndarray,        
        leaders: Tuple[np.ndarray, np.ndarray] = None,
        rootnode: sch.ClusterNode = None,
        nodelist: List[sch.ClusterNode] = None,
    ) -> None:
        """Set underlying clustering data that may be used by callback functions in generating the dendrogram. Ensures expensive operations are calculated only once.

        Args:
            linkage_matrix (np.ndarray): Linkage matrix as produced by 
                `scipy.cluster.hierarchy.linkage` or equivalent
            cluster_assignments (np.ndarray): A one dimensional array of length N that contains flat cluster assignments for each observation. Produced by `scipy.cluster.hierarchy.fcluster` or equivalent.            
            leaders (Tuple[np.ndarray, np.ndarray], optional): Root nodes of the clustering produced by `scipy.cluster.hierarchy.leaders()`. 
            rootnode (sch.ClusterNode, optional): rootnode produced by `scipy.cluster.hierarchy.to_tree(..., rd=True)`. 
            nodelist (List[sch.ClusterNode], optional): nodelist produced by `scipy.cluster.hierarchy.to_tree(..., rd=True)`

        Example:

            ```
            #your clustering workflow
            Z = scipy.cluster.hierarchy.linkage(...)
            threshold = 42
            cluster_assignments =  scipy.cluster.hierarchy.fcluster(Z, threshold=threshold, ...)        

            #dendrogram creation
            dd = idendrogram.idendrogram()
            cdata = idendrogram.ClusteringData(
                linkage_matrix=Z, 
                cluster_assignments=cluster_assignments,                 
            )
            dd.set_cluster_info(cdata)
            ```            
        """
        self.linkage_matrix = linkage_matrix
        self.cluster_assignments = cluster_assignments        
        if leaders is not None:
            self.have_leaders = True
            self.leaders = leaders[0]
            self.flat_cluster_ids = leaders[1]
        if rootnode and nodelist:
            self.have_tree = True
            self.rootnode = rootnode
            self.nodelist = nodelist

    def get_leaders(self) -> Tuple[np.ndarray, np.ndarray]:
        """A wrapper for [scipy.cluster.hierarchy.leaders](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.leaders.html). Returns the root nodes in a hierarchical clustering.

        Returns:
            (Tuple[np.ndarray, np.ndarray]):  [L, M] (see SciPy's documentation for details)
        """
        if not self.have_leaders:
            L, M = sch.leaders(
                self.linkage_matrix, self.cluster_assignments
            )
            self.leaders = L
            self.flat_cluster_ids = M
            self.have_leaders = True
        return self.leaders, self.flat_cluster_ids

    def get_linkage_matrix(self) -> np.ndarray:
        """Returns stored linkage matrix.
        Returns:
            linkage_matrix (np.ndarray): Linkage matrix as produced by scipy.cluster.hierarchy.linkage or equivalent.
        """
        return self.linkage_matrix    

    def get_cluster_assignments(self) -> np.ndarray:
        """Returns flat cluster assignment array.

        Returns:
            cluster_assignments (np.ndarray): A one dimensional array of length N that contains flat cluster assignments for each observation. Produced by `scipy.cluster.hierarchy.fcluster` or equivalent.
        """
        return self.cluster_assignments
    
    def get_cluster_id(self, linkage_id: int) -> Optional[int]:
        """Returns flat cluster ID for a given linkage ID

        Args:
            linkage_id (int): Node linkage ID

        Returns:
            Optional[int]: CLuster ID if a node is within one cluster; None otherwise.
        """
        L, M = self.get_leaders()

        # check if we are above leaders already
        if linkage_id > L.max():
            return None

    # check if this is a leader node
        if linkage_id in L:
            return M[L == linkage_id][0]

        _, nodelist = self.get_tree()
        # Finally, if not grab first real leaf node of the passed id
        leaf_nodes = nodelist[linkage_id].pre_order(
            lambda x: x.id if x.is_leaf() else None
        )
        lf_node = leaf_nodes[0]
        # get its cluster assignment
        cluster = self.cluster_assignments[lf_node]
        return cluster

    def get_tree(self) -> Tuple[sch.ClusterNode, List[sch.ClusterNode]]:
        """A wrapper for [scipy.cluster.hierarchy.to_tree](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.to_tree.html). Converts a linkage matrix into an easy-to-use tree object.

        Returns:
            Tuple[scipy.cluster.hierarchy.ClusterNode, List[scipy.cluster.hierarchy.ClusterNode]]: [rootnode, nodelist] (see SciPy's documentation for details)
        """
        if not self.have_tree:
            rootnode, nodelist = sch.to_tree(self.linkage_matrix, rd=True)
            self.rootnode = rootnode
            self.nodelist = nodelist
            self.have_tree = True
        return self.rootnode, self.nodelist

    def get_merge_map(self) -> dict:
        """Returns a dictionary that maps pairs of linkage matrix IDs to the linkage matrix ID they get merged into.

        Returns:
            dict: Dictionary tuple(ID, ID) -> merged_ID
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
    
class ScikitLearnClusteringData(ClusteringData):

    model: sklearn.cluster.AgglomerativeClustering

    def __init__(self, model: sklearn.cluster.AgglomerativeClustering) -> None:

        self.model = model

        # create the counts of samples under each node
        counts = np.zeros(model.children_.shape[0])
        n_samples = len(model.labels_)

        for i, merge in enumerate(model.children_):
            current_count = 0
            for child_idx in merge:
                if child_idx < n_samples:
                    current_count += 1  # leaf node
                else:
                    current_count += counts[child_idx - n_samples]
            counts[i] = current_count

        linkage_matrix = np.column_stack(
            [model.children_, model.distances_, counts]
        ).astype(float)

        super().__init__(linkage_matrix, model.labels_.astype('int32'))

    def get_model(self)-> sklearn.cluster.AgglomerativeClustering:
        return self.model

class HDBSCANClusteringData(ClusteringData):

    model: hdbscan.HDBSCAN

    def __init__(self, model: hdbscan.HDBSCAN) -> None:

        linkage_matrix = model.single_linkage_tree_.to_numpy()
        flat_clusters = model.labels_.astype('int32')
        self.model = model

        super().__init__(linkage_matrix=linkage_matrix, cluster_assignments=flat_clusters)

    def get_model(self) -> hdbscan.HDBSCAN:
        return self.model