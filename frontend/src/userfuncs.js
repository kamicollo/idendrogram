export function postprocess(d3, dimensions, dendrogram) {
    console.log('I run after every render!')

    /* Sample script to rotate the labels */
    if (dimensions.orientation === 'top') {
        
        d3.selectAll('#label-axis')
        .selectAll("text")	
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", "-.3em")
        .attr("transform", "rotate(-90)")        
    }
    

}