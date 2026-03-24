const toggle = document.getElementById('themeToggle');
const body = document.body;

const renderThemeIcon = () => {
    if (!toggle) return;
    toggle.textContent = body.classList.contains('dark-theme') ? '☀' : '☾';
};

if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark-theme');
}

renderThemeIcon();

if (toggle) {
    toggle.addEventListener('click', () => {
        body.classList.toggle('dark-theme');
        localStorage.setItem('theme', body.classList.contains('dark-theme') ? 'dark' : 'light');
        renderThemeIcon();
    });
}