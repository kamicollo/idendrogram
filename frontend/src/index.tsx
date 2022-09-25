import { Streamlit, RenderData } from "streamlit-component-lib"
import * as d3 from 'd3'
import * as userfuncs from './userfuncs'

interface AxisLabel {
    x: number
    label: string
    labelsize: number
}

interface Coord {
    x: number
    y: number
}

interface ClusterLink {
    x: number[]
    y: number[]
    fillcolor: string
    size: number
    data: Coord[]
}

interface ClusterNode {
    x: number
    y: number
    edgecolor: string
    fillcolor: string
    label: string
    hovertext: Object[] | string
    radius: number
    labelsize: number
    labelcolor: string

}

interface Dendrogram {
    axis_labels: AxisLabel[]
    links: ClusterLink[]
    nodes: ClusterNode[]
    x_limits: [number, number]
    y_limits: [number, number]
}

interface Dimensions {
    margin: Margin
    height: number
    width: number
    innerHeight: number
    innerWidth: number,
    orientation: Orientation
}

enum Orientation {
    top = "top",
    bottom = "bottom",
    right = "right",
    left = "left"
}

interface Margin {
    top: number
    right: number
    bottom: number
    left: number
}

interface plot extends d3.Selection<SVGGElement, unknown, HTMLElement, any> {}

interface scaleLinear extends d3.ScaleLinear<number, number, never> {}

interface scaleLog extends d3.ScaleSymLog<number, number, number | undefined> {}

function create_container(dimensions: Dimensions): plot {


    if (d3.select("#idendro")) {
        d3.select("#idendro").remove()
    }
    // append svg element to the body of the page
    // set dimensions and position of the svg element
    let svg = d3
        .select("body")
        .append("svg")
        .attr("id", "idendro")
        .attr("width", dimensions.width)
        .attr("height", dimensions.height)

    let plot = svg.append("g")
        .attr("transform", "translate(" + dimensions.margin.left + "," + dimensions.margin.top + ")")
        .attr("id", "idendro-container");

    return plot
}

function create_axis(plot: plot, dimensions: Dimensions, dendrogram: Dendrogram, scale_type: string) {

    let label_limits = dendrogram.x_limits
    let value_limits = dendrogram.y_limits

    let label_range, value_range = [0, 0]
    let label_axis_func, value_axis_func: CallableFunction
    let label_axis_transform = [0, 0]
    let value_axis_transform = [0, 0]

    //handle orientation impact on scale ranges & positioning
    if (dimensions.orientation === Orientation.top || dimensions.orientation === Orientation.bottom) {
        label_range = [0, dimensions.innerWidth]
        value_axis_func = d3.axisLeft
        value_axis_transform = [0, 0]
        if (dimensions.orientation === Orientation.top) {
            value_range = [dimensions.innerHeight, 0]
            label_axis_func = d3.axisBottom
            label_axis_transform = [0, dimensions.innerHeight]
        } else {
            value_range = [0, dimensions.innerHeight]
            label_axis_func = d3.axisTop
        }
    } else {
        value_axis_func = d3.axisBottom
        label_range = [dimensions.innerHeight, 0]
        value_axis_transform = [0, dimensions.innerHeight]
        if (dimensions.orientation === Orientation.left) {
            value_range = [dimensions.innerWidth, 0]
            label_axis_func = d3.axisRight
            label_axis_transform = [dimensions.innerWidth, 0]
        } else {            
            value_range = [0, dimensions.innerWidth]
            label_axis_func = d3.axisLeft            
        }
    }

    //get label-axis positions and labels
    let label_axis_pos = dendrogram.axis_labels.map((x) => x.x)
    let label_axis_label = dendrogram.axis_labels.map((x) => x.label)

    //create label-axis
    let labelScale: scaleLinear | scaleLog
    labelScale = d3.scaleLinear()
        .domain(label_limits).range(label_range)

    let labelAxisGenerator = label_axis_func(labelScale)
        .tickValues(label_axis_pos)
        .tickFormat((d, i) => label_axis_label[i])
        .tickSize(3)

    plot.append("g")
        .attr("id", "label-axis")
        .attr("transform", "translate(" + label_axis_transform[0] + "," + label_axis_transform[1] + ")")
        .call(labelAxisGenerator)

    //create value-axis
    let valueScale: scaleLinear | scaleLog

    if (scale_type === 'log') {
        valueScale = d3.scaleSymlog().constant(1)
    } else {
        valueScale = d3.scaleLinear()
    }
    
    valueScale.domain(value_limits)
    valueScale.range(value_range)


    let valueAxisGenerator = value_axis_func(valueScale)

    plot.append("g")
        .attr("id", "value-axis")
        .attr("transform", "translate(" + value_axis_transform[0] + "," + value_axis_transform[1] + ")")
        .call(valueAxisGenerator)
    
    return [labelScale, valueScale]
}

function draw_links(link_container: plot, links: ClusterLink[], xScale: scaleLinear | scaleLog, yScale: scaleLinear | scaleLog) {

    link_container.selectAll(".link")
      .data(links)
      .enter()
      .append("path")
        .attr("fill", "none")
        .attr("stroke", (d) => d.fillcolor)
        .attr("stroke-width", 1.5)
        .attr("class", "link")
        .attr("d", function(d){
          return d3.line<Coord>()
            .x((d) => xScale(d.x) || 0)
            .y((d) => yScale(d.y) || 0)
            (d.data)
        })

}

function draw_nodes(node_container: plot, nodes: ClusterNode[], xScale: scaleLinear | scaleLog, yScale: scaleLinear | scaleLog) {

    var elem = node_container.selectAll(".node")
        .data(nodes)
        .enter()        
	    .append("g")
	    .attr("transform", function(d){return "translate("+ xScale(d.x) +"," + yScale(d.y) + ")"})
        .attr("class", "node")
    
    elem.append("circle")
        .attr("fill", (d) => d.fillcolor)
        .attr("stroke", (d) => d.edgecolor)
        .attr("stroke-width", 1.5)        
        .attr('r', (d) => d.radius)  

    elem.append("text")
          .attr("dx", (d) => 0)
          .text((d) => d.label)
          .attr("fill", (d) => d.labelcolor)
          .attr("font-size", (d) => d.labelsize)
          .attr("alignment-baseline", "central")
          .attr("text-anchor", "middle")
          .attr("font-weight", "bold")
}

/* // Add a click handler to our button. It will send data back to Streamlit.
let numClicks = 0

button.onclick = function(): void {
  // Increment numClicks, and pass the new value back to
  // Streamlit via `Streamlit.setComponentValue`.
  numClicks += 1
  Streamlit.setComponentValue(numClicks)
} */


/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event: Event): void {
    // Get the RenderData from the event
    const data = (event as CustomEvent<RenderData>).detail

    let dendrogram: Dendrogram = data.args['data']
    let scaleType = data.args['scale_type']
    console.log(dendrogram)
    let margin: Margin = { top: 50, right: 50, bottom: 50, left: 50 }
    let label_margin_size = data.args['label_margin']
    let dimensions: Dimensions = {
        height: data.args['height'],
        width: data.args['width'],
        margin: margin,
        innerHeight: 0,
        innerWidth: 0,
        orientation: data.args['orientation']
    }

    let margin_map = { 'top': Orientation.bottom, 'bottom': Orientation.top, 'left': Orientation.right, 'right': Orientation.left }
    let label_margin: Orientation = margin_map[dimensions.orientation]

    dimensions.margin[label_margin] = label_margin_size
    dimensions.innerHeight = dimensions.height - dimensions.margin.top - dimensions.margin.bottom
    dimensions.innerWidth = dimensions.width - dimensions.margin.left - dimensions.margin.right

    let plot = create_container(dimensions)
    let scales = create_axis(plot, dimensions, dendrogram, scaleType)

    let xScale: scaleLinear | scaleLog
    let yScale: scaleLinear | scaleLog

    if (dimensions.orientation === Orientation.top || dimensions.orientation === Orientation.bottom) {        
        xScale = scales[0]
        yScale = scales[1]
        dendrogram.links.forEach(link => {
            link.data = link.x.map(function(x, i) { return {'x': x, 'y': link.y[i]} })
        });        
    } else {
        yScale = scales[0]
        xScale = scales[1]        
        dendrogram.links.forEach(link => {
            link.data = link.x.map(function(x, i) { return {'y': x, 'x': link.y[i]} })            
        });
        dendrogram.nodes.forEach(node => {
            let x = node.x
            node.x = node.y
            node.y = x            
        });
    }

    let link_container = plot.append('g').attr("class", "link-container")
    let node_container = plot.append('g').attr("class", "node-container")
    
    draw_links(link_container, dendrogram.links, xScale, yScale)
    draw_nodes(node_container, dendrogram.nodes, xScale, yScale)

    userfuncs.postprocess(d3, dimensions, dendrogram)
    Streamlit.setFrameHeight()
}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight()
