let margin = {top: 20, right: 5, bottom: 20, left: 5};

let totalWidth = 600
let totalHeight = 450
// effective width and height
let width = totalWidth - margin.left - margin.right,
    height = totalHeight - margin.top - margin.bottom;
let padding = 70

let svgLeft = createSVGSpace("#left");

function createSVGSpace(id){
    return d3.select(id).append('svg')
        .attr("width", totalWidth)
        .attr("height", totalHeight)
        .append("g")
        //.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
}

function drawLeftChart(data){
    // create scales for the x- and y-axes
    const xScale = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))  // Get the min and max date
        .range([padding, width - padding]);

    const yScale = d3.scaleLinear()
        // d3.min(data, d => d.population)
        .domain([0 , d3.max(data, d => d.population)])
        .range([height -padding, padding])

    let area = d3.area()
        .x(d => xScale(d.date))
        .y0(height - padding)
        .y1(d => yScale(d.population))

    // draw area
    svgLeft.append("path")
        .datum(data)
        .attr("class", "area")
        .attr("d", area);

    let boundary = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScale(d.population));

    svgLeft.append("path")
        .datum(data)
        .attr("class", "actual-boundary")
        .attr("d", boundary);

    createAxis(xScale, yScale);

    svgLeft.append("text")
        .attr("class", "x-label")
        .attr("x", -height / 2)
        .attr("y", 10 )
        .attr("transform", "rotate(-90)")
        .text("Population");

    // chart title
    svgLeft.append("text")
        .attr("class","chart-title")
        .attr("x", width/2 -30 )
        .attr("y", padding - 30)
        .text("Camp Population");

    // let tooltip = svgLeft.append("g")
    //     .attr("class", "tooltip")
    //     .style("display", "block")
    //     //.style("display", "none");

    // Create dynamic tooltips for my area chart
    let tooltip = svgLeft.append("g")
        .attr("class", "tooltips")
        .attr('transform', `translate(${padding},${padding})`);

    tooltip.append("line")
        .attr("class", "tooltip-line")
        .attr("x1",0)
        .attr("x2",0)
        .attr("y1", height - padding*2)
        .attr("y2",0)
        .attr("stroke", "black")
        .attr("stroke-width", 2)

    tooltip.append("text")
        .attr("class", "tooltip-population")
        .attr("x", 10)
        .attr("y", 10);

    tooltip.append("text")
        .attr("class", "tooltip-date")
        .attr("x", 10)
        .attr("y", 30);

    svgLeft.append("rect")
        .attr("class", "overlay")
        .attr("width", width-padding*2)
        .attr("height", height - padding * 2)
        .attr('x', padding)
        .attr('y', padding)
        .style("opacity", 0)  //invisible
        .on("mouseover", function() { tooltip.style("display", null); })
        .on("mouseout", function() { tooltip.style("display", "none"); })
        .on("mousemove", mousemove);

    let bisectDate = d3.bisector(d=>d.date).left;

    let formatDate = d3.timeFormat("%Y-%m-%d");
    function mousemove(event){
        let xPos = d3.pointer(event)[0];  // get the x position of the mouse pointer
        let dateValue = xScale.invert(xPos);  // find the equivalent date value
        let idx = bisectDate(data, dateValue, 1);  // index of date
        let datumNow = data[idx];
        console.log(datumNow)

        // Shift the whole tooltip group on the x-axis to the position of the mouse.
        tooltip.attr("transform", "translate("+ xPos +","+padding+")")
        tooltip.select(".tooltip-population").text(datumNow.population);
        tooltip.select(".tooltip-date").text(formatDate(datumNow.date));
    }

}

function createAxis(xScale, yScale){
    // plot
    let xAxis = d3.axisBottom()
        .scale(xScale)
        .tickFormat(d3.timeFormat("%b %Y")) //display the month and year in text format (e.g. April 2013).

    svgLeft.append("g")
        .attr("class", "axis x-axis")
        .attr("transform", "translate(0," + (height - padding) + ")")
        .call(xAxis)
        .selectAll(".tick text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end")
        .attr("dx", "-.5em")
        .attr("dy", ".5em")

    svgLeft.append("text")
        .attr("class", "x-label")
        .attr("x", width / 2 - 30)
        .attr("y", height)
        .text("Month and Year");

    // create and plot y-axis
    let yAxis = d3.axisLeft()
        .scale(yScale)
        .tickFormat(d3.format("d"))

    svgLeft.append("g")
        .attr("class", "axis y-axis")
        .attr("transform", "translate(" + padding + ", 0 )")
        .call(yAxis)
}

let shelters = [
    {type: "Caravans", percentage: 79.68},
    {type: "Tents and caravans", percentage: 10.81},
    {type: "Tents", percentage: 9.51}
]

function drawRightChart(data){
    let svgRight = createSVGSpace("#right");



    let shelterScale = d3.scaleBand()
        .domain(shelters.map(d => d.type))
        .range([padding, width - padding])
        .padding(0.2);

    let percentageScale = d3.scaleLinear()
        .domain([0, 100])
        .range([height - padding, padding]);

    drawBarChart(shelterScale, percentageScale, shelters, svgRight)

}

function drawBarChart(xScale, yScale, data, svg){
    let xAxis = d3.axisBottom().scale(xScale)

    svg.append("g")
        .attr("class", "axis x-axis")
        .attr("transform", "translate(0," + (height - padding) + ")")
        .call(xAxis)

    svg.selectAll("rect")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => xScale(d.type))
        .attr("y", d => yScale(d.percentage))
        .attr("width", xScale.bandwidth())
        .attr("height", d => height - padding - yScale(d.percentage))

// Add labels
    svg.selectAll("text")
        .data(data)
        .enter()
        .append("text")
        .attr("x", d => xScale(d.type) + xScale.bandwidth() / 2)
        .attr("y", d => yScale(d.percentage) )
        .attr("text-anchor", "middle")
        .text(d => d.type);

    let yAxis = d3.axisLeft()
        .scale(yScale)
        .tickFormat(d => d + "%")

    svg.append("g")
        .attr("class", "axis y-axis")
        .attr("transform", "translate(" + padding + ", 0 )")
        .call(yAxis)

    svg.append("text")
        .attr("class", "x-label")
        .attr("x", width / 2 - 30)
        .attr("y", height - 15)
        .text("Shelter Type");

    svg.append("text")
        .attr("class", "y-label")
        .attr("x", -height / 2)
        .attr("y", 10 )
        .attr("transform", "rotate(-90)")
        .text("Percentage");

    // add plot title
    svg.append("text")
        .attr("class","chart-title")
        .attr("x", width / 2 - 30)
        .attr("y", padding - 30)
        .text("Type of Shelter");

    // append labels at the top of each bar
    svg.selectAll("text.label")
        .data(data)
        .enter()
        .append("text")
        .attr("class", "bar-label")
        .attr("x", d => xScale(d.type) + xScale.bandwidth() * 0.5)
        .attr("y", d => yScale(d.percentage) - 6)  // 5 units above the bar for spacing
        .attr("text-anchor", "middle") // center the labels
        .text(d => `${d.percentage}%`)  // the text to display

}

function startDummyProgressBar() {
    var progress = 0;
    var progressBar = document.getElementById('progressBar');
    var downloadButton = document.getElementById('downloadButton');
    progressBar.style.width = progress + '%';

    var interval = setInterval(function() {
        progress += 5; // increment the progress
        progressBar.style.width = progress + '%';

        if (progress >= 100) {
            clearInterval(interval);
            downloadButton.style.display = 'block'; // show the download button
        }
    }, 1000); //update progress every 1 second
}

function downloadVideo() {
    // the URL to the video file
    var videoUrl = 'http://localhost:9000/results/test.mp4';  

    // create a temporary anchor tag to trigger the download
    var a = document.createElement('a');
    a.href = videoUrl;
    a.download = 'processed_video.mp4';  // the name we want to save the file as
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

