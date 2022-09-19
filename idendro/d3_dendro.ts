function draw_dendrogram(data: any) {
    var margin = {top: 80, right: 180, bottom: 80, left: 80},
        padding = {top: 30, right: 30, bottom: 30, left: 30},
        outerWidth = 800,
        outerHeight = 600,
        innerWidth = outerWidth - margin.left - margin.right,
        innerHeight = outerHeight - margin.top - margin.bottom,
        
    var svg = d3.select("body").append("svg")

    .attr("width", outerWidth)
        .attr("height", outerHeight)
        .attr("id", "svg-" + id)

        //add a title
        svg.append("text")
        .text(chartTitle)
        .attr("id", "title-" + id)
        .attr("class", "chart-title")
        .attr("transform", "translate(" + innerWidth / 2 + "," + margin.top/2 + ")")

        //create plot container
        var plot = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
            .attr("id", "plot-" + id);

        lines = plot.append("g")
            .attr("id", "lines-" + id)        
        
        var colorScheme = d3.scaleOrdinal(d3.schemeCategory10);
        
        //create X-axis
        var xScale = d3.scaleTime()        
        var xAxis = d3.axisBottom().scale(xScale)                
        xScale.domain([d3.min(dates), d3.max(dates)])
        .range([0, innerWidth])

        const formatTime = d3.timeFormat("%b %y");
        xticks = xScale.ticks(dates.length / 3)
        xAxis.tickFormat(formatTime)
        xticks = xticks.map(formatTime)         
        

        //create y-axis
        var yAxis = d3.axisLeft().scale(yScale)
        domain_setter(yScale, d3.max(counts))
        yScale.range([innerHeight, 0])


        games = ['Catan', 'Dominion', 'Codenames', 'Terraforming Mars', 'Gloomhaven', 'Magic: The Gathering', 'Dixit', 'Monopoly']
        last_entries = data[data.length - 1]
        

        games.forEach((game, i) => {
            ref = game + "=count"
            
            //add lines
            lines.append("path")
                .datum(data)  
                .attr("fill", "none")
                .attr("stroke", colorScheme(i))
                .attr("stroke-width", 1.5)
                .attr("d", d3.line()
                    .x(function(d) { return xScale(d.date) })
                    .y(function(d) { return yScale(d[ref]) })
            )

            //add labels
            x = xScale(new Date(last_entries.date)) + 10
            y = yScale(parseInt(last_entries[ref]))
            lines.append("text")
            .text(game)
            .attr("transform", "translate(" + x + "," + y + ")")
            .attr("class", "line-legend")    
            .attr("stroke", colorScheme(i))
            .attr("stroke-width", 0.5)

        });

        //add X-axis to plot
        xg = plot.append("g")
            .attr("id", "x-axis-" + id)            
            .attr("transform", "translate(0," + innerHeight + ")")
            .call(xAxis)            
        
        xg.append("text")            
            .attr("transform", "translate(" + innerWidth / 2 + "," + (margin.bottom - 20) + ")")
            .text("Month")            
            .attr("class", "axis-label")
            .attr("text-anchor", "middle")
            .attr("fill", "currentColor")

        

        //add Y-axis to plot
        yg = plot.append("g")
            .attr("id", "y-axis-" + id)            
            //.attr("transform", "translate(" + padding.left + ",0)")
            .call(yAxis)
        
        // Add the text label for X Axis
        yg.append("text")            
            .attr("transform", "translate(-" + (margin.left - 20) +  "," + innerHeight / 2 + ")  rotate(-90)")
            .text("Num of Ratings")            
            .attr("class", "axis-label")
            .attr("text-anchor", "middle")
            .attr("fill", "currentColor")
}