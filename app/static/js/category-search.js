document.addEventListener('DOMContentLoaded', function () {
    // Get elements
    const searchInput = document.getElementById('searchCategories');
    const filterPriority = document.getElementById('filterPriority');
    const filterVisibility = document.getElementById('filterVisibility');
    const searchButton = document.getElementById('searchButton');

    // Handle search button click event
    searchButton.addEventListener('click', function () {
        fetchCategories();
    });

    // Handle filter input and search again button click
    function fetchCategories() {
        const searchQuery = searchInput.value.trim();
        const priority = filterPriority.value;
        const visibility = filterVisibility.value;

        // Perform AJAX request to fetch filtered categories from the entire dataset
        fetch('/fetch_categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()  // Make sure CSRF protection is applied
            },
            body: JSON.stringify({
                search: searchQuery,
                priority: priority,
                visibility: visibility
            })
        })
        .then(response => response.json())
        .then(data => {
            updateCategoriesGrid(data.categories);
        })
        .catch(error => console.error('Error fetching categories:', error));
    }

    // Update categories grid dynamically
    function updateCategoriesGrid(categories) {
        const gridContainer = document.querySelector('.grid-container');
        gridContainer.innerHTML = ''; // Clear current categories

        categories.forEach(category => {
            const categoryCard = createCategoryCard(category);
            gridContainer.appendChild(categoryCard);
        });

        document.querySelector('.search-and-filter').style.display = 'block';
    }

    // Create category card element
    function createCategoryCard(category) {
        const card = document.createElement('div');
        card.classList.add('category-card');
        card.setAttribute('data-category-id', category.id);
        card.style.backgroundColor = category.color;

        card.innerHTML = `
            <h3>${category.name}</h3>
            <p class="category-description">${category.description}</p>
            <p class="priority-level">Priority Level: ${category.priority_level}</p>
            <p class="visibility">Visibility: ${category.visibility}</p>
            <button class="toggle-status-btn" data-category-id="${category.id}">
                Toggle Status
            </button>
        `;

        // Add click event for status toggle button
        const toggleStatusBtn = card.querySelector('.toggle-status-btn');
        toggleStatusBtn.addEventListener('click', function (event) {
            event.stopPropagation();
            toggleCategoryStatus(category.id);
        });

        return card;
    }

    // Toggle category status via AJAX
    function toggleCategoryStatus(categoryId) {
        fetch(`/toggle_category_status/${categoryId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken() // CSRF token 
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Category status updated successfully');
                fetchCategories();  // Refresh toggle? Not working...
            } else {
                alert('Failed to update category status');
            }
        })
        .catch(error => console.error('Error toggling category status:', error));
    }

    // Protected requests
    function getCsrfToken() {
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        return csrfToken;
    }
});
