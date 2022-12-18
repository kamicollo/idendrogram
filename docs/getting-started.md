
IDendro helps you create nicer, interactive visualizations of hierarchical clustering trees (a.k.a. dendrograms) in your preferred python visualization library (Altair, Plotly or Matplotlib), and supports Streamlit integration via a custom D3-powered component. 

It does not include any clustering functionality itself, but integrates with SciPy and Scikit-learn hierarchical clustering outputs instead.

Backends currently supported: Altair, Plotly, Streamlit (with a custom D3 component) and (partially) Matplotlib.

## IDendro 101 

### Cluster iris dataset with SciPy

```python
from sklearn.datasets import load_iris
data = load_iris(as_frame=True)

import scipy.cluster.hierarchy as sch
linkage_matrix = sch.linkage(data['data'], method='single', metric='euclidean')
threshold = 0.6
flat_clusters = sch.fcluster(linkage_matrix, t=threshold, criterion='distance')
```
### Visualize with IDendro

```python
import idendro
#wrap clustering outputs / parameters into a container
cl_data = idendro.ClusteringData(
    linkage_matrix = linkage_matrix, 
    cluster_assignments = flat_clusters, 
    threshold = threshold
)

#instantiate idendro object with default formatting
idd = idendro.IDendro()

#pass clustering information
idd.set_cluster_info(cl_data)

#create a dendrogram object
dendrogram = idd.create_dendrogram(truncate_mode='level', p=10)

#plot in Altair
from idendro.targets.altair import to_altair

to_altair(dendrogram=dendrogram, height=300, width=700)
```