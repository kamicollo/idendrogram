from scipy.cluster.hierarchy import _plot_dendrogram
import numpy as np
import matplotlib.pyplot as plt

class SciPyFeatures:

    def to_scipy(self, 
        orientation='top',
        show_points = False,
        point_hover_func = None,
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

