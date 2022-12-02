import json
import os
from typing import Optional
import streamlit.components.v1 as components
from idendro.containers import ClusterNode, Dendrogram
from .json import to_json

from .common import _check_nodes, _check_orientation, _check_scale


def to_streamlit(
    dendrogram: Dendrogram,
    orientation: str = "top",
    show_nodes: bool = True,
    height: float = 400,
    width: float = 400,
    scale: str = "linear",
) -> Optional[ClusterNode]:
    """Renders dendrogram object as a custom bi-directional Streamlit component

    Args:
        dendrogram (Dendrogram): IDendro dendrogram object
        orientation (str, optional): Position of dendrogram's root node. One of "top", "bottom", "left", "right". Defaults to "top".
        show_nodes (bool, optional): Whether to draw nodes. Defaults to True.
        height (float, optional): Height of the dendrogram. Defaults to 400.
        width (float, optional): Width of the dendrogram. Defaults to 400.
        scale (str, optional): Scale used for the value axis. One of "linear", "symlog", "log". Defaults to 'linear'.

    Returns:
        Optional[ClusterNode]: A ClusterNode object that was clicked on (None if no clicks took place)
    """

    _check_orientation(dendrogram, orientation)
    _check_scale(dendrogram, scale)
    _check_nodes(dendrogram, show_nodes)

    return StreamlitConverter().convert(
        dendrogram=dendrogram,
        orientation=orientation,
        show_nodes=show_nodes,
        height=height,
        width=width,
        key="idendro",
        scale=scale,
    )


class StreamlitConverter:
    def __init__(self, release: bool = False) -> None:
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
        dendrogram = json.loads(to_json(dendrogram)) 

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
