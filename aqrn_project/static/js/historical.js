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
    console.log(data);

    const margin = {top: 30, right: 20, bottom: 30, left: 30},
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
    let yAxis = d3.axisLeft(yAxisScale);

    let xAxis = d3.axisBottom(x).tickFormat(d3.timeFormat("%m/%d")).ticks(6);

    let svg = d3.select("#historical").append("svg")
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        .classed("svg-content", true)
        ;

    let circles = svg.append("g").attr("class", "nodes")
        .attr("width", width)
        .attr("height", height)
        .attr("transform", `translate(${margin.left} ${margin.top})`)
        .selectAll("circle")
        .data(data)
        .enter().append("circle")
            .attr("cx", (d,i) => x(d.date))
            .attr("cy", (d,i) => height - y(d.aqi))
            .attr("r", "3")
            .attr("fill", "#efefef");


    svg.append("g").attr("class", "axis y")
        .attr("transform", `translate(${margin.left}, ${margin.top})`)
        .call(yAxis);
    svg.append("g").attr("class", "axis x")
        .attr("transform", `translate(${margin.left}, ${height + margin.top})`)
        .call(xAxis);

    let line = d3.line()
        .x(d => x(d.date))
        .y(d => yAxisScale(d.aqi));

    let path = svg.append("g").attr("class", "chart-line")
        .attr("transform", `translate(${margin.left}, ${margin.top})`)
        .append("path").attr("d", line(data))
        .attr("fill", "none")
        .attr("stroke", "rgba(255,255,255,.4)");

    let path_length = path.node().getTotalLength();

    path.attr("stroke-dasharray", `${path_length} ${path_length}`)
        .attr("stroke-dashoffset", path_length)
        .transition()
            .duration(2000)
            .ease(d3.easeCubicOut)
            .attr("stroke-dashoffset", 0);

})();