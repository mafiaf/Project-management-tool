function setupTaskManagement() {
    const addTaskButtons = document.querySelectorAll('.add-task-btn');
    addTaskButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.stopPropagation();
            const categoryId = button.getAttribute('data-category-id');
            window.location.href = `/add_task?category_id=${categoryId}`;
        });
    });

    const markAllButtons = document.querySelectorAll('.mark-all-btn');
    markAllButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.stopPropagation();
            const categoryId = button.getAttribute('data-category-id');
            window.location.href = `/mark_all_completed/${categoryId}`;
        });
    });
}
