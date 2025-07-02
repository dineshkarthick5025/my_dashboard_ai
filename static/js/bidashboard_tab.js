function editDashboard(id) {
  window.location.href = `/dashboardeditor?dashboard_id=${id}`;
}

function deleteDashboard(id) {
  if (confirm("Are you sure you want to delete this dashboard?")) {
    fetch("/dashboard/delete", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ id: id })
    })
      .then(res => {
        if (res.ok) {
          window.location.reload();
        } else {
          console.error("Delete failed with status", res.status);
        }
      })
      .catch(err => console.error("Delete failed", err));
  }
}