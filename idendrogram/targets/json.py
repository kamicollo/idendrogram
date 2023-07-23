import json
from dataclasses import is_dataclass, asdict
from typing import Any
from ..containers import Dendrogram


def to_json(dendrogram: Dendrogram) -> str:
    """Returns the dendrogram object represented as a JSON string

    Args:
        dendrogram (Dendrogram): idendrogram dendrogram object

    Returns:
        str: JSON string
    """    

    return JSONConverter().convert(dendrogram)


class FullJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:    
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
