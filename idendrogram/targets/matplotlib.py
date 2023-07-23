import matplotlib.pyplot as plt # type: ignore
from ..containers import ClusterLink, ClusterNode, Dendrogram
from matplotlib.axes import Axes # type: ignore
from typing import List

from .common import _check_nodes, _check_orientation, _check_scale


def to_matplotlib(
        dendrogram: Dendrogram,
        orientation: str = "top",
        show_nodes: bool = True,
        height: float = 400,
        width: float = 400,
        scale: str = "linear",
    ) -> Axes:
        """Converts a dendrogram object into matplotlib chart

        Args:
            dendrogram (Dendrogram): idendrogram dendrogram object
            orientation (str, optional): Position of dendrogram's root node. One of "top", "bottom", "left", "right". Defaults to "top".
            show_nodes (bool, optional): Whether to draw nodes. Defaults to True.
            height (float, optional): Height of the dendrogram. Defaults to 400.
            width (float, optional): Width of the dendrogram. Defaults to 400.
            scale (str, optional): Scale used for the value axis. One of "linear", "symlog", "log". Defaults to 'linear'.

        Returns:
            matplotlib.pyplot.ax: matplotlib axes object
        """
        _check_orientation(dendrogram, orientation)
        _check_scale(dendrogram, scale)
        _check_nodes(dendrogram, show_nodes)

        return matplotlibConverter().convert(
            dendrogram=dendrogram,
            orientation=orientation,
            show_nodes=show_nodes,
            height=height,
            width=width,
            scale=scale,
        )

class matplotlibConverter():
    def convert(
        self,
        dendrogram: Dendrogram,
        orientation: str,
        show_nodes: bool,
        width: float,
        height: float,
        scale: str
    ) -> Axes:
        """Converts dendrogram object to matplotlib chart"""

        #setup axes        
        ax = self.setup_layout(orientation=orientation, width=width, height=height, dendrogram=dendrogram, scale=scale)        
        if orientation in ["top", "bottom"]:
            x = "x" 
            y = 'y'
        else:
            x = "y" 
            y = 'x'

        #plot links        
        self.plot_links(ax, x, y, dendrogram.links)          

        #plot nodes
        if show_nodes:            
            self.plot_nodes(ax, x, y, dendrogram.nodes)            
        return ax                    

    def setup_layout(self, orientation: str, width: float, height: float, dendrogram: Dendrogram, scale: str) -> Axes:
        """Setup axes"""
        
        #use existing axes/figure if any        
        fig = plt.gcf()
        ax = plt.gca()
        fig.set_size_inches(width / fig.dpi, height / fig.dpi)        

        min_y, max_y = dendrogram.y_domain
        range_y = max_y - min_y
        min_x, max_x = dendrogram.x_domain
        range_x = max_x - min_x


        labels, positions = zip(*[(l.label, l.x) for l in dendrogram.axis_labels])
        rotation = dendrogram.axis_labels[0].labelAngle

        if orientation in ['top', 'bottom']:
            label_axis = ax.xaxis
            value_axis = ax.set_yscale
            ax.set_ylim(min_y, max_y + range_y * 0.05)
        else:
            label_axis = ax.yaxis
            value_axis = ax.set_xscale
            ax.set_xlim(min_y, max_y + range_y * 0.05)

        if orientation == 'bottom':
            ax.yaxis.set_inverted(True)
        elif orientation == 'left':
            ax.xaxis.set_inverted(True)

        #set up label axis 
        position_map = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }

        label_position_side = position_map[orientation]
        label_axis.set_ticks(positions, labels=labels, rotation=rotation)
        label_axis.set_ticks_position(label_position_side)
        label_axis.limit_range_for_scale(
            min_x - range_x * 0.05,
            max_x + range_x * 0.05
        )        

        value_axis(scale)


        return ax

    def plot_links(self, ax: Axes, x: str, y: str, links: List[ClusterLink]) -> None:        
        """Plotting the links"""

        for link in links:                         
            ax.plot(
                link.__getattribute__(x), 
                link.__getattribute__(y), 
                color=link.fillcolor,
                linestyle = (0, link.strokedash),
                linewidth = link.strokewidth,
                alpha=link.strokeopacity
            )


    def plot_nodes(self, ax: Axes, x: str, y: str, nodes: List[ClusterNode]) -> None:
        """Plotting the nodes"""
        for node in nodes:

            ax.plot(
                node.__getattribute__(x), node.__getattribute__(y),
                markerfacecolor = node.fillcolor,                
                linewidth = 2,
                alpha = node.opacity,
                markersize = node.radius * (ax.figure.dpi / 72),
                markeredgecolor = node.edgecolor,
                marker='o'
            )
                
            ax.text(
                node.__getattribute__(x), 
                node.__getattribute__(y), 
                s = node.label, 
                fontsize = node.labelsize / (ax.figure.dpi / 72), 
                color = node.labelcolor,
                ha = 'center', 
                va = 'center',
                fontweight = 'bold'
            )