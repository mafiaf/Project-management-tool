function setupModalHandling() {
    const closeEditModalButton = document.getElementById('closeEditModal');
    if (closeEditModalButton) {
        closeEditModalButton.addEventListener('click', function () {
            document.getElementById('editCategoryModal').style.display = 'none';
        });
    }

    const closeModalButton = document.getElementById('closeModal');
    if (closeModalButton) {
        closeModalButton.addEventListener('click', function () {
            document.getElementById('categoryModal').style.display = 'none';
        });
    }

    window.onclick = function (event) {
        const editCategoryModal = document.getElementById('editCategoryModal');
        if (event.target === editCategoryModal) {
            editCategoryModal.style.display = 'none';
        }
    };
}
