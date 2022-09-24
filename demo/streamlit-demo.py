import sys
from pathlib import Path
from turtle import width

path = Path("./").absolute().parent
sys.path.insert(1, str(path))

import streamlit as st
from demo_func import DemoData
import numpy as np
import scipy.cluster.hierarchy as sch
import idendro 
import importlib as imp


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

idd = idendro.Idendro(model, cluster_assignments, threshold)
component_value = idd.to_streamlit(key='o', width=950, height=800)
st.markdown("You've šmiked %s times!" % int(component_value))
