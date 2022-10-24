from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, TypedDict, Dict, Union


class ScipyDendrogram(TypedDict):
    color_list: List[str]
    icoord: List[List[float]]
    dcoord: List[List[float]]
    ivl: List[str]
    leaves: List[int]
    leaves_color_list: List[str]


@dataclass
class ClusterNode:
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
    _default_leaf_radius: float = 4.
    


@dataclass
class ClusterLink:    
    x: List[float]
    y: List[float]
    fillcolor: str
    id: Union[int, None] = None
    children_id: Union[Tuple[int, int], None] = None
    cluster_id: Union[int, None] = None
    strokewidth: float = 1.0
    strokedash: List = field(default_factory=lambda: [1,0])
    strokeopacity: float = 1.0
    _order_helper: List = field(default_factory=lambda : [0,1,2,3])


@dataclass
class AxisLabel:
    x: float
    label: str
    labelAngle: float = 0

@dataclass
class Dendrogram:
    axis_labels: List[AxisLabel]
    links: List[ClusterLink]
    nodes: List[ClusterNode]
    computed_nodes: bool = True
    x_domain: Tuple[float, float] = (0,0)
    y_domain: Tuple[float, float] = (0,0)


    def to_json(self) -> str:
        """Returns a JSON form of the dendrogram

        Returns:
            str: JSON string
        """
        from .targets.json import JSONConverter
        
        return JSONConverter().convert(self)

    def to_altair(self, 
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 400,
        width: float = 400,
        scale = 'linear'
    ) -> Any:            
        from .targets.altair import AltairConverter        
        return AltairConverter().convert(self, orientation=orientation, show_nodes=show_nodes, height=height, width=width, scale=scale)

    def to_plotly(self, 
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 400,
        width: float = 400,
        scale = 'linear'
    ) -> Any:            
        from .targets.plotly import PlotlyConverter        
        return PlotlyConverter().convert(self, orientation=orientation, show_nodes=show_nodes, height=height, width=width, scale=scale)

    def to_matplotlib(self, 
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 400,
        width: float = 400,
        scale= 'linear'
    ) -> Any:            
        from .targets.matplotlib import matplotlibConverter        
        return matplotlibConverter().convert(self, orientation=orientation, show_nodes=show_nodes, height=height, width=width, scale=scale)

    def to_streamlit(self, 
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 400,
        width: float = 400,
        scale = 'linear',
        key: str = None) -> Optional[float]:
        from .targets.streamlit import StreamlitConverter
        return StreamlitConverter().convert(self, orientation=orientation, show_nodes=show_nodes, height=height, width=width, key=key, scale=scale)

    