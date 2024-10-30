function setupMenuHandling() {
    const menuIcons = document.querySelectorAll('.menu-icon');
    menuIcons.forEach(icon => {
        icon.addEventListener('click', function (event) {
            event.stopPropagation();
            document.querySelectorAll('.menu-options').forEach(menu => menu.style.display = 'none');
            const categoryId = icon.getAttribute('data-category-id');
            if (categoryId) {
                toggleMenu(categoryId);
            }
        });
    });

    // Close all menus when clicking outside
    document.addEventListener('click', function (event) {
        const clickedElement = event.target;
        if (!clickedElement.classList.contains('menu-icon')) {
            document.querySelectorAll('.menu-options').forEach(menu => {
                menu.style.display = 'none';
            });
        }
    });
}

// Function to toggle the visibility of menu options
function toggleMenu(categoryId) {
    const menu = document.getElementById(`menu-${categoryId}`);
    if (menu) {
        menu.style.display = (menu.style.display === 'none' || menu.style.display === '') ? 'block' : 'none';
    }
}
