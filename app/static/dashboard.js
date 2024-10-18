document.addEventListener('DOMContentLoaded', function() {
    const iconContainers = document.querySelectorAll('.icon-container');
    iconContainers.forEach(container => {
        container.addEventListener('click', function() {
            const url = container.getAttribute('data-url');
            if (url) {
                window.location.href = url;
            }
        });
    });

    // Handle category card click to navigate to the category page
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('click', function() {
            const categoryId = card.getAttribute('data-category-id');
            // Build the URL dynamically using JavaScript
            const url = `/category/${categoryId}`;
            window.location.href = url;
        });
    });

    // Handle add task button click
    const addTaskButtons = document.querySelectorAll('.add-task-btn');
    addTaskButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent click event from propagating to the card
            const categoryId = button.getAttribute('data-category-id');
            const url = `/add_task?category_id=${categoryId}`;
            window.location.href = url;
        });
    });

    // Handle mark all as completed button click
    const markAllButtons = document.querySelectorAll('.mark-all-btn');
    markAllButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent click event from propagating to the card
            const categoryId = button.getAttribute('data-category-id');
            const url = `/mark_all_completed/${categoryId}`;
            window.location.href = url;
        });
    });

    // Handle menu icon click to toggle dropdown menu
    const menuIcons = document.querySelectorAll('.menu-icon');
    menuIcons.forEach(icon => {
        icon.addEventListener('click', function(event) {
            event.stopPropagation();
            // Close all open menus
            document.querySelectorAll('.menu-options').forEach(menu => menu.style.display = 'none');
            // Toggle the specific menu
            const categoryId = icon.getAttribute('onclick').match(/'([^']+)'/)[1];
            toggleMenu(categoryId);
        });
    });

    // Close all menus when clicking outside
    document.addEventListener('click', function() {
        document.querySelectorAll('.menu-options').forEach(menu => {
            menu.style.display = 'none';
        });
    });
});

function toggleMenu(categoryId) {
    const menu = document.getElementById(`menu-${categoryId}`);
    menu.style.display = (menu.style.display === 'none' || menu.style.display === '') ? 'block' : 'none';
}

function openEditCategoryModal(event, categoryId) {
    event.stopPropagation();
    // Show the edit category modal
    document.getElementById('editCategoryModal').style.display = 'block';

    // Set the form's hidden input values based on the selected category
    const categoryCard = document.querySelector(`[data-category-id="${categoryId}"]`);
    document.getElementById('editCategoryId').value = categoryId;
    document.getElementById('editCategoryName').value = categoryCard.querySelector('h3').textContent.trim();
    document.getElementById('editCategoryColor').value = categoryCard.style.backgroundColor;

    // Set the description if available
    const descriptionElement = categoryCard.querySelector('.category-description');
    if (descriptionElement) {
        document.getElementById('editCategoryDescription').value = descriptionElement.textContent.trim();
    }

    // Set the form action URL dynamically
    const editCategoryForm = document.getElementById('editCategoryForm');
    editCategoryForm.action = `/edit_category/${categoryId}`; // Assuming the route expects category_id as a URL parameter
}


function deleteCategory(event, categoryId) {
    event.stopPropagation();
    if (confirm('Are you sure you want to delete this category?')) {
        fetch(`/delete_category/${categoryId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                window.location.reload(); // Refresh the page after deletion
            } else {
                alert('Failed to delete category.');
            }
        }).catch(error => {
            console.error('Error:', error);
            alert('Failed to delete category.');
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
    const confirmColorBtn = document.getElementById("confirmColorBtn");

    confirmColorBtn.addEventListener("click", function() {
        const selectedColor = colorInput.value;
        alert("Color selected: " + selectedColor);
    });

    colorInput.addEventListener("input", function() {
        colorInput.style.backgroundColor = colorInput.value;
    });
});

function submitEditCategory(event) {
    event.preventDefault(); // Prevent the default form submission

    // Gather form data
    const categoryId = document.getElementById('editCategoryId').value;
    const categoryName = document.getElementById('editCategoryName').value;
    const categoryDescription = document.getElementById('editCategoryDescription').value;
    const categoryColor = document.getElementById('editCategoryColor').value;

    // Send the update request using fetch
    fetch(`/edit_category/${categoryId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            categoryName: categoryName,
            categoryDescription: categoryDescription,
            categoryColor: categoryColor
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to update category.');
        }
    })
    .then(data => {
        console.log(data.message); // Log the success message
        // If successful, close the modal and refresh the categories on the page
        document.getElementById('editCategoryModal').style.display = 'none';
        window.location.reload(); // Reload to reflect changes
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update the category.');
    });
}

fetch(`/edit_category/${categoryId}`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    body: JSON.stringify({
        categoryName: name,
        categoryDescription: description,
        categoryColor: color
    })
})
.then(response => {
    if (response.ok) {
        return response.json();  // Parse as JSON if successful
    } else {
        // If response is not ok, throw an error
        return response.text().then(text => { throw new Error(text); });
    }
})
.then(data => {
    if (data.success) {
        // Close the modal and refresh the page if successful
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
