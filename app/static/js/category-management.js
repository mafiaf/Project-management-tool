function setupCategoryManagement() {
    const editCategoryButtons = document.querySelectorAll('.edit-category-btn');
    editCategoryButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const categoryId = button.getAttribute('data-category-id');
            console.log("Clicked on Edit Category Button for ID:", categoryId);
            openEditCategoryModal(event, categoryId);
        });
    });

    const addCategoryCard = document.getElementById('addCategoryCard');
    if (addCategoryCard) {
        addCategoryCard.addEventListener('click', function () {
            const categoryModal = document.getElementById('categoryModal');
            if (categoryModal) {
                categoryModal.style.display = 'block';
            }
        });
    }

    const editCategoryForm = document.getElementById('editCategoryForm');
    if (editCategoryForm) {
        editCategoryForm.addEventListener('submit', submitEditCategory);
    }
}

// Function to handle opening the edit modal and populate fields
function openEditCategoryModal(event, categoryId) {
    event.stopPropagation();
    const categoryCard = document.querySelector(`[data-category-id="${categoryId}"]`);
    if (!categoryCard) {
        console.error("Category card not found for categoryId:", categoryId);
        return;
    }

    // Populate modal fields
    document.getElementById('editCategoryId').value = categoryId;
    document.getElementById('editCategoryName').value = categoryCard.getAttribute('data-category-name') || '';
    document.getElementById('editCategoryDescription').value = categoryCard.getAttribute('data-category-description') || '';
    document.getElementById('editCategoryColor').value = categoryCard.getAttribute('data-category-color') || '#000000';
    document.getElementById('editCategoryPriority').value = categoryCard.getAttribute('data-category-priority-level') || 'Medium';
    document.getElementById('editCategoryVisibility').value = categoryCard.getAttribute('data-category-visibility') || 'Private';
    document.getElementById('editCategoryShared').checked = categoryCard.getAttribute('data-category-shared') === 'Yes';
    document.getElementById('editCategoryArchived').checked = categoryCard.getAttribute('data-category-archived') === 'Yes';
    document.getElementById('editCategoryIcon').value = categoryCard.getAttribute('data-category-icon') || '';

    document.getElementById('editCategoryModal').style.display = 'block';
}
