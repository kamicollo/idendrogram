from typing import Tuple, Union

import altair as alt # type: ignore
import numpy as np
import pandas as pd
from dataclasses import asdict

from ..containers import Dendrogram


class AltairConverter:
    def convert(
        self,
        dendrogram: Dendrogram,
        orientation: str,
        show_nodes: bool,
        height: float,
        width: float,
    ) -> alt.LayerChart:

        X, Y = self.create_axis(dendrogram=dendrogram, orientation=orientation)

        link_chart = self.draw_links(dendrogram, X, Y)
        if show_nodes:
            if not dendrogram.computed_nodes:
                raise RuntimeError("Nodes were not computed in create_dendrogram() step, cannot show them")
            node_chart = self.draw_nodes(dendrogram, X, Y)
        else:
            node_chart = alt.Chart(pd.DataFrame()).mark_point()

        return alt.layer(link_chart, node_chart).properties(width=width, height=height)        

    def create_axis(self, dendrogram: Dendrogram, orientation: str) -> Tuple[Union[alt.X, alt.Y], Union[alt.X, alt.Y]]:

        if orientation in ["top", "bottom"]:
            label_axis = alt.X
            value_axis = alt.Y
        else:
            label_axis = alt.Y
            value_axis = alt.X

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
            scale=alt.Scale(reverse=reversed_axis),
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