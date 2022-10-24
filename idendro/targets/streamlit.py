import json
import os
from typing import Optional
import streamlit.components.v1 as components
from idendro.containers import ClusterNode, Dendrogram

class StreamlitConverter:
    def __init__(self, release = False) -> None:
        """Upon initialization, setup appropriate Streamlit component"""

        if not release:
            _component_func = components.declare_component(
                "idendro",
                url="http://localhost:3001",
            )
        else:
            parent_dir = os.path.dirname(os.path.abspath(__file__))
            build_dir = os.path.join(parent_dir, "frontend/build")
            _component_func = components.declare_component("idendro", path=build_dir)

        self.component_func = _component_func

    def convert(
        self,
        dendrogram: Dendrogram,
        orientation: str,
        show_nodes: bool,
        width: float,
        height: float,
        scale: str,
        key: Optional[str],
    ) -> Optional[ClusterNode]:
        """Renders the Streamlit component"""

        #ugly way to deal with streamlit not knowing how to serialize dataclasses
        dendrogram = json.loads(dendrogram.to_json()) 

        returned = self.component_func(
            dendrogram=dendrogram,
            orientation=orientation,
            show_nodes=show_nodes,
            width=width,
            height=height,
            key=key,
            default=None,
            scale=scale,
        )
        if returned is not None:
            return ClusterNode(**returned)
        else:
            return None
