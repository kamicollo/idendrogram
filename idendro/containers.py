from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, TypedDict, Dict, Union


class ScipyDendrogram(TypedDict):
    """Data class storing data produced by scipy's dendrogram function"""

    color_list: List[str]
    icoord: List[List[float]]
    dcoord: List[List[float]]
    ivl: List[str]
    leaves: List[int]
    leaves_color_list: List[str]


@dataclass
class ClusterNode:
    """Dataclass storing information about nodes (non-singletons)

    x: X-coordinate of the node
    y: Y-coordinate of hte node
    id: Linkage ID the node represents
    cluster_id: flat cluster assignment ID if this link represents a flat cluster; otherwise empty
    edgecolor: color used for the edge of the node
    fillcolor: colors used to fill the node
    radius: radius of the node
    opacity: opacity level of the node
    label: text label displayed on the node
    labelsize: size of the text label displayed
    labelcolor: color of the text labed displayed
    hovertext: Information displayed on a tooltip, in dictionary form (key: values)
    _default_leaf_radius: size of the radius of the leaf nodes
    """

    x: float
    y: float
    type: str
    id: int
    cluster_id: Union[int, None]
    edgecolor: str
    label: str = ""
    hovertext: Dict[str, str] = field(default_factory=dict)
    fillcolor: str = "#fff"
    radius: float = 7.0
    opacity: float = 1.0
    labelsize: float = 10.0
    labelcolor: str = "#fff"
    _default_leaf_radius: float = 4.0


@dataclass
class ClusterLink:
    """Dataclass storing information about links

    x: 4 coordinates on the x-axis
    y: 4 coordinates on the y-axis
    id: the linkage ID represented by the link
    children_id: a tuple of 2 linkage IDs representing the 2 immediate clusters that got merged into this cluster
    cluster_id: flat cluster assignment ID if this link represents a flat cluster; otherwise empty
    fillcolor: line color used for the link
    strokewidth: the line width of the link
    strokedash: the dash pattern used for the link
    strokeopacity: the opacity level used for the link

    """

    x: List[float]
    y: List[float]
    fillcolor: str
    id: Union[int, None] = None
    children_id: Union[Tuple[int, int], None] = None
    cluster_id: Union[int, None] = None
    strokewidth: float = 1.0
    strokedash: List = field(default_factory=lambda: [1, 0])
    strokeopacity: float = 1.0
    _order_helper: List = field(default_factory=lambda: [0, 1, 2, 3])


@dataclass
class AxisLabel:
    """Dataclass storing information about axis labels

    x: x-coordinate of the label
    label: label text
    labelAngle: rotation of the text label (in degrees)
    """

    x: float
    label: str
    labelAngle: float = 0


@dataclass
class Dendrogram:
    """Dataclass representing the idendro dendrogram object

    axis_labels: list of AxisLabel objects
    links: list of ClusterLink objects
    nodes: list of ClusterNode objects
    computed_nodes: boolean indicating if Cluster Nodes were computed at creation time
    x_domain: the value domain of the label axis
    y_domain: the value domain of the value axis
    """

    axis_labels: List[AxisLabel]
    links: List[ClusterLink]
    nodes: List[ClusterNode]
    computed_nodes: bool = True
    x_domain: Tuple[float, float] = (0, 0)
    y_domain: Tuple[float, float] = (0, 0)

    def to_json(self) -> str:
        """Returns the dendrogram object represented as a JSON string

        Returns:
            str: JSON string
        """
        from .targets.json import JSONConverter

        return JSONConverter().convert(self)

    def check_orientation(
        self, orientation: str, supported: List = ["top", "bottom", "left", "right"]
    ) -> None:
        """Checks validity of orientation value provided"""
        if orientation not in supported:
            raise ValueError(
                f"""Orientation should be one of '{"', '".join(supported)}'. Provided: '{orientation}'"""
            )

    def check_scale(
        self, scale: str, supported: List[str] = ["linear", "log", "symlog"]
    ) -> None:
        """Checks validity of scale value provided"""
        if scale not in supported:
            raise ValueError(
                f"""Scale should be one of '{"', '".join(supported)}'. Provided: '{scale}'"""
            )

    def check_nodes(self, show_nodes: bool) -> None:
        """Checks if nodes were not computed but are requested to be drawn"""
        if show_nodes and not self.computed_nodes:
            raise RuntimeError(
                "Nodes were not computed in create_dendrogram() step, cannot show them"
            )

    def to_altair(
        self,
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 400,
        width: float = 400,
        scale: str = "linear",
    ) -> Any:
        """Converts a dendrogram object into Altair chart

        Args:
            orientation (str, optional): Position of dendrogram's root node. One of "top", "bottom", "left", "right". Defaults to "top".
            show_nodes (bool, optional): Whether to draw nodes. Defaults to True.
            height (float, optional): Height of the dendrogram. Defaults to 400.
            width (float, optional): Width of the dendrogram. Defaults to 400.
            scale (str, optional): Scale used for the value axis. One of "linear", "symlog", "log". Defaults to 'linear'.

        Returns:
            altair.LayeredChart: Altair chart object
        """
        self.check_orientation(orientation)
        self.check_scale(scale)
        self.check_nodes(show_nodes)

        from .targets.altair import AltairConverter

        return AltairConverter().convert(
            self,
            orientation=orientation,
            show_nodes=show_nodes,
            height=height,
            width=width,
            scale=scale,
        )

    def to_plotly(
        self,
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 400,
        width: float = 400,
        scale: str = "linear",
    ) -> Any:
        """Converts a dendrogram object into Plotly chart

        Args:
            orientation (str, optional): Position of dendrogram's root node. One of "top", "bottom", "left", "right". Defaults to "top".
            show_nodes (bool, optional): Whether to draw nodes. Defaults to True.
            height (float, optional): Height of the dendrogram. Defaults to 400.
            width (float, optional): Width of the dendrogram. Defaults to 400.
            scale (str, optional): Scale used for the value axis. One of "linear", "log". "symlog" is not supported by Plotly. Defaults to 'linear'.

        Returns:
            plotly.graph_objs.Figure: Plotly figure object
        """
        self.check_orientation(orientation)
        self.check_scale(scale, supported=["linear", "log"])
        self.check_nodes(show_nodes)

        from .targets.plotly import PlotlyConverter

        return PlotlyConverter().convert(
            self,
            orientation=orientation,
            show_nodes=show_nodes,
            height=height,
            width=width,
            scale=scale,
        )

    def to_matplotlib(
        self,
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 6,
        width: float = 6,
        scale: str = "linear",
    ) -> Any:
        """Converts a dendrogram object into matplotlib chart

        Args:
            orientation (str, optional): Position of dendrogram's root node. One of "top", "bottom", "left", "right". Defaults to "top".
            show_nodes (bool, optional): Whether to draw nodes. Defaults to True.
            height (float, optional): Height of the dendrogram. Defaults to 400.
            width (float, optional): Width of the dendrogram. Defaults to 400.
            scale (str, optional): Scale used for the value axis. One of "linear", "symlog", "log". Defaults to 'linear'.

        Returns:
            matplotlib.pyplot.ax: matplotlib axes object
        """
        self.check_orientation(orientation)
        self.check_scale(scale)
        self.check_nodes(show_nodes)

        from .targets.matplotlib import matplotlibConverter

        return matplotlibConverter().convert(
            self,
            orientation=orientation,
            show_nodes=show_nodes,
            height=height,
            width=width,
            scale=scale,
        )

    def to_streamlit(
        self,
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 400,
        width: float = 400,
        scale: str = "linear",
    ) -> Optional[ClusterNode]:
        """Renders dendrogram object as a custom bi-directional Streamlit component

        Args:
            orientation (str, optional): Position of dendrogram's root node. One of "top", "bottom", "left", "right". Defaults to "top".
            show_nodes (bool, optional): Whether to draw nodes. Defaults to True.
            height (float, optional): Height of the dendrogram. Defaults to 400.
            width (float, optional): Width of the dendrogram. Defaults to 400.
            scale (str, optional): Scale used for the value axis. One of "linear", "symlog", "log". Defaults to 'linear'.

        Returns:
            Optional[ClusterNode]: A ClusterNode object that was clicked on (None if no clicks took place)
        """

        self.check_orientation(orientation)
        self.check_scale(scale)
        self.check_nodes(show_nodes)

        from .targets.streamlit import StreamlitConverter

        return StreamlitConverter().convert(
            self,
            orientation=orientation,
            show_nodes=show_nodes,
            height=height,
            width=width,
            key="idendro",
            scale=scale,
        )
