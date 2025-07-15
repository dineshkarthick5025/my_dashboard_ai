document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("settingsForm");
    const statusMsg = document.getElementById("statusMsg");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const saveBtn = document.getElementById("saveBtn");
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="btn-icon">⏳</span> Saving...';

        try {
            const formData = new FormData(form);
            const response = await fetch('/dashboard/settings/update', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.status === 'success') {
                statusMsg.textContent = result.message;
                statusMsg.className = 'status-msg success';
            } else {
                statusMsg.textContent = result.message;
                statusMsg.className = 'status-msg error';
            }
        } catch (error) {
            statusMsg.textContent = 'Network error. Please try again.';
            statusMsg.className = 'status-msg error';
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<span class="btn-icon">💾</span> Save Changes';
        }
    });
});