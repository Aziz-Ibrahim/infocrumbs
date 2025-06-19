document.addEventListener("DOMContentLoaded", function () {
    const saveButton = document.getElementById("save-btn");

    if (saveButton) {
        saveButton.addEventListener("click", function () {
            const crumbId = this.dataset.id;

            if (!crumbId) {
                console.error("Missing crumb ID");
                return;
            }

            fetch(`/feedback/crumb/save/${crumbId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.saved) {
                    this.innerHTML = '<i class="fa-solid fa-star"></i> Saved';
                } else {
                    this.innerHTML = '<i class="fa-regular fa-star"></i> Save';
                }
            })
            .catch(err => {
                console.error("Error saving crumb:", err);
            });
        });
    };

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
