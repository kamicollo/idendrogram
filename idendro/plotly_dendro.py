import collections
from plotly.graph_objs import graph_objs
import numpy as np
from matplotlib.colors import to_hex


class PlotlyFeatures:

    def to_plotly(self, 
        width=np.inf, height=np.inf, 
        orientation='top',
        show_points = False,
        point_label_func = 'cluster_labels',
        point_hover_func = None,
        point_trace_kwargs = {}
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
        #instantiate a dendrogram if one is not set yet
        if self.icoord is None:
            self.set_default_dendrogram()

        layout = {'xaxis': {}, 'yaxis': {}}

        if orientation in ['top', 'bottom']:
            label_axis = 'xaxis'
            xcoords = self.icoord
            ycoords = self.dcoord
        else:
            label_axis = 'yaxis'
            ycoords = self.icoord
            xcoords = self.dcoord

        traces = self.get_link_traces(
            xcoords=xcoords, 
            ycoords=ycoords, 
        )

        if show_points:
            traces += self.get_point_traces(
                orientation, 
                point_trace_kwargs = point_trace_kwargs, 
                point_label_func = point_label_func,
                point_hover_func = point_hover_func
            )

        ordered_leaf_positions = self.get_ordered_leaf_positions()

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
        layout['xaxis']['range'] = (
            xcoords.min() - (xcoords.max() - xcoords.min())*0.05*(orientation != 'right'),
            xcoords.max() + (xcoords.max() - xcoords.min())*0.05,
        )

        #deal with labels
        layout[label_axis].update({
            "ticktext": self.ordered_leaf_labels,
            "tickmode": "array",
            "tickvals": ordered_leaf_positions,
        })

        #deal with reversed axis
        if orientation == 'bottom':
            layout['yaxis']['range'] = (1.05 * ycoords.max(), ycoords.min())
            layout['xaxis']['side'] = 'top'

        elif orientation == 'left':
            layout['yaxis']['side'] = 'right'
            layout['xaxis']['range'] = (1.05 * xcoords.max(), xcoords.min())

        return graph_objs.Figure(data=traces, layout=layout)

    def get_link_traces(self, xcoords: np.ndarray, ycoords: np.ndarray):
        """
        Forms the traces representing the links in a dendrogram.
        """                
        trace_list = []

        for xs, ys, color in zip(xcoords, ycoords, self.link_colors):
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
    
    def get_point_traces(self, orientation, point_trace_kwargs, point_label_func, point_hover_func):

        point_traces = []
        used_point_kwargs = {
            'type': 'scatter',
            'mode': 'markers+text',
            'hoverinfo' : 'text',
            'textfont_size': 8,
            'textfont_color': 'white'
        }
        used_point_kwargs.update(point_trace_kwargs)

        points = self.get_points()
        if point_label_func == 'cluster_labels':
            point_label_func = lambda x: "" if x['type'] != 'cluster' else f"<b>{x['cluster_id']}</b>"

        for (x,y), point in points.items():
            if orientation in ['left', 'right']:
                x,y = y,x
            fillcolor = 'white' if point['type'] in ['leaf', 'subcluster'] else point['color']
            edgecolor = point['color']

            point = dict(
                x=[x],
                y=[y],
                marker=dict(
                    color=to_hex(fillcolor), 
                    size=14, 
                    line=dict(
                        width=2, 
                        color=to_hex(edgecolor)
                    )),
                text=point_label_func(point) if point_label_func is not None else "",
                hovertext= point_hover_func(point) if point_hover_func is not None else "",
            )

            for key,val in used_point_kwargs.items():
                if isinstance(val, collections.abc.Mapping) and key in point:
                    point[key].update(val)
                else:
                    point[key] = val
                            
            point_traces.append(point)
        
        return point_traces

            