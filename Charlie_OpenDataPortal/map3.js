document.addEventListener("DOMContentLoaded", function() {
    const svg = d3.select("#map3");
    const width = +svg.attr("width");
    const height = +svg.attr("height");

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

        // Slect the first feature from brt_buffer_inpark or brt_buffer_notinpark
        const bufferFeature = brt_buffer_inpark.features[0]

        // Get the corresponding brt_stop
        const correspondingStop = getMatchingStop(bufferFeature);
        // Use the coordinates of the corresponding brt_stop as the center of the circle
        const bufferCentroid = otherProjection(correspondingStop.geometry.coordinates);
        // Get any point on the bufferFeature polygon
        const bufferPoint = otherProjection(bufferFeature.geometry.coordinates[0][0]);
        // Calculate the distance between the center and the point on the polygon
        const dx = bufferPoint[0] - bufferCentroid[0];
        const dy = bufferPoint[1] - bufferCentroid[1];
        const actualRadius = Math.sqrt(dx * dx + dy * dy);

        // Perhaps you want to start with a larger radius initially.
        let currentRadius = actualRadius * 70; // Change the multiplier as needed


        //Parks
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

        // Draw the circles with initial larger radius
        // brt buffer_notinpark
        g.selectAll('circle.brt_buffer_notinpark')
            .data(brt_buffer_notinpark.features)
            .enter()
            .append('circle')
            .attr('cx', d => otherProjection(getMatchingStop(d).geometry.coordinates)[0])
            .attr('cy', d => otherProjection(getMatchingStop(d).geometry.coordinates)[1])
            .attr('r', currentRadius) // set the initial larger radius here
            .attr('class', 'brt_buffer_notinpark2')

        // brt buffer_inpark
        g.selectAll('circle.brt_buffer_inpark')
            .data(brt_buffer_inpark.features)
            .enter()
            .append('circle')
            .attr('cx', d => otherProjection(getMatchingStop(d).geometry.coordinates)[0])
            .attr('cy', d => otherProjection(getMatchingStop(d).geometry.coordinates)[1])
            .attr('r', currentRadius) // set the initial larger radius here
            .attr('class', 'brt_buffer_inpark2')

        function getMatchingStop(bufferFeature) {
            // Extract OBJECTId_left from bufferFeature
            const objectIdLeft = bufferFeature.properties.OBJECTID_left;
            // Find the corresponding stop in brt_stops where OBJECTID matches objectIdLeft
            return brt_stops.features.find(stop => stop.properties.OBJECTID === objectIdLeft);
        }

    });
    createLegend3()
});


function createLegend3() {
    const legendContainer = d3.select('#legend-container3');

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
        }
    });

    // Append text for each legend item
    legendItems.append('text')
        .attr('x', legendItemWidth + textOffset)
        .attr('y', legendItemHeight / 2.2)
        .attr('dy', '0.35em')
        .text(d => d.label);
}
