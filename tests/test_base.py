import unittest
import numpy as np

from src import base_dendro


class TestInit(unittest.TestCase):
    def test_requires_some_args(self):
        self.assertRaises(TypeError, base_dendro.BaseDendro.__init__)

    def test_incomplete_params(self):
        self.assertRaises(
            TypeError,
            base_dendro.BaseDendro.__init__,
            linkage_matrix=np.zeros((100, 4)),
            threshold=30,
        )

    def fake_dendro(self):
        return {
            "color_list": ["a", "b"],
            "icoord": [[1, 2, 3, 4]],
            "dcoord": [[1, 2, 3, 4]],
            "ivl": ["a"],
            "leaves": [1, 2, 3],
            "leaves_color_list": ["a", "b"],
        }

    def test_scipyDendro(self):
        d = self.fake_dendro()
        base_dendro.BaseDendro(scipy_dendrogram=d)
        
    
    def test_incompleteScipyDendro(self):
        d = self.fake_dendro()        
        base_dendro.BaseDendro(scipy_dendrogram=d)


if __name__ == "__main__":
    unittest.main()
