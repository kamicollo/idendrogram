import json
from dataclasses import is_dataclass, asdict
import numpy as np
from .. import types_classes

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


class JSON:
    def to_json(
        self: types_classes.BaseProtocol,
    ) -> str:
        """ Returns Dendrogram object as JSON string"""
        dendrogram = self.to_data()
        return json.dumps(dendrogram, cls=FullJSONEncoder)
