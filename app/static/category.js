// category.js

function markTaskAsDone(taskId) {
    fetch(`/task/${taskId}/mark_done`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then((response) => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Failed to mark the task as done.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Error marking the task as done.');
    });
}
