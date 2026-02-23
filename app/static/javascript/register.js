document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const emailInput = document.querySelector('input[type="email"]');
    const passwordInput = document.querySelector('input[type="password"]');
    const roleSelect = document.querySelector('.select');
    const submitBtn = document.querySelector('.button');

    // Контейнер для помилок (створимо, якщо його немає)
    let errorContainer = document.querySelector('.error-message');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'error-message';
        form.appendChild(errorContainer);
    }

    // захист від XSS (екранування HTML)
    function escapeHTML(str) {
        return str.replace(/[&<>"]/g, function(match) {
            if (match === '&') return '&amp;';
            if (match === '<') return '&lt;';
            if (match === '>') return '&gt;';
            if (match === '"') return '&quot;';
            return match;
        });
    }

    // показати помилку
    function showError(message) {
        errorContainer.innerHTML = escapeHTML(message);
        errorContainer.style.display = 'block';
    }

    // очистити помилку
    function clearError() {
        errorContainer.innerHTML = '';
        errorContainer.style.display = 'none';
    }

    // валiдацiя email
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Перевірка пароля (мінімум 6 символів, хоча б одна цифра)
    function isValidPassword(password) {
        return password.length >= 6 && /\d/.test(password);
    }

    // Обробка відправлення форми
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        clearError();

        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const role = roleSelect.value;

        // Перевірка заповненості
        if (!email || !password || !role) {
            showError('Будь ласка, заповніть всі поля');
            return;
        }

        // Перевірка email
        if (!isValidEmail(email)) {
            showError('Введіть коректний email');
            return;
        }

        // Перевірка пароля
        if (!isValidPassword(password)) {
            showError('Пароль має бути не менше 6 символів та містити хоча б одну цифру');
            return;
        }

        // Якщо все ок — перенаправляємо на головну (поки без бекенду)
        window.location.href = '/';
    });

    // Захист від XSS при вводі (екрануємо на льоту)
    emailInput.addEventListener('input', function() {
        this.value = escapeHTML(this.value);
    });

    passwordInput.addEventListener('input', function() {
        this.value = escapeHTML(this.value);
    });
});