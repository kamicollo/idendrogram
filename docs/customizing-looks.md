# Customizing colors

# Customizing leaf axis labels

##### Customizing leaf axis labels

        `leaf_label_func` should return the leaf label of the linkage ID to be used for the axis labels.
        Two convenience implementations are provided:

        - `idendro.callbacks.counts` returns counts of observations represented by the linkage ID. This is the default. 
        - `idendro.callbacks.cluster_labeller(fmt_string=[..])` returns a callable that returns label only for the first leaf in the cluster, 
        leaving other labels empty. See idendro.callbacks.cluster_labeller for details.

        ##### node_label_func (Customizing node text labels)
        
        `node_label_func` should return the label to be used for the nodes displayed. 
        The default used is `idendro.callbacks.cluster_assignments` which returns flat cluster ID 
        if the linkage ID corresponds to the flat cluster and empty label otherwise.

        ##### node_hover_func (Customizing tooltips)
        
        `node_hover_func` should return a dictionary of key:value pairs that will be displayed in a tooltip.
        The default used is `idendro.callbacks.default_hover` that displays the linkage ID and the # of observations associated with this linkage ID

# Customising node labels

# Customising tooltips