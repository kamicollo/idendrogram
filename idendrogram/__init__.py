"""Interactive dendrograms compatible with scipy, scikit-learn and hdbscan"""

DEV = False
__version__ = "0.2.0"
__description__ = "Interactive dendrograms in Plotly, Altair and Streamlit, compatible with scipy, scikit-learn and hdbscan"

if DEV:
    import importlib as imp

    from .targets import altair as alt_backend
    imp.reload(alt_backend)

    from .targets import json as json_backend
    imp.reload(json_backend)

    from .targets import matplotlib as matplotlib_backend
    imp.reload(matplotlib_backend)

    from .targets import plotly as plotly_backend
    imp.reload(plotly_backend)

    from .targets import streamlit as streamlit_backend
    imp.reload(streamlit_backend)

    from . import callbacks
    imp.reload(callbacks)

    from . import clustering_data
    imp.reload(clustering_data)

    from . import containers
    imp.reload(containers)

    from . import base
    imp.reload(base)


from .base import idendrogram
from .containers import Dendrogram, ClusterLink, ClusterNode, AxisLabel
from .clustering_data import ClusteringData, HDBSCANClusteringData, ScikitLearnClusteringData
