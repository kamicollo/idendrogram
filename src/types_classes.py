from dataclasses import dataclass, field
from typing import List, TypedDict, Protocol, Dict, Union

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
    size: float = 1.0


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


class ScipyDendrogram(TypedDict):
    color_list: List[str]
    icoord: List[List[float]]
    dcoord: List[List[float]]
    ivl: List[str]
    leaves: List[int]
    leaves_color_list: List[str]




class BaseProtocol(Protocol):
    def to_data(self) -> Dendrogram:
        pass
    