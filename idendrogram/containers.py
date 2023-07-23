from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, TypedDict, Dict, Union


class ScipyDendrogram(TypedDict):
    """Data class storing data produced by scipy's dendrogram function."""

    color_list: List[str]
    """List of link colors"""
    icoord: List[List[float]]
    """List of lists of X-coordinates of links"""
    dcoord: List[List[float]]
    """List of lists of Y-coordinates of links"""
    ivl: List[str]
    """List of leaf labels"""
    leaves: List[int]
    """List of leave IDs"""
    leaves_color_list: List[str]
    """List of leave colors"""


@dataclass
class ClusterNode:
    """Data class storing node-level information."""

    x: float
    """X-coordinate of the node"""
    y: float
    """Y-coordinate of the node"""
    type: str
    """Type of the node. One of `leaf`, `subcluster`, `cluster`, `supercluster` """
    id: int
    """Linkage ID the node represents"""
    cluster_id: Union[int, None]
    """flat cluster assignment ID if this link represents a flat cluster; otherwise empty"""
    edgecolor: str
    """color used for the edge of the node"""
    label: str = ""
    """text label displayed on the node"""
    hovertext: Dict[str, str] = field(default_factory=dict)
    """Information displayed on a tooltip, in dictionary form (key: values)"""
    fillcolor: str = "#fff"
    """colors used to fill the node"""
    radius: float = 7.0
    """radius of the node"""
    opacity: float = 1.0
    """opacity level of the node"""
    labelsize: float = 10.0
    """size of the text label displayed"""
    labelcolor: str = "#fff"
    """color of the text label displayed"""
    _default_leaf_radius: float = 4.0
    """size of the radius of the leaf nodes"""
    _default_leaf_radius_if_cluster: float = 7.0
    """size of the radius of the leaf nodes"""



@dataclass
class ClusterLink:
    """Dataclass storing information about links."""

    x: List[float]
    """x: 4 coordinates of the link on the x-axis"""
    y: List[float]
    """y: 4 coordinates of the link on the y-axis"""
    fillcolor: str
    """fillcolor: line color used for the link"""
    id: Union[int, None] = None
    """id: the linkage ID represented by the link"""
    children_id: Union[Tuple[int, int], None] = None
    """children_id: a tuple of 2 linkage IDs representing the 2 immediate clusters that got merged into this cluster"""
    cluster_id: Union[int, None] = None
    """cluster_id: flat cluster assignment ID if this link represents a flat cluster; otherwise empty"""
    strokewidth: float = 1.0
    """strokewidth: the line width of the link"""
    strokedash: List = field(default_factory=lambda: [1, 0])
    """strokedash: the dash pattern used for the link"""
    strokeopacity: float = 1.0
    """strokeopacity: the opacity level used for the link"""
    _order_helper: List = field(default_factory=lambda: [0, 1, 2, 3])


@dataclass
class AxisLabel:
    """Dataclass storing information on axis labels."""

    x: float
    """x-coordinate of the label"""
    label: str
    """label text"""
    labelAngle: float = 0
    """rotation of the text label (in degrees)"""

@dataclass
class Dendrogram:
    """Dataclass representing the idendrogram dendrogram object.
    """

    axis_labels: List[AxisLabel]
    """axis_labels: list of AxisLabel objects"""
    links: List[ClusterLink]
    """links: list of ClusterLink objects"""
    nodes: List[ClusterNode]
    """nodes: list of ClusterNode objects"""
    computed_nodes: bool = True
    """computed_nodes: boolean indicating if Cluster Nodes were computed at creation time"""
    x_domain: Tuple[float, float] = (0, 0)
    """x_domain: the value domain of the label axis"""
    y_domain: Tuple[float, float] = (0, 0)
    """y_domain: the value domain of the value axis"""

    def plot(
        self,
        backend: str = "altair",
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 400,
        width: float = 400,
        scale: str = "linear",
    ) -> Any:
        """
        Plot the dendrogram using one of the supported backends. This is a convenience function,
            you can also use `to_*()` functions from appropriate target backends at `idendrogram.targets.[backend].to_[backend]()`.

        Args:
            backend (str, optional): Backend to use, one of 'altair', 'streamlit', 'plotly', 'matplotlib'. 
            orientation (str, optional): Position of dendrogram's root node. One of "top", "bottom", "left", "right". 
            show_nodes (bool, optional): Whether to draw nodes. 
            height (float, optional): Height of the dendrogram. 
            width (float, optional): Width of the dendrogram. 
            scale (str, optional): Scale used for the value axis. One of "linear", "symlog", "log". 

        Raises:
            ValueError: Parameters supplied did not comform to allowed values.  

        Returns:
            Any: 

                Varies by backend: 
                
                - Altair: `altair.Layered` chart object
                - Plotly: `plotly.graph_objs.Figure` figure object
                - Matplotlib: `matplotlib.pyplot.ax` axes object
                - Streamlit: [idendrogram.ClusterNode][] object that was clicked on (None if no clicks took place)
        """
        if backend == 'altair':
            from .targets.altair import to_altair
            return to_altair(self, orientation=orientation, show_nodes=show_nodes, height=height, width=width, scale=scale)
        elif backend == 'matplotlib':
            from .targets.matplotlib import to_matplotlib
            return to_matplotlib(self, orientation=orientation, show_nodes=show_nodes, height=height, width=width, scale=scale)
        elif backend == 'plotly':
            from .targets.plotly import to_plotly
            return to_plotly(self, orientation=orientation, show_nodes=show_nodes, height=height, width=width, scale=scale)
        elif backend == 'streamlit':
            from .targets.streamlit import to_streamlit
            return to_streamlit(self, orientation=orientation, show_nodes=show_nodes, height=height, width=width, scale=scale)
        else:
            raise ValueError(f"Unsupported backend '{backend}', should be one of 'plotly', 'matplotlib', 'altair', 'streamlit'")

    def to_json(self) -> str:
        """Converts dendrogram to JSON representation.

        Returns:
            str: JSON-formatted dendrogram
        """
        from .targets.json import to_json
        return to_json(self)