<!-- Visualize historical AQI values -->
(function() {
    const data = JSON.parse(document.getElementById("historical_json").textContent);

    let datesArray = [],
        aqiArray = [];

    for (let i in data) {
        data[i].date = new Date(data[i].date);
        data[i].date.setHours(0,0,0,0);
        datesArray.push(data[i].date)
        aqiArray.push(data[i].aqi)
    }
    // console.log(data);

    const margin = {top: 30, right: 20, bottom: 30, left: 26},
        height = 300 - margin.top - margin.bottom,
        width = 400 - margin.left - margin.right;

    // Create scales
    let y = d3.scaleLinear()
        .domain(d3.extent(aqiArray))
        .range([0, height]);

    let x = d3.scaleTime()
        .domain(d3.extent(datesArray))
        .range([0, width]);

    let yAxisScale = d3.scaleLinear()
        .domain(d3.extent(aqiArray))
        .range([height, 0]);

    // Create Axis
    let yAxis = d3.axisLeft(yAxisScale).tickFormat( x => {if (Math.floor(x) == x) { return x; }});
    let xAxis = d3.axisBottom(x).tickFormat(d3.timeFormat("%m/%d")).ticks(datesArray.length);

    // Add SVG element to DOM
    let svg = d3.select("#historical .chart").append("svg")
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        .classed("svg-content", true);

    // Add axis to chart
    svg.append("g").attr("class", "axis y")
        .attr("transform", `translate(${margin.left}, ${margin.top})`)
        .call(yAxis);
    svg.append("g").attr("class", "axis x")
        .attr("transform", `translate(${margin.left}, ${height + margin.top})`)
        .call(xAxis);
    d3.selectAll("text")
        .attr("font-family", "Roboto")
        .attr("font-size", "1em");

    // Create path generator
    let line = d3.line()
        .x(d => x(d.date))
        .y(d => yAxisScale(d.aqi));

    // Add path to chart
    let path = svg.append("g").attr("class", "chart-line")
        .attr("transform", `translate(${margin.left}, ${margin.top})`)
        .append("path").attr("d", line(data))
        .attr("fill", "none")
        .attr("stroke", "rgba(255,255,255,.4)")
        .attr("stroke-width", 3);

    // Add circle nodes to chart
    let circles = svg.append("g").attr("class", "nodes")
        .attr("width", width)
        .attr("height", height)
        .attr("transform", `translate(${margin.left} ${margin.top})`)
        .selectAll("circle")
        .data(data)
        .enter().append("circle")
            .attr("cx", (d,i) => x(d.date))
            .attr("cy", (d,i) => height - y(d.aqi))
            .attr("r", "4")
            .attr("fill", "#efefef");

    // Animate path
    let path_length = path.node().getTotalLength();
    path.attr("stroke-dasharray", `${path_length} ${path_length}`)
        .attr("stroke-dashoffset", path_length)
        .transition()
            .duration(2000)
            .ease(d3.easeCubicOut)
            .attr("stroke-dashoffset", 0);

    // Add tooltip element to DOM
    let tooltip = d3.select('body')
        .append("div")
        .attr("class", "tooltip");

    // Tooltip event handlers
    circles.on('mouseover', function(event, d) {
        const e = circles.nodes();
        const i = e.indexOf(this);

        let the_date = "";
        if (i === e.length - 1)
            the_date = "Current";
        else
            the_date = `${d.date.getMonth() + 1}/${d.date.getDate()} peak`;

        d3.select(".tooltip")
            .classed("show", true)
            .html(`${the_date} AQI: <span>${d.aqi}</span>`)
            .style("top", `${event.pageY - 50}px`)
            .style("left", `${event.pageX - 50}px`)

        d3.select(this)
            .attr("r", 5);

    })
    .on('mouseout', function() {
        tooltip.classed("show", false)

        d3.select(this)
            .attr("r", 4);
    })
    .on('mousemove', function(event, d) {
        d3.select(".tooltip")
            .style("top", `${event.pageY - 50}px`)
            .style("left", `${event.pageX - 50}px`)
    });


})();