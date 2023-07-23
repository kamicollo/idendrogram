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

from . import callbacks

class idendrogram:
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
        """
        Initializes the idendrogram object, optionally with different formatting defaults.

        Args:

            link_factory (Callable[[Dict], ClusterLink]): [idendrogram.ClusterLink][] factory that can be used to override link formatting defaults.                 

            node_factory (Callable[[Dict], ClusterNode]): [idendrogram.ClusterNode][] factory that can be used to override node formatting defaults.                 

            axis_label_factory (Callable[[Dict], AxisLabel]): [idendrogram.AxisLabel][] factory that can be used to override axis label formatting defaults.                 

        Example:
        
            Customizing the Dendrogram to show smaller nodes and dashed link lines:

            ```python
            #define a subclass of `ClusterNode` and redefine radius and text label sizes
            @dataclass
            SmallClusterNode(ClusterNode):
                radius: 3
                labelsize: 3

            #define a subclass of `ClusterLink` and redefine stroke dash pattern
            @dataclass
            DashedLink(ClusterLink):
                strokedash: List = field(default_factory= lambda: [1, 5, 5, 1])

            #instantiate the idendrogram object with the factories for links and nodes
            dd = idendrogram.idendrogram(
                link_factory=lambda x: DashedLink(**x), 
                node_factory=lambda x: SmallClusterNode(**x)
            )

            #proceed as usual
            cdata = idendrogram.ClusteringData(
                linkage_matrix=model, 
                cluster_assignments=cluster_assignments, 
                threshold=threshold
            )
            dd.set_cluster_info(cdata)
            dendrogram = dd.create_dendrogram().to_altair()
            ```
        """
        
        self.link_factory = link_factory
        self.node_factory = node_factory
        self.axis_label_factory = axis_label_factory

    def _convert_matplotlib_color(self, c: str) -> str:
        """Used internally to map matplotlib colors to their values

        Args:
            c (str): Matplotlib color code 'CX'

        Returns:
            str: Hex of the color
        """
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

    def set_cluster_info(self, cluster_data: ClusteringData) -> None:
        """Sets the clustering data (linkage matrix and other parameters) that are required for some of the dendrogram generation features.

        Args:
            cluster_data (ClusteringData): instance of [idendrogram.ClusteringData][]

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
                threshold=threshold 
            )
            dd.set_cluster_info(cdata)
            ```
        """
        self.cluster_data = cluster_data
    
    def create_dendrogram(
        self,
        truncate_mode: str = "level",
        p: int = 4,
        sort_criteria: str = "distance",
        sort_descending: bool = False,
        link_color_func: Callable[[ClusteringData, int], str] = callbacks.link_painter(),
        leaf_label_func: Callable[[ClusteringData, int], str] = callbacks.counts,
        compute_nodes: bool = True,
        node_label_func: Callable[[ClusteringData, int], str] = callbacks.cluster_id_if_cluster,
        node_hover_func: Callable[[ClusteringData, int], Dict[str, str]] = callbacks.default_hover,
        
    ) -> Dendrogram:
        """Creates an idendrogram dendrogram object.

        Args:

            truncate_mode ('level' | 'lastp' | None): Truncation mode used to condense the dendrogram. 
                See [scipy's dendrogram()](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html) for details. 

            p (int): truncate_mode parameter.
                See [scipy's dendrogram()](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html) for details. 

            sort_criteria ('count' | 'distance'): Node order criteria. `count` sorts by number of original observations in the node, 
                `distance` by the distance between direct descendents of the node).             

            sort_descending (bool): Accompanying parameter to sort_criteria to indicate whether sorting should be descending.             
            link_color_func (Callable[[ClusteringData, int], str]): A callable function that determines colors of nodes and links. See below for details. 

            leaf_label_func (Callable[[ClusteringData, int], str]): A callable function that determines leaf node labels. See below for details. 

            compute_nodes (bool): Whether nodes should be computed (can be computationally expensive on large datasets). 

            node_label_func (Callable[[ClusteringData, int], str]): A callable function that determines node text labels. See below for details. 

            node_hover_func (Callable[[ClusteringData, int], Dict[str, str]], optional): A callable function that determines node hover text. See below for details. 

        Returns:
            Dendrogram: [idendrogram.Dendrogram] object

        
        ### Usage notes

        For how-to examples, see [How-to Guide](how-to-guides).
    

        #### SciPy's dendrogram parameters 

        idendrogram uses SciPy to generate the initial dendrogram structure and passes a few parameters directly to `scipy.cluster.hierarchy.dendrogram`:

        - `truncate_mode` and `p` are passed without modifications
        - `sort_criteria` and `sort_descending` map to `count_sort` and `distance_sort`
        - `leaf_color_func` and `leaf_label_func` are passed on with an additional wrapper that enables access to the linkage matrix (see below for details)

        To fully understand these parameters, it is easiest to explore [scipy's documentation directly](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html).

        #### Callback functions
        idendrogram uses callbacks to allow customizing link/node colors (`link_color_func`), leaf axis labels (`leaf_label_func`), 
            node labels (`node_label_func`) and tooltips (`node_hover_func`). All callback functions will be called with 2 parameters: 

        - an instance of [idendrogram.ClusteringData][] object that provides access to linkage matrix and other clustering information.
        - linkage ID (integer)

        The return types should be: 

        - `link_color_func` should return the color for the link/node represented by the linkage ID. 
        - `leaf_label_func` should return the text label to be used for the axis label of the leaf node represented by the linkage ID.
        - `node_label_func` should return the text label to be used for the node represented by the linkage ID. 
        - `node_hover_func` should return a dictionary of key:value pairs that will be displayed in a tooltip of the node represented by the linkage ID.

        This setup allows nearly endless customization - examples are provided in [How-to Guide](how-to-guides).

        """

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
            link_color_func=link_color_func,
        )

        return dendrogram
    
    def convert_scipy_dendrogram(
        self,
        R: ScipyDendrogram,
        compute_nodes: bool = True,
        node_label_func: Callable[[ClusteringData, int], str] = callbacks.cluster_id_if_cluster,
        node_hover_func: Callable[[ClusteringData, int], Dict[str, str]] = callbacks.default_hover,
        link_color_func: Callable[[ClusteringData, int], str] = callbacks.link_painter(),
    ) -> Dendrogram:
        """Converts a dictionary representing a dendrogram generated by SciPy to [idendrogram.Dendrogram][] object.

        Args:

            R (ScipyDendrogram): Dictionary as generated by SciPy's `dendrogram(..., no_plot=True)` or equivalent

            compute_nodes: Whether to compute nodes (requires [idendrogram.ClusteringData][] to be set via [idendrogram.idendrogram.set_cluster_info][] and can be computationally expensive on large datasets).            

            node_label_func (Callable[[], str], optional): Callback function to generate dendrogram node labels. See [idendrogram.idendrogram.create_dendrogram][] for usage details.

            node_hover_func (Callable[[], Union[Dict, str]], optional): Callback function to generate dendrogram hover text labels. See [idendrogram.idendrogram.create_dendrogram][] for usage details.

        Returns:
            Dendrogram: [idendrogram.Dendrogram] object

        Example:

            ```
            #your clustering workflow
            Z = scipy.cluster.hierarchy.linkage(*)
            threshold = 42
            cluster_assignments =  scipy.cluster.hierarchy.fcluster(Z, threshold=threshold, *)
            R = scipy.cluster.hierarchy.dendrogram(Z, no_plot=True, get_leaves=True, *)        

            #Render scipy's dendrogram in plotly without any additional modifications
            dd = idendrogram.idendrogram()        
            dendrogram = dd.convert_scipy_dendrogram(R, compute_nodes = False)
            dendrogram.to_plotly()

            ```

        """
        R["color_list"] = [self._convert_matplotlib_color(c) for c in R["color_list"]]
        R["leaves_color_list"] = [self._convert_matplotlib_color(c) for c in R["leaves_color_list"]]

        self._set_scipy_dendrogram(R)

        dendrogram = self._generate_dendrogram(
            compute_nodes=compute_nodes,
            node_label_func=node_label_func,
            node_hover_func=node_hover_func, 
            link_color_func= link_color_func           
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
                "Clustering data was not provided (idendrogram.set_cluster_info()), cannot generate dendrogram."
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
        node_hover_func: Callable[[ClusteringData, int], Dict[str, str]],
        link_color_func: Callable[[ClusteringData, int], str]
    ) -> Dendrogram:
        """Used internally to generate the dendrogram by calling internal functions. See create_dendrogram() for details
        """
        
        links = self._links()
        axis_labels = self._axis_labels()

        X_domain, Y_domain = self._domain_ranges()        
        
        nodes = self._nodes(
            links=links,
            node_label_func=node_label_func, 
            node_hover_func=node_hover_func,
            link_color_func = link_color_func
        ) if compute_nodes else []
        
        return Dendrogram(
            links=links, axis_labels=axis_labels, 
            nodes=nodes, computed_nodes=compute_nodes,
            x_domain = X_domain, y_domain = Y_domain
        )

    def _domain_ranges(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Used internally to obtain x/y domain ranges

        Returns:
            Tuple[Tuple[float, float], Tuple[float, float]]: X and Y domain ranges
        """
        return (
            (self.icoord.flatten().min(), self.icoord.flatten().max()),
            (self.dcoord.flatten().min(), self.dcoord.flatten().max())
        )

    def _links(self) -> List[ClusterLink]:
        """Generates link objects

        Returns:
            List[ClusterLink]: List of links
        """
        return [
            self.link_factory(dict(x=x, y=y, fillcolor=color))
            for x, y, color in zip(self.icoord.tolist(), self.dcoord.tolist(), self.link_colors)
        ]

    def _axis_labels(self) -> List[AxisLabel]:
        """Generates axis label objects

        Returns:
            List[AxisLabel]: List of axis labels
        """
        return [
            self.axis_label_factory(dict(label=l, x=x))
            for x, l in zip(self.leaf_positions, self.leaf_labels)
        ]

    def _nodes(
        self, 
        links: List[ClusterLink],
        node_label_func: Callable[[ClusteringData, int], str],
        node_hover_func: Callable[[ClusteringData, int], Dict[str, str]],
        link_color_func: Callable[[ClusteringData, int], str]
    ) -> List[ClusterNode]:
        """Used internally to generate node objects, apply node label and node hover functions

        Args:
            links (List[ClusterLink]): list of cluster links
            node_label_func (Callable[[ClusteringData, int], str]): callable for labeling nodes; see create_dendrogram() for details
            node_hover_func (Callable[[ClusteringData, int], Dict[str, str]]): callable for hover text; see create_dendrogram() for details

        Raises:
            RuntimeError: Raises a runtime error if underlying clustering data is not provided

        Returns:
            List[ClusterNode]: List of cluster node objects
        """

        self.node_dict = {}

        if self.cluster_data is None:
            raise RuntimeError(
                "Clustering data was not provided (idendrogram.set_cluster_info()), cannot compute nodes."
            )

        merge_map = self.cluster_data.get_merge_map()
        leaders, flat_cluster_ids = self.cluster_data.get_leaders()
        

        #first, create node objects for each leaf
        for xcoord, leaf_id, color in zip(
            self.leaf_positions, self.leaves, self.leaves_color_list
        ):

            p = self.node_factory(dict(
                x=xcoord,
                y=0,
                edgecolor=color if leaf_id not in leaders else link_color_func(self.cluster_data, leaf_id),
                fillcolor=color if leaf_id not in leaders else link_color_func(self.cluster_data, leaf_id),
                type="leaf" if leaf_id not in leaders else 'leaf-cluster',
                cluster_id= int(flat_cluster_ids[leaders == leaf_id][0]) if leaf_id in leaders else None,
                id=leaf_id
            ))

            p.radius = p._default_leaf_radius if p.type == 'leaf' else p._default_leaf_radius_if_cluster
            p.label = node_label_func(self.cluster_data, p.id)
            p.hovertext = node_hover_func(self.cluster_data, p.id)

            self.node_dict[(xcoord, 0)] = p

        #then, we traverse all the other links and associate them with leaves
        # this approach works because links in a scipy.dendrogram are generated in the same order as leaves and sequentially
        # so we can be always sure that a link has its "leafs" are present in our dictionary            

        for link in links:
            left_coords = (link.x[0], link.y[0])
            right_coords = (link.x[3], link.y[3])
            right_leaf = self.node_dict[right_coords]
            left_leaf = self.node_dict[left_coords]
            if (left_leaf.id, right_leaf.id) in merge_map:
                merged_id = int(merge_map[(left_leaf.id, right_leaf.id)])
            elif (right_leaf.id, left_leaf.id) in merge_map:
                merged_id = int(merge_map[(right_leaf.id, left_leaf.id)])
            else:
                raise LookupError("Link traversing failed - the linkage matrix is likely invalid")

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

    