from scipy.cluster.hierarchy import _plot_dendrogram
import numpy as np
import matplotlib.pyplot as plt

class matplotlibConverter():
    pass

class SciPyFeatures:

    def to_scipy(self, 
        orientation='top',
        show_points = False,
        point_label_func = 'cluster_labels',
        point_kwargs = {},
        label_kwargs = {},
        ax = None,
        no_labels=False,
        leaf_font_size = None,
        leaf_rotation = None,
        above_threshold_color = 'C0'
    ):

        #instantiate a dendrogram if one is not set yet
        if self.icoord is None:
            self.set_default_dendrogram()

        mh = np.max(self.linkage_matrix[:, 2])

        _plot_dendrogram(
            icoords=self.icoord, dcoords=self.dcoord, ivl=self.ordered_leaf_labels, 
            p=None, n=None, mh=mh, orientation=orientation,
            no_labels=no_labels, color_list=self.link_colors, leaf_font_size=leaf_font_size,
            leaf_rotation=leaf_rotation, 
            ax=ax, above_threshold_color=above_threshold_color,
            contraction_marks=None
        )

        if show_points:
            used_point_kwargs = {'markersize': 14}
            used_point_kwargs.update(point_kwargs)

            used_label_kwargs = {'size': 8, 'color': 'white', 'fontweight': 'bold', 'ha': 'center', 'va': 'center'}
            used_label_kwargs.update(label_kwargs)

            ploton = ax if ax is not None else plt
            points = self.get_points()
            if point_label_func == 'cluster_labels':
                point_label_func = lambda x: "" if x['type'] != 'cluster' else x['cluster_id']

            for (x,y), point in points.items():
                if orientation in ['left', 'right']:
                    x,y = y,x
                facecolor = 'white' if point['type'] in ['leaf', 'subcluster'] else point['color']
                ploton.plot(x, y, marker='o', markerfacecolor=facecolor, markeredgecolor=point['color'], **used_point_kwargs)

                if point_label_func is not None:
                    label = point_label_func(point)
                    ploton.text(x, y, s=label, **used_label_kwargs)
