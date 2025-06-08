document.addEventListener("DOMContentLoaded", function () {
    const commentForm = document.querySelector("#comment-form form");
    const commentsSection = document.getElementById("comments-section");

    if (commentForm) {
        commentForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const formData = new FormData(commentForm);
            const actionUrl = commentForm.getAttribute("action");

            fetch(actionUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => {
                if (!response.ok) throw new Error("Failed to post comment.");
                return response.text();
            })
            .then(html => {
                commentsSection.innerHTML = html;
                commentForm.reset();
            })
            .catch(err => {
                console.error(err);
                alert("Error posting comment. Try again.");
            });
        });
    }

    commentsSection.addEventListener("click", function (e) {
        const target = e.target;

        if (target.classList.contains("edit-comment")) {
            e.preventDefault();
            const commentId = target.dataset.id;

            fetch(`/feedback/edit/${commentId}/`, {
                headers: { "X-Requested-With": "XMLHttpRequest" }
            })
            .then(res => res.text())
            .then(html => {
                const container = document.getElementById(`comment-${commentId}`);
                if (container) {
                    container.innerHTML = html;
                }
            });
        }

        if (target.classList.contains("delete-comment")) {
            e.preventDefault();
            const commentId = target.dataset.id;

            if (confirm("Delete this comment?")) {
                fetch(`/feedback/delete/${commentId}/`, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCSRFToken(),
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        const el = document.getElementById(`comment-${commentId}`);
                        if (el) el.remove();
                    } else {
                        alert("Failed to delete comment.");
                    }
                });
            }
        }
    });

    commentsSection.addEventListener("submit", function (e) {
        if (e.target.classList.contains("edit-comment-form")) {
            e.preventDefault();
            const form = e.target;
            const commentId = form.dataset.id;
            const formData = new FormData(form);

            fetch(`/feedback/edit/${commentId}/`, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCSRFToken(),
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const el = document.getElementById(`comment-${commentId}`);
                    if (el) {
                        el.innerHTML = `
                            <p><strong>You</strong> — just now</p>
                            <p class="comment-content">${data.content}</p>
                            <div class="comment-actions">
                                <a href="#" class="edit-comment" data-id="${commentId}">Edit</a> |
                                <a href="#" class="delete-comment" data-id="${commentId}">Delete</a>
                            </div>`;
                    }
                } else {
                    alert("Failed to update comment.");
                }
            })
            .catch(err => {
                console.error(err);
                alert("Error saving comment. Try again.");
            });
        }
    });

    function getCSRFToken() {
        const csrfInput = document.querySelector('input[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }
});