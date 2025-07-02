document.addEventListener("DOMContentLoaded", () => {
    const connectBtn = document.getElementById("connectDatabase");
    const modal = document.getElementById("dbModal");
    const closeModal = document.getElementById("closeModal");

    connectBtn.onclick = () => {
        modal.style.display = "block";
    };

    closeModal.onclick = () => {
        modal.style.display = "none";
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    document.querySelectorAll(".db-option").forEach(button => {
        button.addEventListener("click", () => {
            const dbType = button.getAttribute("data-type");
            alert(`You selected: ${dbType}`);
            modal.style.display = "none";
        });
    });
});

