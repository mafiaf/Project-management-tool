window.submitEditCategory = function(event) {
    event.preventDefault(); // Prevent default form submission behavior
    
    console.log("submitEditCategory function is called.");
    
    const editCategoryForm = document.getElementById('editCategoryForm');
    if (!editCategoryForm) {
        console.error("Edit category form not found.");
        return;
    }

    const formData = new FormData(editCategoryForm);
    const data = Object.fromEntries(formData.entries());

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
};
