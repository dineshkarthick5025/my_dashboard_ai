function toggleDetails(id) {
  const details = document.getElementById(`details-${id}`);
  const arrow = document.querySelector(`button[onclick="toggleDetails(${id})"]`);
  
  if (details.style.display === 'block') {
    details.style.display = 'none';
    arrow.classList.remove('expanded');
  } else {
    details.style.display = 'block';
    arrow.classList.add('expanded');
  }
}
