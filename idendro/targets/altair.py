import collections
from typing import Union

import altair as alt
import numpy as np
import pandas as pd
from dataclasses import asdict

from ..containers import Dendrogram

class AltairConverter:

    def convert(self,
        dendrogram: Dendrogram,
        orientation: str,
        show_points: bool,        
    ):

        X, Y = self.create_axis(dendrogram=dendrogram, orientation=orientation)

        link_chart = self.draw_links(dendrogram, X, Y)
        if show_points:
            node_chart = self.draw_nodes(dendrogram, X, Y)
        else:
            node_chart = alt.Chart(pd.DataFrame()).mark_point()
        
        return alt.layer(link_chart, node_chart)

        

        if show_points:
            point_df, hover_fields = self.get_point_df(
                point_label_func=point_label_func,
                point_hover_func=point_hover_func,
            )

            points = (
                alt.Chart(point_df)
                .mark_point(size=10**2, opacity=1)
                .encode(
                    X,
                    Y,
                    alt.Stroke("edgecolor", scale=None),
                    alt.Fill("fillcolor", scale=None),
                    alt.Tooltip(hover_fields),
                )
            )

            labels = (
                alt.Chart(point_df)
                .mark_text(size=9, color="white", fontWeight="bold")
                .encode(X, Y, alt.Text("text"), alt.Tooltip(hover_fields))
            )
            chart = lines + points + labels
        else:
            chart = lines + alt.Chart(pd.DataFrame()).mark_point()

        return chart

    def create_axis(self, dendrogram: Dendrogram, orientation: str):

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
            ),
        )
        reversed_axis = orientation in ["bottom", "left"]

        Y = value_axis(
            "y",
            title=None,
            scale=alt.Scale(reverse=reversed_axis),
            axis=alt.Axis(grid=False),
        )

        return X,Y

    def draw_links(self, dendrogram: Dendrogram, X: Union[alt.X, alt.Y], Y: Union[alt.X, alt.Y]) -> alt.Chart:
        """
        Forms the traces representing the links in a dendrogram.
        """
        
        df = pd.DataFrame([asdict(x) for x in dendrogram.links]).explode(["x", "y", "_order_helper"]).reset_index()

        lines = (
            alt.Chart(df)
            .mark_line()
            .encode(
                X,
                Y,
                alt.Color("fillcolor", legend=None, scale=None),
                alt.Detail("index"),
                alt.Order("_order_helper"),
                alt.StrokeWidth('strokewidth', legend=None, scale=None),
                alt.StrokeOpacity('strokeopacity', legend=None, scale=None),
                alt.StrokeDash('strokedash', legend=None, scale=None),
            )
        )

        return lines

    def draw_nodes(self, dendrogram: Dendrogram, X: Union[alt.X, alt.Y], Y: Union[alt.X, alt.Y]) -> alt.LayerChart:
        node_df = pd.DataFrame(dendrogram.nodes)
        #node_df['_hover'] = node_df['hovertext'].apply(lambda: )

        nodes = (
            alt.Chart(node_df)
            .mark_point(size=10**2, opacity=1)
            .encode(
                X,
                Y,
                alt.Stroke("edgecolor", scale=None),
                alt.Fill("fillcolor", scale=None),
                alt.Tooltip("hovertext"),
                alt.Radius("radius")
            )
        )

        node_labels = (
            alt.Chart(node_df)
            .mark_text(size=9, color="white", fontWeight="bold")
            .encode(X, Y, alt.Text("label"), alt.Tooltip("hovertext"))
        )

        return alt.layer(nodes + node_labels)
    


    def get_point_df(self, point_label_func, point_hover_func):

        point_traces = []

        points = self.get_points()
        if point_label_func == "cluster_labels":
            point_label_func = (
                lambda x: "" if x["type"] != "cluster" else f"{x['cluster_id']}"
            )

        for (x, y), point in points.items():
            fillcolor = (
                "white" if point["type"] in ["leaf", "subcluster"] else point["color"]
            )
            edgecolor = point["color"]
            text = point_label_func(point) if point_label_func is not None else ""

            p = dict(
                x=x,
                y=y,
                fillcolor=to_hex(fillcolor),
                edgecolor=to_hex(edgecolor),
                text=text,
            )

            hovertext = point_hover_func(point) if point_hover_func is not None else ""
            if isinstance(hovertext, collections.abc.Mapping):
                p["hover"] = list(hovertext.keys())
                p.update(hovertext)
            else:
                p["hovertext"] = hovertext
                p["hover"] = "hovertext"

            point_traces.append(p)

        return pd.DataFrame(point_traces), p["hover"]
