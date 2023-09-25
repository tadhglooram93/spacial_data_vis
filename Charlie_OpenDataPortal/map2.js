document.addEventListener("DOMContentLoaded", function() {
    const svg = d3.select("#map2");
    const width = +svg.attr("width");
    const height = +svg.attr("height");

    // Define the zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([1, 500])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    // Apply the zoom behavior to the SVG
    svg.call(zoom);

    // append a group element to SVG
    const g = svg.append('g');

    Promise.all([
        d3.json('data/regions_3395.geojson'),
        d3.json('data/parks_3395.geojson'),
        d3.json('data/waters_3395.geojson'),
        d3.json('data/bert_3395_circles_inpark.geojson'),
        d3.json('data/bert_3395_circles_notinpark.geojson'),
        d3.json('data/bert_3395.geojson')

    ]).then(([regionsData, parks, water, brt_buffer_inpark,brt_buffer_notinpark,brt_stops]) => {

        // projection for regions
        const regionsProjection = d3.geoIdentity()
            .reflectY(true)
            .translate([width / 2, height / 2])
            .scale([1, -1])
            .fitExtent([[0, 0], [width, height]], regionsData);

        const regionsPath = d3.geoPath(regionsProjection);

        // Draw Paths
        // Regions
        g.selectAll('path.regions')
            .data(regionsData.features)
            .enter()
            .append('path')
            .attr('d', regionsPath)
            .attr('class', 'regions')
            .attr('fill', 'none')
            .attr('stroke', 'black')

        // Projection for the other datasets
        const otherProjection = d3.geoIdentity()
            .reflectY(true)
            .translate([width / 2, height / 2])
            .fitExtent([[0, 0], [width, height]], {
                type: "FeatureCollection",
                features: [...parks.features, ...water.features, ...brt_buffer_inpark.features,...brt_buffer_notinpark.features]
            });

        const path = d3.geoPath(otherProjection);

        // Water in Parks
        g.selectAll('path.parks')
            .data(parks.features)
            .enter()
            .append('path')
            .attr('d', path)
            .attr('class', 'parks')

        // Water not in water - projection doesn't seem to work withouth it (making transparent
        g.selectAll('path.water')
            .data(water.features)
            .enter()
            .append('path')
            .attr('d', path)
            .attr('class', 'water')

        // brt buffer_notinpark
        g.selectAll('path.brt_buffer_notinpark')
            .data(brt_buffer_notinpark.features)
            .enter()
            .append('path')
            .attr('d', path)
            .attr('class', 'brt_buffer_notinpark')

        // brt buffer_inpark
        g.selectAll('path.brt_buffer_inpark')
            .data(brt_buffer_inpark.features)
            .enter()
            .append('path')
            .attr('d', path)
            .attr('class', 'brt_buffer_inpark')

        // bert
        g.selectAll('circle.bert')
            .data(brt_stops.features)
            .enter()
            .append('circle')
            .attr('cx', d => otherProjection(d.geometry.coordinates)[0]) // x coordinate
            .attr('cy', d => otherProjection(d.geometry.coordinates)[1]) // y coordinate
            .attr('r', 0.01) // radius of the circle
            .attr('class', 'bert');


    });
    createLegend2()
});
function createLegend2() {
    const legendContainer = d3.select('#legend-container2');

    const categories = [
        { color: '#48b07b', label: 'Parks', shape: 'rect' },
        { color: '#F88379', label: 'bus stops within 10m of park', shape: 'circle' },
        { color: '#E5E4E2', label: 'Other bus stops', shape: 'circle' }
    ];

    const legendItemHeight = 30; // Adjusted the height to better fit circles
    const legendItemWidth = 20;
    const textOffset = 5;

    const legendSvg = legendContainer.append('svg')
        .attr('width', 220)
        .attr('height', categories.length * legendItemHeight);

    const legendItems = legendSvg.selectAll('g')
        .data(categories)
        .enter()
        .append('g')
        .attr('transform', (d, i) => `translate(0,${i * legendItemHeight})`);

    legendItems.each(function (d) {
        const item = d3.select(this);

        if (d.shape === 'rect') {
            item.append('rect')
                .attr('width', legendItemWidth)
                .attr('height', legendItemHeight-10)
                .attr('fill', d.color);
        } else { // 'circle'
            item.append('circle')
                .attr('cx', legendItemWidth / 2)
                .attr('cy', legendItemHeight / 2)
                .attr('r', legendItemWidth / 2)
                .attr('fill', d.color);

            // Append smaller white dot in the middle of the circle
            item.append('circle')
                .attr('cx', legendItemWidth / 2)
                .attr('cy', legendItemHeight / 2)
                .attr('r', legendItemWidth / 6) // Smaller radius for the white dot
                .attr('fill', 'white');
        }
    });

    // Append text for each legend item
    legendItems.append('text')
        .attr('x', legendItemWidth + textOffset)
        .attr('y', legendItemHeight / 2.2)
        .attr('dy', '0.35em')
        .text(d => d.label);
}
