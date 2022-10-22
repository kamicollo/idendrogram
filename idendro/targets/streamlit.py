import json
import os
from typing import Optional
import streamlit.components.v1 as components
from idendro.containers import ClusterNode, Dendrogram


_RELEASE = False

class StreamlitConverter:
    def __init__(self) -> None:
    
        if not _RELEASE:
            _component_func = components.declare_component(
                "idendro",
                url="http://localhost:3001",
            )
        else:
            parent_dir = os.path.dirname(os.path.abspath(__file__))
            build_dir = os.path.join(parent_dir, "frontend/build")
            _component_func = components.declare_component("idendro", path=build_dir)

        self.component_func = _component_func

    def convert(self,
        dendrogram: Dendrogram,
        orientation: str,
        show_nodes: bool,
        width: float,
        height: float,
        key: str = None) -> Optional[ClusterNode]:
        if show_nodes and not dendrogram.computed_nodes:
                raise RuntimeError("Nodes were not computed in create_dendrogram() step, cannot show them")  

        dendrogram = json.loads(dendrogram.to_json())
        
        returned = self.component_func(dendrogram=dendrogram, orientation=orientation, show_nodes=show_nodes, width=width, height=height, key=key, default=None)
        if returned is not None:
            return ClusterNode(**returned)
