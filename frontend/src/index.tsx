import { Streamlit, RenderData } from "streamlit-component-lib"
import * as d3 from 'd3'

interface AxisLabel {
    x: number
    label: string
    labelsize: number
}

interface ClusterLink {
    x: number[]
    y: number[]
    fillcolor: string
    size: number
}

interface ClusterNode {
    x: number
    y: number
    edgecolor: string
    fillcolor: string
    label: string
    hovertext: Object[] | string
    size: number
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

interface plot extends d3.Selection<SVGGElement, unknown, HTMLElement, any> {
    
}

function create_container(dimensions: Dimensions): plot {

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

function create_axis(plot: plot, dimensions: Dimensions, dendrogram: Dendrogram) {

    //create X-axis
    var xScale = d3.scaleLinear()        
    xScale.domain(dendrogram.x_limits).range([0, dimensions.innerWidth])
    var xAxis = d3.axisBottom(xScale)
    
    //create y-axis
    var yScale = d3.scaleLinear()
    yScale.domain(dendrogram.y_limits).range([dimensions.innerHeight, 0])
    var yAxis = d3.axisLeft(yScale)

    //add X-axis to plot
    let xg = plot.append("g")
        .attr("id", "x-axis-lines")            
        .attr("transform", "translate(0," + dimensions.innerHeight + ")")
        .call(xAxis)

    //add Y-axis to plot
    let yg = plot.append("g")
    .attr("id", "y-axis-lines")            
    //.attr("transform", "translate(" + padding.left + ",0)")
    .call(yAxis)
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

    var dendrogram: Dendrogram = data.args['data']
    let margin: Margin = { top: 20, right: 10, bottom: 20, left: 50 }    
    let dimensions: Dimensions = {
        height:  data.args['height'],
        width: data.args['width'],
        margin: margin,
        innerHeight: 0,
        innerWidth: 0,
        orientation: data.args['orientation']
    }
    dimensions.innerHeight = dimensions.height - dimensions.margin.top - dimensions.margin.bottom
    dimensions.innerWidth = dimensions.width - dimensions.margin.left - dimensions.margin.right
    
    let plot = create_container(dimensions)
    create_axis(plot, dimensions, dendrogram)

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
