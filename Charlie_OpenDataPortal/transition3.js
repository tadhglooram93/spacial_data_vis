document.addEventListener("DOMContentLoaded", function() {
    const transitionBtn = document.getElementById('transitionBtn3');

    transitionBtn.addEventListener('click', function() {
        remove_elements_move_brts();

    });
});

function remove_elements_move_brts() {
    const svg = d3.select("#map3");
    const legendContainer = d3.select('#legend-container3'); // Select the legend container div
    const width = +svg.attr("width");
    const height = +svg.attr("height");

    // Remove regions and parks with a transition
    svg.selectAll('.regions, .parks')
        .transition()
        .duration(500) // Transition duration in milliseconds
        .style('opacity', 0) // Fade out the elements
        .remove() // Remove the elements after the transition

    legendContainer.selectAll('g')
        .transition()
        .duration(500) // Transition duration in milliseconds
        .style('opacity', 0) // Fade out the elements
        .remove() // Remove the elements after the transition

    // move  points to one place
    // Select and move brt_buffer_inpark circles to the column
    svg.selectAll('.brt_buffer_inpark2')
        .transition()
        .delay(1000)
        .duration(1500)
        .attr('cx', width *0.4)
        .attr('cy', height*0.1)
        .attr('r',8);

    svg.selectAll('.brt_buffer_notinpark2')
        .transition()
        .delay(1000)
        .duration(1500)
        .attr('cx', width *0.45)
        .attr('cy', height*0.1)
        .attr('r',8)

    // add text to explain
    svg.append('text')
        .attr('id', 'explanation-text')
        .attr('x', width *0.5)
        .attr('y', height*0.03)
        .attr('text-anchor', 'middle')
        .text("Let's plot each stop on a line by their shortest distance to a park:")
        .style('opacity', 0)
        .transition()
        .delay(2500)
        .duration(1000)
        .style('opacity', 1)


    // Load the bert_3395_distance.geojson file
    d3.json('data/bert_3395_distance.geojson').then((distanceData) => {
        // Create a map of OBJECTID to distance for bert_3395_distance
        const distanceMap = new Map();
        distanceData.features.forEach((distanceFeature) => {
            const objectId = distanceFeature.properties.OBJECTID;
            const distance = distanceFeature.properties.distance;
            distanceMap.set(objectId, distance);
        });

        // Find the minimum and maximum distances
        const minDistance = d3.min(distanceData.features, (feature) => feature.properties.distance);
        const maxDistance = d3.max(distanceData.features, (feature) => feature.properties.distance);

        // Define the coordinates for the line endpoints based on min and max distances
        const lineData = [
            { distance: minDistance, x: 50, y: 500 },
            { distance: maxDistance, x: 700, y: 500 },
        ];

        // Append the line to the SVG
        svg.append('line')
            .attr('x1', lineData[0].x)
            .attr('y1', lineData[0].y)
            .attr('x2', lineData[1].x)
            .attr('y2', lineData[1].y)
            .attr('stroke', 'black')
            .attr('stroke-opacity', 0)
            .transition() // Start a transition
            .delay(2500) // Delay the transition
            .duration(1000) // Set the duration of the transition (adjust as needed)
            .attr('stroke-opacity', 1);

        // Calculate the positions for x ticks at 25% intervals
        const xTicks = [minDistance, minDistance + (maxDistance - minDistance) * 0.25, minDistance + (maxDistance - minDistance) * 0.5, minDistance + (maxDistance - minDistance) * 0.75, maxDistance];

        // Append x ticks to the SVG
        svg.selectAll('.x-tick')
            .data(xTicks)
            .enter()
            .append('line')
            .attr('class', 'x-tick')
            .attr('x1', function(d) {
                return d3.scaleLinear()
                    .domain([minDistance, maxDistance])
                    .range([lineData[0].x, lineData[1].x])(d);
            })
            .attr('x2', function(d) {
                return d3.scaleLinear()
                    .domain([minDistance, maxDistance])
                    .range([lineData[0].x, lineData[1].x])(d);
            })
            .attr('y1', lineData[0].y - 5) // Adjust the y-coordinate for the ticks
            .attr('y2', lineData[0].y + 5) // Adjust the y-coordinate for the ticks
            .attr('stroke', 'black')
            .attr('stroke-opacity', 0)
            .transition() // Start a transition
            .delay(2500) // Delay the transition
            .duration(1000) // Set the duration of the transition (adjust as needed)
            .attr('stroke-opacity', 1);


        const formatDistance = d3.format(',.0f'); // Format as integer with comma separators

        // Calculate the positions for x labels at 25% intervals
        const xLabels = [
            { distance: minDistance, x: lineData[0].x, y: lineData[0].y + 35 },
            { distance: minDistance + (maxDistance - minDistance) * 0.25, x: lineData[0].x + (lineData[1].x - lineData[0].x) * 0.25, y: lineData[0].y + 35 },
            { distance: minDistance + (maxDistance - minDistance) * 0.5, x: lineData[0].x + (lineData[1].x - lineData[0].x) * 0.5, y: lineData[0].y + 35 },
            { distance: minDistance + (maxDistance - minDistance) * 0.75, x: lineData[0].x + (lineData[1].x - lineData[0].x) * 0.75, y: lineData[0].y + 35 },
            { distance: maxDistance, x: lineData[1].x, y: lineData[1].y + 35 }
        ];

        // Append x labels to the SVG
        svg.selectAll('.x-label')
            .data(xLabels)
            .enter()
            .append('text')
            .attr('class', 'x-label')
            .attr('x', function(d) {
                return d.x;
            })
            .attr('y', function(d) {
                return d.y;
            })
            .attr('text-anchor', 'middle')
            .text(function(d) {
                return `${formatDistance(d.distance)} meters`;
            })
            .style('opacity', 0) // Start with opacity 0
            .transition() // Start a transition
            .delay(2500) // Delay the transition
            .duration(1000) // Set the duration of the transition (adjust as needed)
            .style('opacity', 1)

        // Append a text label beneath the x-axis labels
        svg.append('text')
            .attr('x', width / 2) // Position it in the middle of the SVG
            .attr('y', lineData[0].y + 60) // Adjust the y-coordinate as needed
            .attr('text-anchor', 'middle')
            .text('Shortest Distance to a Park')// Add your x-axis label text
            .style('opacity', 0) // Start with opacity 0
            .transition() // Start a transition
            .delay(2500) // Delay the transition
            .duration(1000) // Set the duration of the transition (adjust as needed)
            .style('opacity', 1)

        // Move the existing circles to the coordinates that match the distance
        svg.selectAll('.brt_buffer_notinpark2')
            .transition()
            .delay(5000) // Delay the transition
            .duration(function(d) {
                const objectIdLeft = d.properties.OBJECTID_left;
                if (distanceMap.has(objectIdLeft)) {
                    const distance = parseInt(distanceMap.get(objectIdLeft)); // Convert distance to an integer

                    // Calculate the duration of the transition based on distance and speed
                    const speed = 1.2; // Adjust the speed factor as needed
                    return distance * speed;
                }
                // Return a default duration if distance data is not available
                return 5000; // Default duration in milliseconds
            })
            .attr('cx', function (d) {
                const objectIdLeft = d.properties.OBJECTID_left;
                if (distanceMap.has(objectIdLeft)) {
                    const distance = distanceMap.get(objectIdLeft);

                    // Calculate the x-coordinate based on the distance
                    return d3.scaleLinear()
                        .domain([minDistance, maxDistance])
                        .range([lineData[0].x, lineData[1].x])(distance);
                }
                // Return the existing cx value if distance data is not available
                return parseFloat(d3.select(this).attr('cx'));
            })
            .attr('cy', lineData[0].y)

        // Move the existing circles to the coordinates that match the distance
        svg.selectAll('.brt_buffer_inpark2')
            .transition()
            .delay(5000) // Delay the transition
            .duration(function(d) {
                const objectIdLeft = d.properties.OBJECTID_left;
                if (distanceMap.has(objectIdLeft)) {
                    const distance = parseInt(distanceMap.get(objectIdLeft));

                    // Calculate the duration of the transition based on distance and speed
                    const speed = 500; // Adjust the speed factor as needed
                    return distance * speed;
                }
                // Return a default duration if distance data is not available
                return 5000; // Default duration in milliseconds
            })
            .attr('cx', function (d) {
                const objectIdLeft = d.properties.OBJECTID_left;
                if (distanceMap.has(objectIdLeft)) {
                    const distance = distanceMap.get(objectIdLeft);

                    // Calculate the x-coordinate based on the distance
                    return d3.scaleLinear()
                        .domain([minDistance, maxDistance])
                        .range([lineData[0].x, lineData[1].x])(distance);
                }
                // Return the existing cx value if distance data is not available
                return parseFloat(d3.select(this).attr('cx'));
            })
            .attr('cy', lineData[0].y)


        meltCirclesAndCreateHistogram()

        function meltCirclesAndCreateHistogram() {
            const svg = d3.select("#map3");
            const explanationText = d3.select('#explanation-text');

            explanationText
                .transition()
                .delay(10000)
                .duration(1000)
                .style('opacity', 0) // Fade out the existing text
                .on('end', function() {
                    // Remove the existing text after the fade-out animation
                    explanationText.remove();

                    // Create and animate a new text element
                    svg.append('text')
                        .attr('class', 'explanation-text')
                        .attr('id', 'explanation-text')
                        .attr('x', width * 0.5)
                        .attr('y', height * 0.03)
                        .attr('text-anchor', 'middle')
                        .text("Hmm... lot's of overlap, let's turn this into a histogram!")
                        .style('opacity', 0)
                        .transition()
                        .duration(1000)
                        .style('opacity', 1);
                });

            // Select all circles and melt them into the line
            svg.selectAll('.brt_buffer_notinpark2, .brt_buffer_inpark2')
                .transition()
                .delay(13000)
                .duration(1500) // Transition duration in milliseconds
                .attr('r', 0) // Reduce the radius to 0
                .style('opacity', 0) // Fade out the elements
                .on('end', function() {
                    // After the animation, set the radius to 1 to keep the circles
                    d3.select(this).remove();

                    // Create a histogram from the line
                    createHistogram();
                });
        }



        function createHistogram() {
            // Define the number of bins and bin size
            const numBins = 800 / 50; // 800 is the width of the SVG, and 50 is the bin size
            const binSize = 50;
            const svg = d3.select("#map3");

            // Create an array of distances from minDistance to maxDistance
            const distances = d3.range(minDistance, maxDistance + binSize, binSize);

            // Create a histogram function
            const histogram = d3.histogram()
                .domain([minDistance, maxDistance])
                .thresholds(distances);

            // Compute the histogram data
            const histogramData = histogram(distanceData.features.map((feature) => feature.properties.distance));

            // Create scales for the histogram
            const xScale = d3.scaleLinear()
                .domain([minDistance, maxDistance])
                .range([lineData[0].x, lineData[1].x]);

            const yScale = d3.scaleLinear()
                .domain([0, d3.max(histogramData, (d) => d.length)])
                .range([lineData[0].y,lineData[0].x]);

            // Create the bars of the histogram
            svg.selectAll('.bar')
                .data(histogramData)
                .enter()
                .append('rect')
                .attr('class', 'bar')
                .attr('x', (d) => xScale(d.x0))
                .attr('y', [lineData[0].y]) // Start the bars at the bottom of the histogram
                .attr('width', (d) => xScale(d.x1) - xScale(d.x0))
                .attr('height', 0) // Start the bars with zero height
                .attr('fill', "#beb9db")
                .transition() // Add a transition
                .duration(3000) // Set the transition duration (adjust as needed)
                .attr('y', (d) => yScale(d.length)) // Transition the bars to their final height
                .attr('height', (d) => [lineData[0].y] - yScale(d.length)); // Transition the bars to their final height

            // Append the Y-axis to the SVG
            const yAxis = svg.append("g")
                .attr("class", "y-axis")
                .attr("transform", `translate(${lineData[0].x},0)`) // Position the Y-axis on the left of the histogram
                .call(d3.axisLeft(yScale));

            // Add text labels to the Y-axis
            yAxis.selectAll("text")
                .attr("x", -5) // Adjust the label position
                .attr("dy", -4) // Adjust the label position
                .style("text-anchor", "end");

            const explanationText = d3.select('#explanation-text');

            explanationText
                .transition()
                .delay(3000)
                .duration(1000)
                .style('opacity', 0) // Fade out the existing text
                .on('end', function() {
                    // Remove the existing text after the fade-out animation
                    explanationText.remove();

                    // Create and animate a new text element
                    svg.append('text')
                        .attr('class', 'explanation-text')
                        .attr('id', 'explanation-text')
                        .attr('x', width * 0.5)
                        .attr('y', height * 0.03)
                        .attr('text-anchor', 'middle')
                        .text("Looks like the majority of bus stops are within 200m of a park!")
                        .style('opacity', 0)
                        .transition()
                        .duration(1000)
                        .style('opacity', 1);
                });

        }
    });

}

