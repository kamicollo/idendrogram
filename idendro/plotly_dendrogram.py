from __future__ import absolute_import

from collections import OrderedDict

from plotly import exceptions, optional_imports
from plotly.graph_objs import graph_objs
import numpy as np
import scipy as scp
from matplotlib.colors import to_hex


def convert_scipy_to_plotly(scipy_dendrogram, width=np.inf, height=np.inf, orientation='top'):

    dendrogram = _Dendrogram(
        scipy_dendrogram,
        height=height,
        width=width,
        orientation=orientation
    )

    return graph_objs.Figure(data=dendrogram.data, layout=dendrogram.layout)



class _Dendrogram(object):
    """Refer to FigureFactory.create_dendrogram() for docstring."""

    def __init__(
        self,
        scipy_dendrogram,
        orientation,
        width,
        height,        
    ):
        self.orientation = orientation
        self.layout = {'xaxis': {}, 'yaxis': {}}
        
        dd_traces, ordered_leaf_positions = self.get_dendrogram_traces(scipy_dendrogram)

        ordered_leaf_labels = scp.array(scipy_dendrogram['ivl'])
        self.data = dd_traces

        #set general layout properties
        self.layout.update(
            {
                "showlegend": False,
                "autosize": False,
                "hovermode": "closest",
                "width": width,
                "height": height,
            }
        )

        #set axis defaults
        axis_defaults = {
            "type": "linear",
            "ticks": "outside",
            "mirror": False,
            "rangemode": "tozero",
            "showticklabels": True,
            "zeroline": False,
            "showgrid": False,
            "showline": True,
            "tickangle": 0,
        }
        self.layout['yaxis'].update(axis_defaults)
        self.layout['xaxis'].update(axis_defaults)

        #deal with labels
        label_axis = 'xaxis' if orientation in ['top', 'bottom'] else 'yaxis'
        self.layout[label_axis].update({
            "ticktext": ordered_leaf_labels,
            "tickmode": "array",
            "tickvals": ordered_leaf_positions,
        })
        if label_axis == 'xaxis':
            self.layout['xaxis']['tickangle'] = 90

        #deal with reversed axis
        if self.orientation == 'bottom':
            self.layout['yaxis']['autorange'] = 'reversed'
            self.layout['xaxis']['side'] = 'top'

        if self.orientation == 'left':
            self.layout['xaxis']['autorange'] = 'reversed'
            self.layout['yaxis']['side'] = 'right'


    def get_dendrogram_traces(
        self, scipy_dendrogram
    ):
        """
        Calculates all the elements needed for plotting a dendrogram.
        :param (ndarray) X: Matrix of observations as array of arrays
        """
                        
        icoord = scp.array(scipy_dendrogram["icoord"])
        dcoord = scp.array(scipy_dendrogram["dcoord"])
        link_colors = scipy_dendrogram["color_list"]

        trace_list = []
        leaf_positions = np.array([])

        for ic, dc, color in zip(icoord, dcoord, link_colors):
            # xs and ys are arrays of 4 points that make up the '∩' shapes
            # of the dendrogram tree

            #if dc == 0, we're looking at a leaf position
            leaf_positions = np.append(leaf_positions, ic[dc == 0])

            if self.orientation in ["top", "bottom"]:
                xs = ic
                ys = dc
            else:
                xs = dc
                ys = ic

            trace = dict(
                type="scatter",
                x=xs,
                y=ys,
                mode="lines",
                marker=dict(color=to_hex(color)),
                text=None,
                hoverinfo="text",
            )

            trace_list.append(trace)

        return trace_list, np.sort(leaf_positions)