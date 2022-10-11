from scipy.cluster.hierarchy import dendrogram # type: ignore
import numpy as np
import numpy.typing as npt

from typing import Callable, Dict, List, Tuple, Union
from .clustering_data import ClusteringData
from .containers import (
    ClusterLink,
    ClusterNode,
    Dendrogram,
    ScipyDendrogram,
    AxisLabel,
)
from .callbacks import cluster_assignments, counts, default_hover, link_painter

class IDendro:
    cluster_data: Union[ClusteringData, None]
    icoord: npt.NDArray[np.float32] = np.ndarray(0)
    dcoord: npt.NDArray[np.float32] = np.ndarray(0)
    link_colors: List[str] = []
    leaf_labels: List[str] = []
    leaf_positions: List[float] = []
    leaves: List[int] = []
    leaves_color_list: List[str] = []
    node_dict: Dict[Tuple[float, float], ClusterNode] = {}    
    link_factory: Callable[[Dict], ClusterLink]
    node_factory: Callable[[Dict], ClusterNode]
    axis_label_factory: Callable[[Dict], AxisLabel]

    def __init__(
        self,        
        link_factory: Callable[[Dict], ClusterLink] = lambda x: ClusterLink(**x),
        node_factory: Callable[[Dict], ClusterNode] = lambda x: ClusterNode(**x),
        axis_label_factory: Callable[[Dict], AxisLabel] = lambda x: AxisLabel(**x)
    ) -> None:
        
        self.link_factory = link_factory
        self.node_factory = node_factory
        self.axis_label_factory = axis_label_factory

    def convert_matplotlib_color(self, c: str) -> str:
        index = int(c[1])
        _matplotlib_colors = {
            0 : '#1f77b4',
            1 : '#ff7f0e',
            2 : '#2ca02c',
            3 : '#d62728',
            4 : '#9467bd',
            5 : '#8c564b',
            6 : '#e377c2',
            7 : '#7f7f7f',
            8 : '#bcbd22',
            9 : '#17becf'
        }
        return _matplotlib_colors[index]

    def convert_scipy_dendrogram(
        self,
        R: ScipyDendrogram,
        compute_nodes: bool = True,
        node_label_func: Callable[[ClusteringData, int], str] = cluster_assignments,
        node_hover_func: Callable[[ClusteringData, int], Dict[str, str]] = default_hover,
    ) -> Dendrogram:
        """Converts a dictionary representing a dendrogram generated by SciPy to Idendro dendrogram object

        Args:
            R (ScipyDendrogram): Dictionary as generated by scipy.cluster.hierarchy.dendrogram(*, no_plot=True) or equivalent
            node_label_func (Callable[[], str], optional): Callback function to generate dendrogram node labels. See create_dendrogram() for usage details.
            node_hover_func (Callable[[], Union[Dict, str]], optional): Callback function to generate dendrogram hover text labels. See create_dendrogram() for usage details.

        Returns:
            Dendrogram: Idendro dendrogram object
        """
        R["color_list"] = [self.convert_matplotlib_color(c) for c in R["color_list"]]
        R["leaves_color_list"] = [self.convert_matplotlib_color(c) for c in R["leaves_color_list"]]

        self._set_scipy_dendrogram(R)

        dendrogram = self._generate_dendrogram(
            compute_nodes=compute_nodes,
            node_label_func=node_label_func,
            node_hover_func=node_hover_func,
        )

        return dendrogram

    def set_cluster_info(self, cluster_data: ClusteringData) -> None:          
        self.cluster_data = cluster_data     

    def create_dendrogram(
        self,
        truncate_mode: str = "level",
        p: int = 4,
        sort_criteria: str = "distance",
        sort_descending: bool = False,
        link_color_func: Callable[[ClusteringData, int], str] = link_painter(),
        leaf_label_func: Callable[[ClusteringData, int], str] = counts,
        compute_nodes: bool = True,
        node_label_func: Callable[[ClusteringData, int], str] = cluster_assignments,
        node_hover_func: Callable[[ClusteringData, int], Dict[str, str]] = default_hover,
        
    ) -> Dendrogram:        

        # if we don't have a scipy dendrogram yet, create one
        if self.icoord.shape[0] == 0:            
            R = self._create_scipy_dendrogram(
                truncate_mode=truncate_mode,
                p=p,
                sort_criteria=sort_criteria,
                sort_descending=sort_descending,
                link_color_func=link_color_func,
                leaf_label_func=leaf_label_func,
            )
            self._set_scipy_dendrogram(R)

        # proceed to create a dendrogram object
        dendrogram = self._generate_dendrogram(
            compute_nodes=compute_nodes,
            node_label_func=node_label_func,
            node_hover_func=node_hover_func,
        )

        return dendrogram

    def _set_scipy_dendrogram(self, R: ScipyDendrogram) -> None:
        """Validates and sets SciPy-format dendrogram.

        Args:
            R (ScipyDendrogram): SciPy-format dendrogram

        Raises:
            AttributeError: if the dictionary is not of SciPy format
        """
        required_keys = [
            "icoord",
            "dcoord",
            "color_list",
            "ivl",
            "leaves",
            "leaves_color_list",
        ]

        missing_keys = set(required_keys).difference(set(R.keys()))
        if missing_keys:
            raise AttributeError(
                "SciPy Dendrogram passed is missing keys '{}'".format(
                    ", ".join(missing_keys)
                )
            )

        self.icoord = np.array(R["icoord"])
        self.dcoord = np.array(R["dcoord"])
        self.link_colors = R["color_list"]
        self.leaf_labels = R["ivl"]
        self.leaves = R["leaves"]
        self.leaves_color_list = R["leaves_color_list"]

        X = self.icoord.flatten()
        Y = self.dcoord.flatten()
        self.leaf_positions = np.sort(X[Y == 0.0]).tolist()

    def _create_scipy_dendrogram(
        self,
        truncate_mode: str,
        p: int,
        sort_criteria: str,
        sort_descending: bool,
        link_color_func: Callable[[ClusteringData, int], str],
        leaf_label_func: Callable[[ClusteringData, int], str],
    ) -> ScipyDendrogram:
        """Uses SciPy to generate a dendrogram object

        Args:
            truncate_mode ('str'): truncate mode that takes values 'lastp', 'level' or None. Refer to create_dendrogram() for details.
            p (int): criterion for truncate mode. Refer to create_dendrogram() for details
            sort_criteria (str): sort criteria that takes values 'count' or 'distance'. Refer to create_dendrogram() for details.
            sort_descending (bool): sort direction. 
            link_color_func (Callable[[int], str]): callback function to generate link and node colors. Refer to create_dendrogram() for details.
            leaf_label_func (Callable[[int], str]): callback function to generate leaf labels. Refer to create_dendrogram() for details.

        Returns:
            ScipyDendrogram: SciPy-format dendrogram dictionary
        """

        if self.cluster_data is None:
            raise RuntimeError(
                "Clustering data was not provided (idendro.set_cluster_info()), cannot generate dendrogram."
            )

        
        wrapper_link_color_func = lambda x: link_color_func(self.cluster_data, x)        
        wrapper_leaf_label_func = lambda x: leaf_label_func(self.cluster_data, x)
        

        kwargs = dict(    
            Z=self.cluster_data.linkage_matrix,
            truncate_mode=truncate_mode,
            p=p,
            link_color_func=wrapper_link_color_func,
            leaf_label_func=wrapper_leaf_label_func,            
            no_plot=True,
        )

        # translate sort arguments to scipy interface
        assert sort_criteria in ["distance", "count"], ValueError(
            "sort_criteria can be only 'distance' or 'count'"
        )
        if sort_criteria == "distance":
            kwargs['distance_sort'] = "descending" if sort_descending else "ascending"
            kwargs['count_sort'] = False            
        elif sort_criteria == "count":
            kwargs['count_sort'] = "descending" if sort_descending else "ascending"
            kwargs['distance_sort'] = False            

        # generate scipy dendrogram
        return dendrogram(**kwargs)


    def _generate_dendrogram(
        self,      
        compute_nodes: bool,  
        node_label_func: Callable[[ClusteringData, int], str],
        node_hover_func: Callable[[ClusteringData, int], Dict[str, str]]
    ) -> Dendrogram:
        
        links = self._links()
        axis_labels = self._axis_labels()

        X_domain, Y_domain = self._domain_ranges()

        
        nodes = self._nodes(
            links=links,
            node_label_func=node_label_func, node_hover_func=node_hover_func
        ) if compute_nodes else []
        
        return Dendrogram(
            links=links, axis_labels=axis_labels, 
            nodes=nodes, computed_nodes=compute_nodes,
            x_domain = X_domain, y_domain = Y_domain
        )

    def _domain_ranges(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return (
            (self.icoord.flatten().min(), self.icoord.flatten().max()),
            (self.dcoord.flatten().min(), self.dcoord.flatten().max())
        )

    def _links(self) -> List[ClusterLink]:
        return [
            self.link_factory(dict(x=x, y=y, fillcolor=color))
            for x, y, color in zip(self.icoord.tolist(), self.dcoord.tolist(), self.link_colors)
        ]

    def _axis_labels(self) -> List[AxisLabel]:
        return [
            self.axis_label_factory(dict(label=l, x=x))
            for x, l in zip(self.leaf_positions, self.leaf_labels)
        ]

    def _nodes(
        self, 
        links: List[ClusterLink],
        node_label_func: Callable[[ClusteringData, int], str],
        node_hover_func: Callable[[ClusteringData, int], Dict[str, str]]
    ) -> List[ClusterNode]:

        if not self.node_dict:

            if self.cluster_data is None:
                raise RuntimeError(
                    "Clustering data was not provided (idendro.set_cluster_info()), cannot compute nodes."
                )


            #first, create node objects for each leaf
            for xcoord, leaf_id, color in zip(
                self.leaf_positions, self.leaves, self.leaves_color_list
            ):

                p = self.node_factory(dict(
                    x=xcoord,
                    y=0,
                    edgecolor=color,
                    fillcolor=color,
                    radius=4.,
                    type="leaf",
                    cluster_id=None,
                    id=leaf_id
                ))

                p.label = node_label_func(self.cluster_data, p.id)
                p.hovertext = node_hover_func(self.cluster_data, p.id)

                self.node_dict[(xcoord, 0)] = p

            #then, we traverse all the other links and associate them with leaves
            # this approach works because links in a scipy.dendrogram are generated in the same order as leaves and sequentially
            # so we can be always sure that a link has its "leafs" are present in our dictionary
            merge_map = self.cluster_data.get_merge_map()
            leaders, flat_cluster_ids = self.cluster_data.get_leaders()

            for link in links:
                left_coords = (link.x[0], link.y[0])
                right_coords = (link.x[3], link.y[3])
                right_leaf = self.node_dict[right_coords]
                left_leaf = self.node_dict[left_coords]
                merged_id = int(merge_map[(left_leaf.id, right_leaf.id)])

                cluster_id = None
                if merged_id in leaders:
                    node_type = "cluster"
                    cluster_id = int(flat_cluster_ids[leaders == merged_id][0])
                elif right_leaf.type in ["leaf", "subcluster"] and left_leaf.type in ["leaf", "subcluster"]:
                    node_type = "subcluster"
                else:
                    node_type = "supercluster"

                merged_coords = (float(link.x[1] + (link.x[2] - link.x[1]) / 2.0), float(link.y[2]))

                p = self.node_factory(dict(
                    x=merged_coords[0],
                    y=merged_coords[1],
                    edgecolor=link.fillcolor,                    
                    type=node_type,
                    cluster_id=cluster_id,
                    id=merged_id
                ))

                if node_type != 'subcluster':
                    p.fillcolor = link.fillcolor

                p.label = node_label_func(self.cluster_data, p.id)
                p.hovertext = node_hover_func(self.cluster_data, p.id)

                #update link with info
                link.id = merged_id
                link.cluster_id = cluster_id
                link.children_id = (left_leaf.id, right_leaf.id)
                

                self.node_dict[merged_coords] = p        

        return list(self.node_dict.values())

    