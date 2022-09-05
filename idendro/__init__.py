import idendro.base_dendro as base_dendro
import idendro.plotly_dendro as plotly_dendro
import idendro.scipy_dendro as scipy_dendro

import importlib as imp

imp.reload(base_dendro)
imp.reload(plotly_dendro)
imp.reload(scipy_dendro)


from .base_dendro import BaseDendro
from .plotly_dendro import PlotlyFeatures
from .scipy_dendro import SciPyFeatures


class Idendro(PlotlyFeatures, SciPyFeatures, BaseDendro):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)