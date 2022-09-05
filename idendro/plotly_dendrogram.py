from __future__ import absolute_import
import typing

from plotly.graph_objs import graph_objs
import numpy as np
from matplotlib.colors import to_hex


def convert_scipy_to_plotly(
    scipy_dendrogram: dict, 
    width=np.inf, height=np.inf, 
    orientation='top',
    show_points = False,
    point_hover_func = None
    ):
    """Converts a SciPy dendrogram object to a Plotly one (with additional features)
    :param scipy_dendrogram - SciPy dendrogram object returned by scipy.cluster.hierarchy.dendrogram(no_plot=True,*)
    :param width - width of Plotly chart
    :param height - height of Plotly chart
    :param orientation - orientation of the dendrogram ('top', 'bottom', 'left' or 'right')
    :param show_points - whether dendrogram should be enhanced with points indicating nodes (True/False)
    :param point_hover_func -   a callable function that should return hovertext for each node. 
        The function will be called with a single parameter that represents the j-th position of the node in the linkage matrix.
        For details on how to interpret the position, see examples or https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html
    
    """

    layout = {'xaxis': {}, 'yaxis': {}}
    icoord = np.array(scipy_dendrogram['icoord'])
    dcoord = np.array(scipy_dendrogram['dcoord'])
    link_colors = np.array(scipy_dendrogram['color_list'])
    ordered_leaf_labels = np.array(scipy_dendrogram['ivl'])

    if orientation in ['top', 'bottom']:
        label_axis = 'xaxis'
        xcoords = icoord
        ycoords = dcoord
    else:
        label_axis = 'yaxis'
        ycoords = icoord
        xcoords = dcoord

    traces = get_plotly_traces(
        xcoords=xcoords, 
        ycoords=ycoords, 
        link_colors=link_colors
    )

    ordered_leaf_positions = get_ordered_leaf_positions(icoord, dcoord)

    #set general layout properties
    layout.update(
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
    layout['yaxis'].update(axis_defaults)
    layout['xaxis'].update(axis_defaults)

    #give a bit more range to x-axis for aesthetics
    layout['xaxis']['range'] = (xcoords.min(), 1.05 * xcoords.max())

    #deal with labels
    layout[label_axis].update({
        "ticktext": ordered_leaf_labels,
        "tickmode": "array",
        "tickvals": ordered_leaf_positions,
    })
    if label_axis == 'xaxis':
        layout['xaxis']['tickangle'] = 90

    #deal with reversed axis
    if orientation == 'bottom':
        layout['yaxis']['range'] = (1.05 * ycoords.max(), ycoords.min())
        layout['xaxis']['side'] = 'top'

    elif orientation == 'left':
        layout['yaxis']['side'] = 'right'
        layout['xaxis']['range'] = (1.05 * xcoords.max(), xcoords.min())

    return graph_objs.Figure(data=traces, layout=layout)


def get_ordered_leaf_positions(icoord: np.ndarray, dcoord: np.ndarray) -> np.ndarray: 
    "Finds the X-coordinate of the leafs in a dendrogram (Y-coordinate is zero)"
    X = icoord.flatten()
    Y = dcoord.flatten()
    return np.sort(X[Y == 0.0])


def get_plotly_traces(xcoords: np.ndarray, ycoords: np.ndarray, link_colors: np.ndarray):
    """
    Forms the traces representing the links in a dendrogram.
    """                
    trace_list = []

    for xs, ys, color in zip(xcoords, ycoords, link_colors):
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

    return trace_list