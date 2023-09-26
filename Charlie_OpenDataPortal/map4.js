document.addEventListener("DOMContentLoaded", function() {
    const svg = d3.select("#map4");
    const width = +svg.attr("width");
    const height = +svg.attr("height");

    // Define the zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([1, 10])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    // Apply the zoom behavior to the SVG
    svg.call(zoom);

    // append a group element to SVG
    const g = svg.append('g');

    // Append a div to body for the tooltip
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    Promise.all([
        d3.json('data/suburbs_3395_parks.geojson'),

    ]).then(([areas_parks]) => {

        const color = d3.scaleSequentialLog(d3.interpolateViridis)
            .domain([
                d3.min(areas_parks.features, d => Math.max(1e-6, d.properties.parks_percentage)),
                d3.max(areas_parks.features, d => d.properties.parks_percentage)
            ]);

        const legend = svg.append("g")
            .attr("class", "legend")
            .attr("transform", "translate(" + (width - 300) + "," + 30 + ")");

        const legendScale = d3.scaleLinear()
            .domain(color.domain())
            .range([0, 300]);

        // const legendAxis = d3.axisBottom(legendScale)
        //     .ticks(2)  // Reduce the number of ticks to prevent overlapping
        //     .tickFormat(d => d3.format(".2s")(Math.pow(100, d)));
        //
        // legend.call(legendAxis);

        legend.selectAll("rect")
            .data(color.ticks().map((t, i, arr) => ({
                value: t,
                width: i < arr.length - 1 ? legendScale(Math.log10(arr[i + 1])) - legendScale(Math.log10(t)) : legendScale(legendScale.domain()[1]) - legendScale(Math.log10(t))
            })))
            .enter().append("rect")
            .attr("height", 8)
            .attr("x", d => legendScale(Math.log10(d.value)))
            .attr("width", d => d.width)
            .attr("fill", d => color(d.value));

        // Projection for the other datasets
        const otherProjection = d3.geoIdentity()
            .reflectY(true)
            .translate([width / 2, height / 2])
            .fitExtent([[0, 0], [width, height]], {
                type: "FeatureCollection",
                features: [...areas_parks.features]
            });

        const path = d3.geoPath(otherProjection);

        //Suburb and Parks
        g.selectAll('path.suburb_park')
            .data(areas_parks.features)
            .enter()
            .append('path')
            .attr('d', path)
            .attr('class', 'areas_parks')
            .attr('fill', d => color(d.properties.parks_percentage))
            .attr('stroke', 'black')
            .on('mouseover', function(event, d) {
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html("Suburb: " + d.properties.OFC_SBRB_NAME + "<br/>Parks Percentage: " + d.properties.parks_percentage.toFixed(1) + "%")
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY + 10) + "px");
            })
            .on('mousemove', function(event, d) {
                tooltip
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY + 10) + "px");
            })
            .on('mouseout', function(d) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });
    });
});

