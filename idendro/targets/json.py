import json
from dataclasses import is_dataclass, asdict
from typing import Any
import numpy as np
from ..containers import Dendrogram

class FullJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
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
    def convert(self, d: Dendrogram) -> str:
        """Returns a JSON form of the dendrogram

        Args:
            d (Dendrogram): Dendrogram object

        Returns:
            str: JSON string
        """
        return json.dumps(d, cls=FullJSONEncoder)
