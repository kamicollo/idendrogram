from math import pi
from typing import Dict, List
from plotly.graph_objs import graph_objs # type: ignore

from ..containers import ClusterLink, ClusterNode, Dendrogram


class PlotlyConverter:
    def convert(
        self,
        dendrogram: Dendrogram,
        orientation: str,
        show_nodes: bool,
        height: float,
        width: float,
    ) -> graph_objs._figure.Figure:

        layout = self.setup_layout(orientation=orientation, width=width, height=height, dendrogram=dendrogram)

        if orientation in ["top", "bottom"]:
            x = "x" 
            y = 'y'
        else:
            x = "y" 
            y = 'x'

        traces = self.link_traces(x, y, dendrogram.links)  

        if show_nodes:
            if not dendrogram.computed_nodes:
                raise RuntimeError("Nodes were not computed in create_dendrogram() step, cannot show them")
            traces += self.node_traces(x, y, dendrogram.nodes)
        
        return graph_objs.Figure(data=traces, layout=layout)

    def setup_layout(self, orientation: str, width: float, height: float, dendrogram: Dendrogram) -> Dict:

        layout = {
            "showlegend": False,
            "autosize": False,
            "hovermode": "closest",
            "width": width,
            "height": height,            
        }
            
        # set axis defaults
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
        value_axis = axis_defaults.copy()
        label_axis = axis_defaults.copy()


        #control label position
        position_map = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }

        label_position_side = position_map[orientation]

        # add label-axis labels
        label_axis['ticktext'] = [label.label for label in dendrogram.axis_labels]
        label_axis['tickvals'] = [label.x for label in dendrogram.axis_labels]
        label_axis['tickmode'] = 'array'
        label_axis['side'] = label_position_side

        # give a bit more range to x-axis for aesthetics
        min_x, max_x = dendrogram.x_domain
        range_x = max_x - min_x
        label_axis["range"] = (
            min_x - range_x * 0.05,
            max_x + range_x * 0.05,
        )

        # deal with reversed axis
        min_y, max_y = dendrogram.y_domain
        range_y = max_y - min_y
        if orientation in ["bottom", "left"]:
            value_axis["range"] = (max_y + range_y * 0.05, min_y)
        else:
            value_axis["range"] = (min_y, max_y + range_y * 0.05)


        if orientation in ["top", "bottom"]:
            layout["xaxis"] = label_axis
            layout["yaxis"] = value_axis            
        else:
            layout["yaxis"] = label_axis
            layout["xaxis"] = value_axis
                    
        return layout

    def link_traces(self, x: str, y: str, links: List[ClusterLink]) -> List[Dict]:
        """
        Forms the traces representing the links in a dendrogram.
        """
        trace_list = []

        for link in links:

            dash = ", ".join([str(i) for i in link.strokedash])
            trace = dict(
                type="scatter",                
                mode="lines",                
                line = dict(width=link.strokewidth, color=link.fillcolor, dash=dash),
                text=None,
                hoverinfo="text",
                opacity=link.strokeopacity,                
            )

            #no idea why mypy is throwing type errors here...
            trace[x] = link.x # type: ignore
            trace[y] = link.y # type: ignore
            trace_list.append(trace)

        return trace_list

    def node_traces(self, x: str, y: str, nodes: List[ClusterNode]) -> List[Dict]:

        node_traces = []

        for node in nodes:

            html_hovertext = "<br>".join([f"<b>{k}</b> : {v}" for k, v in node.hovertext.items()])

            p = dict(
                type = "scatter",
                mode =  "markers+text",
                hoverinfo = "text",
                textfont_size =  node.labelsize,
                textfont_color = node.labelcolor,
                marker=dict(
                    color=node.fillcolor,
                    size=node.radius * 2,
                    line=dict(width=2, color=node.edgecolor),
                ),
                hovertext = html_hovertext,
                text=node.label,
                opacity = node.opacity
            )
            p[x] = [node.x]
            p[y] = [node.y]

            node_traces.append(p)

        return node_traces
