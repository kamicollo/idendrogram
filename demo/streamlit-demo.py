import sys
from pathlib import Path

path = Path("./").absolute().parent
sys.path.insert(1, str(path))

import streamlit as st
st.set_page_config(layout="wide")

from demo_func import DemoData
import numpy as np
import scipy.cluster.hierarchy as sch

signals_to_generate = 100
network_cluster_count = 12
x_plot_labels = np.linspace(1, 1000, 1000)

demo = DemoData(no_signals=signals_to_generate, seed=833142, no_network_clusters = network_cluster_count)
signals = demo.generate_raw_data()

impairments = {
            "Suckout" : (20, "green", np.arange(300,370), 0.5 * (np.abs(np.arange(-35, 35)) - 35)),
            "Wave" : (12, "orange", np.arange(580,700), 3*np.sin(np.arange(120)/5)),
        }

tilt_x = np.arange(1000)
tilt_y = np.zeros(1000,)
tilt_y[demo.ideal_signal > 0] = -tilt_x[demo.ideal_signal > 0] * 0.02
impairments["Tilt"] = (19, "red", tilt_x, tilt_y)

graph, impaired_signals, network_clusters = demo.generate_impaired_graph(impairments=impairments)
sparse_matrix = demo.get_sparse_wavelet_matrix(impaired_signals)
dists = demo.get_adjacency_matrix(sparse_matrix)

model = sch.linkage(dists, method='average')
threshold = 70
cluster_assignments = sch.fcluster(model, threshold, criterion='distance')

from dataclasses import dataclass, field
from typing import List
import idendro
import importlib as imp

from idendro.callbacks import cluster_labeller
imp.reload(idendro)

@dataclass
class MyAxisLabel(idendro.AxisLabel):
    labelAngle: float = 90

@dataclass
class MyLink(idendro.ClusterLink):
    strokewidth: float = 2
    strokedash: List = field(default_factory= lambda: [10, 5, 10, 10])
    strokeopacity: float = 0.5

@dataclass
class MyNode(idendro.ClusterNode):
    radius: float = 8
    _default_leaf_radius: float = 2
    labelsize: float = 10
    opacity: float = 0.5
    pass


cdata = idendro.ClusteringData(linkage_matrix=model, cluster_assignments=cluster_assignments, threshold=threshold)

dd = idendro.IDendro(link_factory=lambda x: MyLink(**x), node_factory=lambda x: MyNode(**x), axis_label_factory=lambda x: MyAxisLabel(**x))
dd.set_cluster_info(cdata)
dendrogram = dd.create_dendrogram(
    compute_nodes=True, 
    leaf_label_func= cluster_labeller()
)

sel_value = dendrogram.to_streamlit(orientation='top', height=800, width=1200, show_nodes=True, scale='linear')
st.write(sel_value)



