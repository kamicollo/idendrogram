from typing import List
from ..containers import Dendrogram

def _check_orientation(
        dendrogram: Dendrogram, orientation: str, supported: List = ["top", "bottom", "left", "right"]
    ) -> None:
        """Checks validity of orientation value provided"""
        if orientation not in supported:
            raise ValueError(
                f"""Orientation should be one of '{"', '".join(supported)}'. Provided: '{orientation}'"""
            )

def _check_scale(
    dendrogram: Dendrogram, scale: str, supported: List[str] = ["linear", "log", "symlog"]
) -> None:
    """Checks validity of scale value provided"""
    if scale not in supported:
        raise ValueError(
            f"""Scale should be one of '{"', '".join(supported)}'. Provided: '{scale}'"""
        )

def _check_nodes(dendrogram: Dendrogram, show_nodes: bool) -> None:
    """Checks if nodes were not computed but are requested to be drawn"""
    if show_nodes and not dendrogram.computed_nodes:
        raise RuntimeError(
            "Nodes were not computed in create_dendrogram() step, cannot show them"
        )