from typing import Tuple, Union

import altair as alt # type: ignore
import numpy as np
import pandas as pd
from dataclasses import asdict

from ..containers import Dendrogram
from .common import _check_nodes, _check_orientation, _check_scale

def to_altair(
    dendrogram: Dendrogram,
    orientation: str = "top",
    show_nodes: bool = True,
    height: float = 400,
    width: float = 400,
    scale: str = "linear",
) -> alt.LayerChart:
    """Converts a dendrogram object into Altair chart.

    Args:
        dendrogram (Dendrogram): idendrogram dendrogram object
        orientation (str, optional): Position of dendrogram's root node. One of "top", "bottom", "left", "right". Defaults to "top".
        show_nodes (bool, optional): Whether to draw nodes. Defaults to True.
        height (float, optional): Height of the dendrogram. Defaults to 400.
        width (float, optional): Width of the dendrogram. Defaults to 400.
        scale (str, optional): Scale used for the value axis. One of "linear", "symlog", "log". Defaults to 'linear'.

    Returns:
        Altair chart object
    """
    _check_orientation(dendrogram, orientation)
    _check_scale(dendrogram, scale)
    _check_nodes(dendrogram, show_nodes)

    return AltairConverter().convert(
        dendrogram=dendrogram,
        orientation=orientation,
        show_nodes=show_nodes,
        height=height,
        width=width,
        scale=scale,
    )

class AltairConverter:
    def convert(
        self,
        dendrogram: Dendrogram,
        orientation: str,
        show_nodes: bool,
        height: float,
        width: float,
        scale: str
    ) -> alt.LayerChart:
        """Converts dendrogram object into an Altair chart"""

        #first, initialize axes
        X, Y = self.create_axis(dendrogram=dendrogram, orientation=orientation, scale=scale)

        #draw links
        link_chart = self.draw_links(dendrogram, X, Y)

        #draw nodes if requested
        if show_nodes:            
            node_chart = self.draw_nodes(dendrogram, X, Y)
        else:
            node_chart = alt.Chart(pd.DataFrame()).mark_point()

        #return layered object
        return alt.layer(link_chart, node_chart).properties(width=width, height=height)        

    def create_axis(self, dendrogram: Dendrogram, orientation: str, scale: str) -> Tuple[Union[alt.X, alt.Y], Union[alt.X, alt.Y]]:
        """Create appropriate altair axis objects"""

        if orientation in ["top", "bottom"]:
            label_axis = alt.X
            value_axis = alt.Y
        else:
            label_axis = alt.Y
            value_axis = alt.X

        #there's no nice way to do custom tick labels in Altair, so we use vegalite JS conditions...
        expr = [f"datum.value == {x.x} ? '{x.label}'" for x in dendrogram.axis_labels]
        expr.append("''")  # else condition
        label_expr_conditions = " : ".join(expr)

        label_pos = {
            "top": "bottom",
            "bottom": "top",
            "left": "right",
            "right": "left",
        }[orientation]

        X = label_axis(
            "x",
            title=None,
            axis=alt.Axis(
                ticks=False,
                labelExpr=label_expr_conditions,
                values=[x.x for x in dendrogram.axis_labels],
                orient=label_pos,
                grid=False,
                labelPadding=10,
                labelAngle=dendrogram.axis_labels[0].labelAngle
            ),
        )
        reversed_axis = orientation in ["bottom", "left"]

        Y = value_axis(
            "y",
            title=None,
            scale=alt.Scale(reverse=reversed_axis, type=scale),
            axis=alt.Axis(grid=False),
        )

        return X, Y

    def draw_links(
        self, dendrogram: Dendrogram, X: Union[alt.X, alt.Y], Y: Union[alt.X, alt.Y]
    ) -> alt.Chart:
        """
        Forms the traces representing the links in a dendrogram.
        """

        df = (
            pd.DataFrame([asdict(x) for x in dendrogram.links]) 
            .explode(["x", "y", "_order_helper"]) # type: ignore
            .reset_index() 
        ) 

        lines = (
            alt.Chart(df)
            .mark_line()
            .encode(
                X,
                Y,
                alt.Color("fillcolor", legend=None, scale=None),
                alt.Detail("index"),
                alt.Order("_order_helper"),
                alt.StrokeWidth("strokewidth", legend=None, scale=None),
                alt.StrokeOpacity("strokeopacity", legend=None, scale=None),
                alt.StrokeDash("strokedash", legend=None, scale=None),
            )
        )

        return lines

    def draw_nodes(
        self, dendrogram: Dendrogram, X: Union[alt.X, alt.Y], Y: Union[alt.X, alt.Y]
    ) -> alt.LayerChart:
        """Forms the traces representing the nodes"""

        node_df = pd.DataFrame(dendrogram.nodes)
        node_df['size'] = node_df['radius'] ** 2 * np.pi #altair uses size for area, not radius

        nodes = (
            alt.Chart(node_df)
            .mark_point()
            .encode(
                X,
                Y,
                alt.Stroke("edgecolor", scale=None),
                alt.Fill("fillcolor", scale=None),
                alt.Tooltip("hovertext"),
                alt.Size("size", scale=None),
                alt.Opacity("opacity", scale=None)
            )
        )

        node_labels = (
            alt.Chart(node_df)
            .mark_text(fontWeight='bold')
            .encode(
                X,
                Y,
                alt.Text("label"),
                alt.Tooltip("hovertext"),
                alt.Size("labelsize", scale=None),
                alt.Color("labelcolor", scale=None),                
            )
        )

        return alt.layer(nodes + node_labels)