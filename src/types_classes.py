from dataclasses import dataclass, field
from typing import List, Tuple, TypedDict, Dict, Union


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
    fillcolor: str = "fff"    
    radius: float = 7.0
    labelsize: float = 10.0
    labelcolor: str = "fff"
    


@dataclass
class ClusterLink:    
    x: List[float]
    y: List[float]
    fillcolor: str
    id: Union[int, None] = None
    children_id: Union[Tuple[int, int], None] = None
    cluster_id: Union[int, None] = None
    strokewidth: float = 1.0
    strokedash: List = field(default_factory=lambda: [1,1])
    strokeopacity: float = 1.0
    _order_helper: List = field(default_factory=lambda : [0,1,2,3])


@dataclass
class AxisLabel:
    x: float
    label: str
    labelsize: float = 8.0


@dataclass
class Dendrogram:
    axis_labels: List[AxisLabel]
    links: List[ClusterLink]
    nodes: List[ClusterNode]

    def to_json(self) -> str:
        """Returns a JSON form of the dendrogram

        Returns:
            str: JSON string
        """
        from .targets.json import JSONConverter
        
        return JSONConverter().convert(self)

    def to_altair(self, 
        orientation: str = "top",
        show_points: bool = True
    ):
        
        from .targets.altair import AltairConverter
        
        return AltairConverter().convert(self, orientation, show_points)

    