function openModal() {
  document.getElementById("dbModal").style.display = "block";
}

function closeModal() {
  document.getElementById("dbModal").style.display = "none";
}

function openPostgresForm() {
  closeModal();
  document.getElementById("postgresModal").style.display = "block";
}

function closePostgresForm() {
  document.getElementById("postgresModal").style.display = "none";
}

window.onclick = function (event) {
  const dbModal = document.getElementById("dbModal");
  const postgresModal = document.getElementById("postgresModal");
  if (event.target === dbModal) dbModal.style.display = "none";
  if (event.target === postgresModal) postgresModal.style.display = "none";
};

document.addEventListener("DOMContentLoaded", () => {
  const biHomeBtn = document.getElementById("connectDatabase");      // BI Home
  const dataTabBtn = document.getElementById("connectDatabaseBtn");  // Data Tab

  if (biHomeBtn) biHomeBtn.addEventListener("click", openModal);
  if (dataTabBtn) dataTabBtn.addEventListener("click", openModal);

  const closeModalBtn = document.getElementById("closeModal");
  if (closeModalBtn) closeModalBtn.addEventListener("click", closeModal);
});

