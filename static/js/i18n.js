let translations = {};
let currentLang = 'en';

function loadLanguage(lang) {
  currentLang = lang;
  fetch(`/static/lang.json`)
    .then(response => response.json())
    .then(data => {
      translations = data[lang] || {};
      applyTranslations();
    })
    .catch(error => console.error('Error loading language file:', error));
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[key]) {
      el.textContent = translations[key];
    }
  });

  // Handle placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (translations[key]) {
      el.setAttribute('placeholder', translations[key]);
    }
  });
}
