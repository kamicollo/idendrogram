import collections
from itertools import zip_longest
import altair as alt 
import numpy as np
import pandas as pd
from matplotlib.colors import to_hex


class AltairFeatures:

    def to_altair(self, 
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

        if orientation in ['top', 'bottom']:
            label_axis = 'xaxis'
            xcoords = self.icoord
            ycoords = self.dcoord
        else:
            label_axis = 'yaxis'
            ycoords = self.icoord
            xcoords = self.dcoord

        traces = self.get_link_df(
            xcoords=xcoords, 
            ycoords=ycoords, 
        )


        line_chart = alt.Chart(traces).mark_line().encode(
            alt.X('x', title=None),
            alt.Y('y', title=None, scale=alt.Scale(reverse=True)),
            alt.Color('color', legend=None),
            alt.Detail('detail')
        )

        if show_points:
            self.get_point_df(
                orientation, 
                point_trace_kwargs = point_trace_kwargs, 
                point_label_func = point_label_func,
                point_hover_func = point_hover_func
            )

        ordered_leaf_positions = self.get_ordered_leaf_positions()

        

        return line_chart

    def get_link_df(self, xcoords: np.ndarray, ycoords: np.ndarray):
        """
        Forms the traces representing the links in a dendrogram.
        """                
        trace_list = []

        for i, (xs, ys, color) in enumerate(zip(xcoords, ycoords, self.link_colors)):
            line_segments = zip(xs, ys, [color]*4, [i]*4)
            trace_list += line_segments

        trace_df = pd.DataFrame(trace_list, columns = ['x', 'y', 'color', 'detail'])
        return trace_df  
    
    def get_point_df(self, orientation, point_trace_kwargs, point_label_func, point_hover_func):

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

            