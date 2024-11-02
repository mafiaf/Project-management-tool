document.addEventListener('DOMContentLoaded', function () {
        const openTaskModalButton = document.getElementById('openTaskModalButton');
        const addTaskModal = document.getElementById('addTaskModal');
        const closeTaskModal = document.getElementById('closeTaskModal');

        // Open the Add Task modal
        openTaskModalButton.addEventListener('click', function () {
            addTaskModal.style.display = 'block';
        });

        // Close the Add Task modal
        closeTaskModal.addEventListener('click', function () {
            addTaskModal.style.display = 'none';
        });

        // Close modal when clicking outside of it
        window.addEventListener('click', function (event) {
            if (event.target == addTaskModal) {
                addTaskModal.style.display = 'none';
            }
        });
    });

