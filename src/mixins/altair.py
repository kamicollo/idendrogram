import collections

import altair as alt
import numpy as np
import pandas as pd
from matplotlib.colors import to_hex


class AltairFeatures:
    def to_altair(
        self,
        orientation="top",
        show_points=False,
        point_label_func="cluster_labels",
        point_hover_func=None,        
    ):
        """Converts a SciPy dendrogram object to a Plotly one (with additional features)
        :param width - width of Plotly chart
        :param height - height of Plotly chart
        :param orientation - orientation of the dendrogram ('top', 'bottom', 'left' or 'right')
        :param show_points - whether dendrogram should be enhanced with points indicating nodes (True/False)
        :param point_hover_func -   a callable function that should return hovertext for each node.
            The function will be called with a single parameter that represents the j-th position of the node in the linkage matrix.
            For details on how to interpret the position, see examples or https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html

        """
        # instantiate a dendrogram if one is not set yet
        if self.icoord is None:
            self.set_default_dendrogram()

        if orientation in ["top", "bottom"]:
            label_axis = alt.X
            value_axis = alt.Y
        else:
            label_axis = alt.Y
            value_axis = alt.X

        expr = []
        for pos, label in zip(
            self.get_ordered_leaf_positions(), self.ordered_leaf_labels
        ):
            expr.append(f"datum.value == {pos} ? '{label}'")
        expr.append("''")  # else condition
        label_expr_conditions = " : ".join(expr)

        traces = self.get_link_df(
            xcoords=self.icoord,
            ycoords=self.dcoord,
        )

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
                values=self.get_ordered_leaf_positions(),
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

        color_domain = np.arange(len(self.link_colors))
        color_range = [to_hex(c) for c in self.link_colors]

        lines = (
            alt.Chart(traces)
            .mark_line()
            .encode(
                X,
                Y,
                alt.Color(
                    "detail",
                    legend=None,
                    scale=alt.Scale(domain=color_domain, range=color_range),
                ),
                alt.Detail("detail"),
                alt.Order("order"),
            )
        )

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

    def get_link_df(self, xcoords: np.ndarray, ycoords: np.ndarray):
        """
        Forms the traces representing the links in a dendrogram.
        """
        trace_list = []

        for i, (xs, ys) in enumerate(zip(xcoords, ycoords)):
            line_segments = zip(xs, ys, [i] * 4, [1, 2, 3, 4])
            trace_list += line_segments

        trace_df = pd.DataFrame(trace_list, columns=["x", "y", "detail", "order"])
        return trace_df

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
