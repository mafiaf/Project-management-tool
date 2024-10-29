document.addEventListener('DOMContentLoaded', function () {
    // Handle icon container click
    const iconContainers = document.querySelectorAll('.icon-container');
    iconContainers.forEach(container => {
        container.addEventListener('click', function () {
            const url = container.getAttribute('data-url');
            if (url) {
                window.location.href = url;
            }
        });
    });

    const openCategoryModal = document.getElementById('openCategoryModalButton');
    if (openCategoryModal) {
        openCategoryModal.addEventListener('click', function (event) {
            openEditCategoryModal(event, openCategoryModal.getAttribute('data-category-id'));
        });
    }

    const editCategoryForm = document.getElementById('editCategoryForm');
    if (editCategoryForm) {
        editCategoryForm.addEventListener('submit', submitEditCategory);
        console.log("Edit category form event listener attached.");
    } else {
        console.error("Edit category form not found during DOMContentLoaded.");
    }

    // Handle category card click to navigate to the category page
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        if (!card.classList.contains('add-category-card')) {
            card.addEventListener('click', function () {
                const categoryId = card.getAttribute('data-category-id');
                if (categoryId) {
                    window.location.href = `/category/${categoryId}`;
                }
            });
        }
    });
    
    // Handle add task button click
    const addTaskButtons = document.querySelectorAll('.add-task-btn');
    addTaskButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.stopPropagation(); // Prevent click event from propagating to the card
            const categoryId = button.getAttribute('data-category-id');
            window.location.href = `/add_task?category_id=${categoryId}`;
        });
    });

    // Handle mark all as completed button click
    const markAllButtons = document.querySelectorAll('.mark-all-btn');
    markAllButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.stopPropagation(); // Prevent click event from propagating to the card
            const categoryId = button.getAttribute('data-category-id');
            window.location.href = `/mark_all_completed/${categoryId}`;
        });
    });

    // Handle menu icon click to toggle dropdown menu
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

    // Handle "Add Category" button click (big plus button)
    const addCategoryCard = document.getElementById('addCategoryCard');
    if (addCategoryCard) {
        addCategoryCard.addEventListener('click', function () {
            console.log('Add Category card clicked!'); // Debugging log
            const categoryModal = document.getElementById('categoryModal');
            if (categoryModal) {
                categoryModal.style.display = 'block';
            }
        });
    }

    // Close "Create New Category" modal
    const closeModalBtn = document.getElementById('closeModal');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', function () {
            const categoryModal = document.getElementById('categoryModal');
            if (categoryModal) {
                categoryModal.style.display = 'none';
            }
        });
    }

    // Close "Edit Category" modal event
    const closeEditModalBtn = document.getElementById('closeEditModal');
    if (closeEditModalBtn) {
        closeEditModalBtn.addEventListener('click', function () {
            const editCategoryModal = document.getElementById('editCategoryModal');
            if (editCategoryModal) {
                editCategoryModal.style.display = 'none';
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        // Handle "Create New Category" form submission
        const createCategoryForm = document.getElementById('createCategoryForm');
        if (createCategoryForm) {
            createCategoryForm.addEventListener('submit', function (event) {
                event.preventDefault(); // Prevent default form submission
    
                const formData = new FormData(createCategoryForm);
                const data = Object.fromEntries(formData.entries());
                console.log('Form data being submitted:', data);
    
                // Use fetch to submit the form data via AJAX
                fetch(createCategoryForm.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-CSRFToken': formData.get('csrf_token')
                    },
                    body: JSON.stringify(data)
                })
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(data => {
                                throw new Error(data.error || 'Failed to add category');
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            alert(data.message || 'Category created successfully.');
                            // Hide the modal after success
                            const categoryModal = document.getElementById('categoryModal');
                            if (categoryModal) {
                                categoryModal.style.display = 'none';
                            }
                            window.location.reload(); // Refresh the page to show the new category
                        } else {
                            alert(data.error || 'Failed to add category');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Failed to create category. Please try again.');
                    });
            });
        }
    });    

    document.addEventListener('DOMContentLoaded', function () {
        // Handle "Edit Category" form submission (modal version)
        const editCategoryForm = document.getElementById('editCategoryForm');
        if (editCategoryForm) {
            editCategoryForm.addEventListener('submit', function (event) {
                event.preventDefault(); // Prevent default form submission

                const formData = new FormData(editCategoryForm);
                const data = Object.fromEntries(formData.entries());

                // Log the data to debug
                console.log("Data being sent:", data);

                // Get the category ID to construct the URL
                const categoryId = data.categoryId;

                // Use fetch to submit the form data via AJAX
                fetch(`/edit_category/${categoryId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-CSRFToken': data.csrf_token // Pass the CSRF token in the headers
                    },
                    body: JSON.stringify(data)
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            console.error("Error response data:", data);
                            throw new Error(data.error || 'Failed to edit category');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        alert(data.message || 'Category updated successfully.');
                        // Optionally, hide the modal or reload the page after success
                        const editCategoryModal = document.getElementById('editCategoryModal');
                        if (editCategoryModal) {
                            editCategoryModal.style.display = 'none';
                        }
                        window.location.reload(); // Reload to see updated category
                    } else {
                        alert(data.error || 'Failed to edit category');
                    }
                })
                .catch(error => {
                    console.error('Error occurred during fetch:', error);
                    alert('Failed to update category. Please try again.');
                });
            });
        } else {
            console.error("Edit category form not found in the DOM");
        }
    });
    
    
    function submitEditCategory(event) {
        event.preventDefault(); // Prevent the default form submission behavior
    
        console.log("submitEditCategory function is called.");
    
        const editCategoryForm = document.getElementById('editCategoryForm');
        if (!editCategoryForm) {
            console.error("Edit category form not found.");
            return;
        }
    
        const formData = new FormData(editCategoryForm);
        const data = Object.fromEntries(formData.entries());
    
        // Log data to verify the values
        console.log("Form data being prepared for submission:", data);
    
        const categoryId = data.categoryId;
    
        fetch(`/edit_category/${categoryId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-CSRFToken': data.csrf_token
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            console.log("Response received from server:", response);
    
            if (!response.ok) {
                return response.json().then(data => {
                    console.error("Error response data:", data);
                    throw new Error(data.error || 'Failed to edit category');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Server response JSON:", data);
    
            if (data.success) {
                alert(data.message || 'Category updated successfully.');
                document.getElementById('editCategoryModal').style.display = 'none';
                window.location.reload(); // Reload to see the updated category
            } else {
                alert(data.error || 'Failed to edit category');
            }
        })
        .catch(error => {
            console.error('Error occurred during fetch:', error);
            alert('Failed to update category. Please try again.');
        });
    }
    
    


// Function to toggle menu visibility
function toggleMenu(categoryId) {
    const menu = document.getElementById(`menu-${categoryId}`);
    if (menu) {
        menu.style.display = (menu.style.display === 'none' || menu.style.display === '') ? 'block' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed.");
    const editCategoryBtn = document.getElementById('editCategoryBtn');
    
    if (editCategoryBtn) {
        editCategoryBtn.addEventListener('click', function (event) {
            const categoryId = event.target.getAttribute('data-category-id');
            openEditCategoryModal(event, categoryId);
        });
    }
    


    // Close modal functionality
    document.getElementById('closeEditModal').addEventListener('click', function () {
        document.getElementById('editCategoryModal').style.display = 'none';
    });

    window.onclick = function (event) {
        const editCategoryModal = document.getElementById('editCategoryModal');
        if (event.target === editCategoryModal) {
            editCategoryModal.style.display = 'none';
        }
    };
});

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed.");

    const editCategoryButtons = document.querySelectorAll('.edit-category-btn');
    console.log("Number of Edit Category Buttons Found:", editCategoryButtons.length); 

    editCategoryButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const categoryId = button.getAttribute('data-category-id');
            console.log("Clicked on Edit Category Button for ID:", categoryId);
            openEditCategoryModal(event, categoryId);
        });
    });

    // Close modal functionality
    const closeEditModalButton = document.getElementById('closeEditModal');
    if (closeEditModalButton) {
        console.log("Close Edit Modal Button Found");
        closeEditModalButton.addEventListener('click', function () {
            document.getElementById('editCategoryModal').style.display = 'none';
        });
    } else {
        console.error("Close Edit Modal button not found");
    }

    window.onclick = function (event) {
        const editCategoryModal = document.getElementById('editCategoryModal');
        if (event.target === editCategoryModal) {
            console.log("Clicked outside modal, closing modal");
            editCategoryModal.style.display = 'none';
        }
    };
});


function openEditCategoryModal(event, categoryId) {
    event.stopPropagation(); // Prevent click event propagation

    console.log("Opening Edit Modal for Category ID:", categoryId);

    // Get the category card element using the data-category-id attribute
    const categoryCard = document.querySelector(`[data-category-id="${categoryId}"]`);

    if (!categoryCard) {
        console.error("Category card not found for categoryId:", categoryId);
        return;
    }

    console.log("Category card found. Populating modal form fields...");

    // Populate the form fields using the data attributes directly from the category card
    document.getElementById('editCategoryId').value = categoryId;

    // Set category name
    const categoryName = categoryCard.getAttribute('data-category-name') || '';
    document.getElementById('editCategoryName').value = categoryName;

    // Set category description
    const categoryDescription = categoryCard.getAttribute('data-category-description') || '';
    document.getElementById('editCategoryDescription').value = categoryDescription;

    // Set category color
    const categoryColor = categoryCard.getAttribute('data-category-color') || '#000000';
    document.getElementById('editCategoryColor').value = categoryColor;

    // Set priority level
    const priorityLevel = categoryCard.getAttribute('data-category-priority-level') || 'Medium';
    document.getElementById('editCategoryPriority').value = priorityLevel;

    // Set visibility
    const visibility = categoryCard.getAttribute('data-category-visibility') || 'Private';
    document.getElementById('editCategoryVisibility').value = visibility;

    // Set shared checkbox
    const isShared = categoryCard.getAttribute('data-category-shared') === 'Yes';
    document.getElementById('editCategoryShared').checked = isShared;

    // Set archived checkbox
    const isArchived = categoryCard.getAttribute('data-category-archived') === 'Yes';
    document.getElementById('editCategoryArchived').checked = isArchived;

    // Set icon value
    const categoryIcon = categoryCard.getAttribute('data-category-icon') || '';
    document.getElementById('editCategoryIcon').value = categoryIcon;

    console.log("Modal fields populated. Displaying modal...");

    // Show the edit category modal
    document.getElementById('editCategoryModal').style.display = 'block';
}

// Helper function to convert RGB to HEX color format (for later use if necessary)
function rgbToHex(rgb) {
    const rgbArray = rgb.match(/\d+/g);
    if (!rgbArray) {
        return "#000000";
    }
    return `#${((1 << 24) + (+rgbArray[0] << 16) + (+rgbArray[1] << 8) + +rgbArray[2]).toString(16).slice(1)}`;
}
})