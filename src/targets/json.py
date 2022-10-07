import json
from dataclasses import is_dataclass, asdict
import numpy as np
from .. import base_dendro

class FullJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if is_dataclass(obj):
            return asdict(obj)
        return json.JSONEncoder.default(self, obj)


class JSONConverter:
    def convert(self, d: base_dendro.Dendrogram) -> str:
        """Returns a JSON form of the dendrogram

        Args:
            d (base_dendro.Dendrogram): Dendrogram object

        Returns:
            str: JSON string
        """
        return json.dumps(d, cls=FullJSONEncoder)
