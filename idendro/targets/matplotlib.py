import math
import matplotlib.pyplot as plt
from ..containers import ClusterLink, ClusterNode, Dendrogram
from matplotlib.axes import Axes
from typing import List

class matplotlibConverter():
    def convert(
        self,
        dendrogram: Dendrogram,
        orientation: str,
        show_nodes: bool,
        width: float,
        height: float,
    ) -> list:

        ax = self.setup_layout(orientation=orientation, width=width, height=height, dendrogram=dendrogram)
        
        if orientation in ["top", "bottom"]:
            x = "x" 
            y = 'y'
        else:
            x = "y" 
            y = 'x'

        self.plot_links(ax, x, y, dendrogram.links)  

        if show_nodes:
            if not dendrogram.computed_nodes:
                raise RuntimeError("Nodes were not computed in create_dendrogram() step, cannot show them")
            self.plot_nodes(ax, x, y, dendrogram.nodes)                        

    def setup_layout(self, orientation: str, width: float, height: float, dendrogram: Dendrogram) -> Axes:
        
        fig = plt.gcf()
        fig.set_size_inches(width, height)

        ax = plt.gca()

        min_y, max_y = dendrogram.y_domain
        range_y = max_y - min_y
        min_x, max_x = dendrogram.x_domain
        range_x = max_x - min_x


        labels, positions = zip(*[(l.label, l.x) for l in dendrogram.axis_labels])

        if orientation in ['top', 'bottom']:
            label_axis = ax.xaxis
            ax.set_ylim(min_y, max_y + range_y * 0.05)
        else:
            label_axis = ax.yaxis
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
        label_axis.set_ticks(positions, labels=labels)
        label_axis.set_ticks_position(label_position_side)
        label_axis.limit_range_for_scale(
            min_x - range_x * 0.05,
            max_x + range_x * 0.05
        )


        return ax

    def plot_links(self, ax: Axes, x: str, y: str, links: List[ClusterLink]):        

        for link in links: 
            if len(link.strokedash) > 1:
                dash = (link.strokedash[0], link.strokedash[1:]) 
            else:
                dash = link.strokedash          
            plt.plot(
                link.__getattribute__(x), 
                link.__getattribute__(y), 
                color=link.fillcolor,
                linestyle=tuple(dash),
                linewidth = link.strokewidth,
                alpha=link.strokeopacity
            )


    def plot_nodes(self, ax: Axes, x: str, y: str, nodes: List[ClusterNode]):
        
        for node in nodes:
            
            # circle = Circle(
            #     (node.__getattribute__(x), node.__getattribute__(y)),
            #     facecolor = node.fillcolor,                
            #     linewidth = 2,
            #     alpha = node.opacity,
            #     radius = node.radius,
            #     edgecolor = node.edgecolor
            # )

            # ax.add_patch(circle)

            plt.plot(
                node.__getattribute__(x), node.__getattribute__(y),
                markerfacecolor = node.fillcolor,                
                linewidth = 2,
                alpha = node.opacity,
                markersize = node.radius * math.pi,
                markeredgecolor = node.edgecolor,
                marker='o'
            )
                
            plt.text(
                node.__getattribute__(x), 
                node.__getattribute__(y), 
                s = node.label, 
                fontsize = node.labelsize, 
                color = node.labelcolor,
                ha = 'center', 
                va = 'center',
                fontweight = 'bold'
            )