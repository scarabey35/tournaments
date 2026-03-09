const toggle = document.getElementById('themeToggle');
const body = document.body;
const roleDisplay = document.querySelector('.role');

const renderRole = () => {
    const role = (body.dataset.role || 'guest').toLowerCase();
    const roleNames = {
        teacher: 'Учитель',
        jury: 'Журі',
        student: 'Учень',
        guest: 'Гість'
    };

    if (roleDisplay) {
        roleDisplay.textContent = `Роль: ${roleNames[role] || 'Гість'}`;
    }
};

// Допоміжна функція для зміни ролі з інших скриптів / кнопок
window.setRole = (role) => {
    if (!role) return;
    body.dataset.role = role;
    renderRole();
};

// Слухаємо зміни атрибута data-role, щоб оновлювати текст у шапці
const roleObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-role') {
            renderRole();
        }
    }
});
roleObserver.observe(body, { attributes: true, attributeFilter: ['data-role'] });

// Завантаження збереженої теми
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    body.classList.add('dark-theme');
    toggle.textContent = '☀️';
} else {
    toggle.textContent = '🌙';
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

renderRole();
