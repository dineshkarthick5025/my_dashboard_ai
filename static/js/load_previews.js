document.addEventListener("DOMContentLoaded", () => {
  const spinner = document.getElementById("loadingSpinner");
  const previewContent = document.getElementById("previewContent");
  
  // Initial load - show spinner, hide content
  spinner.style.display = "flex";
  previewContent.style.display = "none";
  
  // Try to load from cache first
  const cachedContent = sessionStorage.getItem("cachedPreviews");
  if (cachedContent) {
    previewContent.innerHTML = cachedContent;
    previewContent.style.display = "block";
    spinner.style.display = "none";
  }
  
  // Then load fresh data (but don't show spinner if we had cache)
  loadPreviews(!cachedContent);
  
  // Refresh button handler - will force fresh load
  const refreshBtn = document.getElementById("refreshPreviewsBtn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      // Clear cache and force fresh load
      sessionStorage.removeItem("cachedPreviews");
      loadPreviews(true);
    });
  }
});

async function loadPreviews(showLoading = true) {
  const previewContent = document.getElementById("previewContent");
  const refreshBtn = document.getElementById("refreshPreviewsBtn");
  const spinner = document.getElementById("loadingSpinner");

  if (showLoading) {
    spinner.style.display = "flex";
    previewContent.style.display = "none";
    if (refreshBtn) refreshBtn.disabled = true;
  }

  try {
    const res = await fetch("/dashboard/data/previews", {
      credentials: "include",
      headers: {
        // Add cache-control header if you want to control caching
        'Cache-Control': 'no-cache'
      }
    });

    if (res.redirected) {
      window.location.href = res.url;
      return;
    }

    const html = await res.text();
    
    // Cache the response
    sessionStorage.setItem("cachedPreviews", html);
    
    previewContent.innerHTML = html;
    previewContent.style.display = "block";
    
  } catch (err) {
    // Try to show cached content if available
    const cachedContent = sessionStorage.getItem("cachedPreviews");
    if (cachedContent) {
      previewContent.innerHTML = cachedContent;
      previewContent.style.display = "block";
    } else {
      previewContent.innerHTML = `
        <div class="error-message">
          <p>⚠️ Failed to load previews. Please try again.</p>
          <button onclick="loadPreviews(true)">Retry</button>
        </div>
      `;
      previewContent.style.display = "block";
    }
  } finally {
    spinner.style.display = "none";
    if (refreshBtn) refreshBtn.disabled = false;
  }
}