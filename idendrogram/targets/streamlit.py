from typing import Optional
from idendrogram.containers import ClusterNode, Dendrogram
from .common import _check_nodes, _check_orientation, _check_scale
import importlib
idendrogram_streamlit = importlib.import_module("idendrogram_streamlit_component")


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
        dendrogram (Dendrogram): idendrogram dendrogram object
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

    return idendrogram_streamlit.StreamlitConverter(release=True).convert(
        dendrogram=dendrogram,
        orientation=orientation,
        show_nodes=show_nodes,
        height=height,
        width=width,
        key="idendrogram",
        scale=scale,
    )