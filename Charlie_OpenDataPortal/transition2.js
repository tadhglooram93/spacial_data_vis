document.addEventListener("DOMContentLoaded", function() {
    const transitionBtn = document.getElementById('transitionBtn2');

    transitionBtn.addEventListener('click', function() {
        transitionToBarChart2();
    });
});

function transitionToBarChart2() {
    const svg = d3.select("#map2");
    const barWidth = 100;
    const totalBarHeight = 500;
    const targetX = 20;
    const targetY = 60;

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
        .text('Total Brt Bus Stops');

    const brt_notinpark_Transition = 1500;
    const brt_inpark_Transition = 3000;

    // Define separate transition functions for water in parks and water not in parks
    transitionShape2('.brt_buffer_notinpark', totalBarHeight * 0.91, targetY + totalBarHeight * 0.09,brt_notinpark_Transition,fill="#E5E4E2");
    transitionShape2('.brt_buffer_inpark', totalBarHeight * 0.09, targetY,brt_inpark_Transition,fill="#F88379");

    function transitionShape2(selector, targetHeight, targetY, delay) {
        // Create a single text element
        const textElement = svg.append('text')
            .attr('x', targetX + barWidth / 2)
            .attr('y', targetY + targetHeight / 2)
            .attr('dy', '0.35em')
            .attr('text-anchor', 'middle')
            .attr('fill', 'black');

        d3.selectAll(selector).each(function (d) {
            const currentElement = d3.select(this);

            // Calculate the initial position and size of the element
            const bbox = currentElement.node().getBBox();
            const initialX = bbox.x;
            const initialY = bbox.y;
            const initialWidth = bbox.width;
            const initialHeight = bbox.height;

            // Create a new rectangle element on top of the current one with the same fill color
            const newRect = svg.append('rect')
                .attr('x', initialX)
                .attr('y', initialY)
                .attr('width', initialWidth)
                .attr('height', initialHeight)
                .attr('fill', fill) // Apply the same fill color
                .attr('class', currentElement.attr('class'));

            // Transition the new rectangle element
            newRect.transition()
                .delay(delay)
                .duration(3500)
                .attr('x', targetX)
                .attr('y', targetY)
                .attr('width', barWidth)
                .attr('height', targetHeight)
                .on('start', function () {
                    // Remove the current element at the start of the transition
                    currentElement.remove();
                })
                .on('end', function () {
                });
        });
    }

    // Create and add text after all transitions are complete
    const textPercentage = [
        { selector: '.brt_buffer_inpark', percentage: '81 (9%)' },
        { selector: '.brt_buffer_notinpark', percentage: '863 (91%)' },
    ];

    textPercentage.forEach((item) => {
        const rectHeight = item.selector === '.brt_buffer_inpark' ? totalBarHeight * 0.09 : totalBarHeight * 0.91;
        const rectY = item.selector === '.brt_buffer_inpark' ? targetY : targetY + totalBarHeight * 0.09;
        const textY = rectY + rectHeight / 2;

        svg.append('text')
            .attr('x', targetX + barWidth / 2)
            .attr('y', textY)
            .attr('dy', '0.35em')
            .attr('text-anchor', 'middle')
            .attr('fill', 'black')
            .text(item.percentage)
            .style('opacity', 0) // Set initial opacity to 0
            .transition()
            .delay(5500) // Delay before the transition starts
            .duration(1000) // Transition duration
            .style('opacity', 1); // Fade in
    });
}

