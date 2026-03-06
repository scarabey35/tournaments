const toggle = document.getElementById('themeToggle');
const body = document.body;

// Завантаження збереженої теми
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    body.classList.add('dark-theme');
    toggle.textContent = '☀️';
}

toggle.addEventListener('click', () => {
    body.classList.toggle('dark-theme');
    
    if (body.classList.contains('dark-theme')) {
        toggle.textContent = '☀️';
        localStorage.setItem('theme', 'dark');
    } else {
        toggle.textContent = '🌙';
        localStorage.setItem('theme', 'light');
    }
});