""""
import idendro.base_dendro as base_dendro
import idendro.plotly_dendro as plotly_dendro
import idendro.scipy_dendro as scipy_dendro
import idendro.altair_dendro as altair_dendro
import idendro.streamlit_dendro as streamlit_dendro

import importlib as imp



imp.reload(base_dendro)
imp.reload(plotly_dendro)
imp.reload(scipy_dendro)
imp.reload(altair_dendro)
imp.reload(streamlit_dendro)


from .base_dendro import BaseDendro
from .plotly_dendro import PlotlyFeatures
from .scipy_dendro import SciPyFeatures
from .altair_dendro import AltairFeatures
from .streamlit_dendro import StreamlitFeatures


class Idendro(PlotlyFeatures, SciPyFeatures, AltairFeatures, StreamlitFeatures, BaseDendro):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

"""