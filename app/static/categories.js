document.addEventListener('DOMContentLoaded', function () {
    const iconContainers = document.querySelectorAll('.icon-container');
    iconContainers.forEach(container => {
        container.addEventListener('click', function () {
            const url = container.getAttribute('data-url');
            if (url) {
                window.location.href = url;
            }
        });
    });

    // Handle category card click to navigate to the category page
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('click', function () {
            const categoryId = card.getAttribute('data-category-id');
            const url = `/category/${categoryId}`;
            window.location.href = url;
        });
    });

    // Handle add task button click
    const addTaskButtons = document.querySelectorAll('.add-task-btn');
    addTaskButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.stopPropagation(); // Prevent click event from propagating to the card
            const categoryId = button.getAttribute('data-category-id');
            const url = `/add_task?category_id=${categoryId}`;
            window.location.href = url;
        });
    });

    // Handle mark all as completed button click
    const markAllButtons = document.querySelectorAll('.mark-all-btn');
    markAllButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.stopPropagation(); // Prevent click event from propagating to the card
            const categoryId = button.getAttribute('data-category-id');
            const url = `/mark_all_completed/${categoryId}`;
            window.location.href = url;
        });
    });

    // Handle menu icon click to toggle dropdown menu
    const menuIcons = document.querySelectorAll('.menu-icon');
    menuIcons.forEach(icon => {
        icon.addEventListener('click', function (event) {
            event.stopPropagation();
            // Close all open menus
            document.querySelectorAll('.menu-options').forEach(menu => menu.style.display = 'none');
            // Toggle the specific menu
            const categoryId = icon.getAttribute('onclick').match(/'([^']+)'/)[1];
            toggleMenu(categoryId);
        });
    });

    // Close all menus when clicking outside
    document.addEventListener('click', function () {
        document.querySelectorAll('.menu-options').forEach(menu => {
            menu.style.display = 'none';
        });
    });

    // Handle "Add Category" button click (big plus button)
    document.querySelector('.add-category-card').onclick = function () {
        document.getElementById('categoryModal').style.display = 'block';
    };

    // Close "Create New Category" modal
    document.getElementById('closeModal').onclick = function () {
        document.getElementById('categoryModal').style.display = 'none';
    };

    // Close "Edit Category" modal event
    document.getElementById('closeEditModal').onclick = function () {
        document.getElementById('editCategoryModal').style.display = 'none';
    };

    // Close modals if user clicks outside of them
    window.onclick = function (event) {
        if (event.target === document.getElementById('categoryModal')) {
            document.getElementById('categoryModal').style.display = 'none';
        }
        if (event.target === document.getElementById('editCategoryModal')) {
            document.getElementById('editCategoryModal').style.display = 'none';
        }
    };
});

function toggleMenu(categoryId) {
    const menu = document.getElementById(`menu-${categoryId}`);
    menu.style.display = (menu.style.display === 'none' || menu.style.display === '') ? 'block' : 'none';
}

function openEditCategoryModal(event, categoryId) {
    event.stopPropagation(); // Prevent click event propagation

    console.log("Opening Edit Modal for Category ID:", categoryId);

    // Get the category card based on the categoryId
    const categoryCard = document.querySelector(`[data-category-id="${categoryId}"]`);

    if (!categoryCard) {
        console.error("Category card not found for categoryId:", categoryId);
        return;
    }

    // Populate the form fields
    document.getElementById('editCategoryId').value = categoryId;

    // Set category name
    const nameElement = categoryCard.querySelector('h3');
    if (nameElement) {
        document.getElementById('editCategoryName').value = nameElement.textContent.trim();
    } else {
        console.error("Category name element not found for categoryId:", categoryId);
    }

    // Set category color (Ensure you parse RGB to hex if necessary)
    const rgbColor = window.getComputedStyle(categoryCard).backgroundColor;
    document.getElementById('editCategoryColor').value = rgbToHex(rgbColor);

    // Set the description if available
    const descriptionElement = categoryCard.querySelector('.category-description');
    if (descriptionElement) {
        document.getElementById('editCategoryDescription').value = descriptionElement.textContent.trim();
    } else {
        console.warn("No description element found for categoryId:", categoryId);
    }

    // Set priority level
    const priorityElement = categoryCard.querySelector('p.priority-level');
    const prioritySelect = document.getElementById('editCategoryPriority');
    if (priorityElement) {
        prioritySelect.value = priorityElement.textContent.split(": ")[1].trim();
    } else {
        prioritySelect.value = "Medium"; // Default value
    }

    // Set visibility
    const visibilityElement = categoryCard.querySelector('p.visibility');
    const visibilitySelect = document.getElementById('editCategoryVisibility');
    if (visibilityElement) {
        visibilitySelect.value = visibilityElement.textContent.split(": ")[1].trim();
    } else {
        visibilitySelect.value = "Private"; // Default value
    }

    // Set shared checkbox
    const sharedElement = categoryCard.querySelector('p.shared');
    const sharedCheckbox = document.getElementById('editCategoryShared');
    sharedCheckbox.checked = sharedElement && sharedElement.textContent.split(": ")[1].trim() === "Yes";

    // Set icon value (Assuming there's an attribute 'data-icon' on the card element)
    const iconValue = categoryCard.getAttribute('data-icon');
    document.getElementById('editCategoryIcon').value = iconValue || "";

    // Set archived checkbox
    const archivedElement = categoryCard.querySelector('p.archived');
    const archivedCheckbox = document.getElementById('editCategoryArchived');
    archivedCheckbox.checked = archivedElement && archivedElement.textContent.split(": ")[1].trim() === "Yes";

    // Show the edit category modal
    document.getElementById('editCategoryModal').style.display = 'block';
}

// Helper function to convert RGB to HEX color format
function rgbToHex(rgb) {
    const rgbArray = rgb.match(/\d+/g);
    if (!rgbArray) {
        return "#000000"; // Fallback color if RGB is not found
    }
    return `#${((1 << 24) + (+rgbArray[0] << 16) + (+rgbArray[1] << 8) + +rgbArray[2]).toString(16).slice(1)}`;
}


function deleteCategory(event, categoryId) {
    event.stopPropagation(); // Prevent click event from propagating to other elements

    if (confirm('Are you sure you want to delete this category?')) {
        // Send a POST request with a delete flag using fetch
        fetch(`/delete_category/${categoryId}`, {
            method: 'POST',  // Use POST instead of DELETE
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ delete: true })  // Optional: send additional info to confirm delete
        })
        .then(response => {
            if (response.ok) {
                return response.json();  // Parse response as JSON if successful
            } else {
                return response.text().then(text => { throw new Error(text); });
            }
        })
        .then(data => {
            if (data.success) {
                window.location.reload(); // Refresh the page after successful deletion
            } else {
                alert(data.error || 'Failed to delete category.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to delete category. Please try again.');
        });
    }
}




document.addEventListener("DOMContentLoaded", function() {
    // Open modal on button click
    document.querySelector(".add-category-card").onclick = function() {
        document.getElementById("categoryModal").style.display = "block";
    };

    // Close modal event
    document.getElementById("closeModal").onclick = function() {
        document.getElementById("categoryModal").style.display = "none";
    };

    // Close modal if user clicks outside of it
    window.onclick = function(event) {
        if (event.target == document.getElementById("categoryModal")) {
            document.getElementById("categoryModal").style.display = "none";
        }
    };

    // Close edit modal event
    document.getElementById("closeEditModal").onclick = function() {
        document.getElementById("editCategoryModal").style.display = "none";
    };

    // Close edit modal if user clicks outside of it
    window.onclick = function(event) {
        if (event.target == document.getElementById("editCategoryModal")) {
            document.getElementById("editCategoryModal").style.display = "none";
        }
    };
});

// Confirm color selection
document.addEventListener("DOMContentLoaded", function() {
    const colorInput = document.getElementById("categoryColor");

    if (colorInput) {
        colorInput.addEventListener("input", function() {
            colorInput.style.backgroundColor = colorInput.value;
        });
    } else {
        console.warn('Element with ID "categoryColor" not found.');
    }
});


function submitEditCategory(event) {
    event.preventDefault(); // Prevent the default form submission

    const categoryId = document.getElementById('editCategoryId').value;
    const categoryName = document.getElementById('editCategoryName').value;
    const categoryDescription = document.getElementById('editCategoryDescription').value;
    const categoryColor = document.getElementById('editCategoryColor').value;
    const priorityLevel = document.getElementById('editCategoryPriority').value;
    const visibility = document.getElementById('editCategoryVisibility').value;
    const isShared = document.getElementById('editCategoryShared').checked;
    const categoryIcon = document.getElementById('editCategoryIcon').value;
    const archived = document.getElementById('editCategoryArchived').checked;

    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

    console.log("CSRF Token:", csrfToken);  // Log the CSRF token to verify it's correct

    fetch(`/edit_category/${categoryId}`, {
        method: 'POST', // Change to POST
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            name: categoryName,
            description: categoryDescription,
            color: categoryColor,
            priority_level: priorityLevel,
            visibility: visibility,
            is_shared: isShared,
            icon: categoryIcon,
            archived: archived
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);

        if (response.ok) {
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return response.json();
            } else {
                console.error('Expected JSON, got text response:', response);
                throw new Error('Expected JSON response but received a different format');
            }
        } else if (response.status === 400) {
            // Handle CSRF or form validation errors
            return response.json().then(data => {
                throw new Error(data.error || 'Invalid request');
            });
        } else {
            return response.text().then(text => {
                console.error('Response error text:', text);
                throw new Error(`Error response from server: ${text}`);
            });
        }
    })
    .then(data => {
        if (data.success) {
            alert(data.message || 'Category updated successfully.');
            document.getElementById('editCategoryModal').style.display = 'none';
            window.location.reload();
        } else {
            alert(data.error || 'Failed to update category.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update category. Please try again.');
    });
}

