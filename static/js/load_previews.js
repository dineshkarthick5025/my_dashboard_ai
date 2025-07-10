async function loadPreviews(showLoading = true) {
  const previewSection = document.getElementById("preview-section");
  const refreshBtn = document.getElementById("refreshPreviewsBtn");
  const spinner = document.getElementById("loadingSpinner");

  if (!previewSection) return;

  if (showLoading) {
    spinner.style.display = "inline";
    if (refreshBtn) refreshBtn.disabled = true;
  }

  // Use cached version if not explicitly asked to refresh
  const cached = sessionStorage.getItem("table_previews");
  if (cached && !showLoading) {
    previewSection.innerHTML = cached;
    spinner.style.display = "none";
    if (refreshBtn) refreshBtn.disabled = false;
    return;
  }

  try {
    const res = await fetch("/dashboard/data/previews", {
      credentials: "include",
    });

    const html = await res.text();

    // Check if redirected to login (best effort)
    if (res.redirected || res.url.includes("/login")) {
      window.location.href = res.url;
      return;
    }

sessionStorage.setItem("table_previews", html);
previewSection.innerHTML = html;

  } catch (err) {
    previewSection.innerHTML = `<p style="color:red;">Failed to load previews</p>`;
  } finally {
    spinner.style.display = "none";
    if (refreshBtn) refreshBtn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Load from cache or fetch on first visit
  loadPreviews(false);

  const refreshBtn = document.getElementById("refreshPreviewsBtn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      sessionStorage.removeItem("table_previews");
      loadPreviews(true);
    });
  }
});


document.getElementById('refreshPreviewsBtn').addEventListener('click', () => {
  
  const loader = document.getElementById('loadingSpinner');
  const previewContent = document.getElementById('previewContent');

  loader.style.display = 'flex';
  previewContent.style.display = 'none';

  // Simulate loading, replace with real fetch
  setTimeout(() => {
    loader.style.display = 'none';
    previewContent.innerHTML = "<p>✅ Previews loaded successfully!</p>";
    previewContent.style.display = 'block';
  }, 2000);

});







