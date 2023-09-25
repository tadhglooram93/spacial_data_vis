document.addEventListener("DOMContentLoaded", function() {
    const transitionBtn = document.getElementById('transitionBtn');

    transitionBtn.addEventListener('click', function() {
        transitionToBarChart();
    });
});


function transitionToBarChart() {
    const svg = d3.select("#map");
    const barWidth = 150;
    const totalBarHeight = 500;
    const targetX = 0;
    const targetY = 50;

    // Create a total water area rectangle
    const initialRect = svg.append('rect')
        .attr('x', targetX)
        .attr('y', targetY)
        .attr('width', barWidth)
        .attr('height', 0)
        .attr('fill', 'transparent')
        .attr('stroke', 'black');

    // Transition for the initial rectangle to grow to its full height
    initialRect.transition()
        .duration(1000) // 1 second duration
        .attr('height', totalBarHeight);

    // Create a total water area text above the rectangle
    svg.append('text')
        .attr('x', targetX + barWidth / 2)
        .attr('y', targetY - 5)
        .attr('text-anchor', 'middle')
        .text('Total Storm Water');

    const waterInParksTransition = 1500;
    const delayBetweenTransitions = 1000;

    // Define separate transition functions for water in parks and water not in parks
    transitionShape('.water-in-parks', totalBarHeight * 0.05, targetY,waterInParksTransition);
    transitionShape('.water-not-in-parks', totalBarHeight * 0.95, targetY + totalBarHeight * 0.05,delayBetweenTransitions);

    function transitionShape(selector, targetHeight, targetY, delay) {
        d3.selectAll(selector).each(function (d) {
            const currentElement = d3.select(this);
            const currentPath = currentElement.attr('d');

            // Create a new path element on top of the current one
            const newPathElement = svg.append('path')
                .attr('d', currentPath)
                .attr('class', currentElement.attr('class'))
                .attr('fill', currentElement.attr('fill'));

            // Transition the new path element
            newPathElement.transition()
                .delay(delay)
                .duration(1300)
                .attrTween('d', function (d) {
                    const targetPath = `M${targetX} ${targetY} H${targetX + barWidth} V${targetY + targetHeight} H${targetX} Z`;
                    return d3.interpolateString(currentPath, targetPath);
                })
                .on('start', function(d, i) {
                    // Get the bounding box of the current element before the transition starts
                    const bbox = this.getBBox();

                    // Calculate a new, smaller size and a new position closer to the target
                    const adjustedX = d3.interpolate(bbox.x, targetX)(0.01);
                    const adjustedY = d3.interpolate(bbox.y, targetY)(0.01);
                    const adjustedWidth = d3.interpolate(bbox.width, barWidth)(0.01);
                    const adjustedHeight = d3.interpolate(bbox.height, targetHeight)(0.01);

                    // Set the initial size and position of the element to the adjusted values
                    const path = d3.path();
                    path.rect(adjustedX, adjustedY, adjustedWidth, adjustedHeight);
                    d3.select(this).attr('d', path.toString());
                })
                .on('end', function (d, i) {
                    // Remove the original path element and the new path element
                    currentElement.remove();
                    // d3.select(this).remove();

                    // Append rectangle
                    svg.append('rect')
                        .attr('x', targetX)
                        .attr('y', targetY)
                        .attr('width', barWidth)
                        .attr('height', targetHeight)
                        .attr('fill', selector === '.water-in-parks' ? 'cyan' : '#088F8F')
                        .attr('stroke', 'black');

                    // Append text inside rectangle
                    const textPercentage = selector === '.water-in-parks' ? '5%' : '95%';
                    svg.append('text')
                        .attr('x', targetX + barWidth / 2)  // centering the text inside the rectangle
                        .attr('y', targetY + targetHeight / 2)  // centering the text inside the rectangle
                        .attr('dy', '0.35em')  // to vertically center the text
                        .attr('text-anchor', 'middle')  // to horizontally center the text
                        .text(textPercentage)
                        .attr('fill', 'black');  // text color
                });
        });
    }

}
