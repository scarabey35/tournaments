(function initThemeToggle() {
    const body = document.body;
    const toggle = document.getElementById('themeToggle');
    const storage = window.localStorage;

    try {
        const savedTheme = storage.getItem('theme');
        if (savedTheme === 'light') {
            body.classList.add('light-theme');
            if (toggle) toggle.textContent = '☀️';
        } else {
            if (toggle) toggle.textContent = '🌙';
        }
    } catch(e) {}

    if (toggle) {
        toggle.addEventListener('click', () => {
            body.classList.toggle('light-theme');
            const isLight = body.classList.contains('light-theme');
            toggle.textContent = isLight ? '☀️' : '🌙';
            try { storage.setItem('theme', isLight ? 'light' : 'dark'); } catch(e) {}
        });
    }
})();