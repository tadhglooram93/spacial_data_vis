document.addEventListener("DOMContentLoaded", function() {
    const svg = d3.select("#map");
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

    Promise.all([
        d3.json('data/regions_3395.geojson'),
        d3.json('data/water_in_parks_3395.geojson'),
        d3.json('data/water_not_in_parks_3395.geojson'),
        d3.json('data/parks_minus_water.geojson')
    ]).then(([regionsData, waterInParksData, waterNotInParksData, parksMinusWaterData]) => {

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
                features: [...waterInParksData.features, ...waterNotInParksData.features, ...parksMinusWaterData.features]
            });

        const path = d3.geoPath(otherProjection);

        // Water in Parks
        g.selectAll('path.water-in-parks')
            .data(waterInParksData.features)
            .enter()
            .append('path')
            .attr('d', path)
            .attr('class', 'water-in-parks')

        // Water not in Parks
        g.selectAll('path.water-not-in-parks')
            .data(waterNotInParksData.features)
            .enter()
            .append('path')
            .attr('d', path)
            .attr('class', 'water-not-in-parks')

        // Parks Minus Water
        g.selectAll('path.parks-minus-water')
            .data(parksMinusWaterData.features)
            .enter()
            .append('path')
            .attr('d', path)
            .attr('class', 'parks-minus-water')

    });
    createLegend()
});
function createLegend() {
    const legendContainer = d3.select('#legend-container');

    const categories = [
        { color: '#48b07b', label: 'Parks' },
        { color: 'lightblue', label: 'Water in Parks' },
        { color: '#088F8F', label: 'Water not in Parks' }
    ];

    const legendItemHeight = 20;
    const legendItemWidth = 20;
    const textOffset = 5;

    const legendSvg = legendContainer.append('svg')
        .attr('width', 200) // or whatever width you find appropriate
        .attr('height', categories.length * legendItemHeight);

    const legendItems = legendSvg.selectAll('g')
        .data(categories)
        .enter()
        .append('g')
        .attr('transform', (d, i) => `translate(0,${i * legendItemHeight})`);

    // Append rect for each legend item
    legendItems.append('rect')
        .attr('width', legendItemWidth)
        .attr('height', legendItemHeight)
        .attr('fill', d => d.color);

    // Append text for each legend item
    legendItems.append('text')
        .attr('x', legendItemWidth + textOffset) // Offset the text right from the rect
        .attr('y', legendItemHeight / 2) // Center the text vertically in the rect
        .attr('dy', '0.35em') // Adjust the positioning of text vertically
        .text(d => d.label);
}