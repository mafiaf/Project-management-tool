document.addEventListener("DOMContentLoaded", function () {
    const circularContainer = document.querySelector(".circular-container");
    const nodes = document.querySelectorAll(".category-node");
    const addButton = document.getElementById("add-category-btn");

    if (!circularContainer || nodes.length === 0 || !addButton) {
        return; // exit if element isnt' found
    }

    const radius = 180; // distance from center
    const centerX = circularContainer.offsetWidth / 2;
    const centerY = circularContainer.offsetHeight / 2;

    // Circular positioning
    nodes.forEach((node, index) => {
        const angle = (index / nodes.length) * 2 * Math.PI;
        const x = centerX + radius * Math.cos(angle) - node.offsetWidth / 2;
        const y = centerY + radius * Math.sin(angle) - node.offsetHeight / 2;

        node.style.position = "absolute";
        node.style.left = `${x}px`;
        node.style.top = `${y}px`;
    });

    // Position to the add button in the middle
    addButton.style.position = "absolute";
    addButton.style.left = `${centerX - addButton.offsetWidth / 2}px`;
    addButton.style.top = `${centerY - addButton.offsetHeight / 2}px`;
});
