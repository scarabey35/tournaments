document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#loginForm');
    const emailInput = document.querySelector('#email');
    const passwordInput = document.querySelector('#password');

    if (!form || !emailInput || !passwordInput) {
        return;
    }

    // Контейнер для помилок (створимо, якщо його немає)
    let errorContainer = document.querySelector('.error-message');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'error-message';
        form.appendChild(errorContainer);
    }

    // Захист вiд XSS (екранування HTML)
    function escapeHTML(str) {
        return str.replace(/[&<>"]/g, function(match) {
            if (match === '&') return '&amp;';
            if (match === '<') return '&lt;';
            if (match === '>') return '&gt;';
            if (match === '"') return '&quot;';
            return match;
        });
    }

    // Показати помилку
    function showError(message) {
        errorContainer.innerHTML = escapeHTML(message);
        errorContainer.style.display = 'block';
    }

    // Очистити помилку
    function clearError() {
        errorContainer.innerHTML = '';
        errorContainer.style.display = 'none';
    }

    // Валідація email
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Перевiрка пароля (мiнiмум 6 символiв)
    function isValidPassword(password) {
        return password.length >= 6;
    }

    // Обробка вiдправлення форми
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        clearError();

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        // Перевiрка заповненостi
        if (!email || !password) {
            showError('Будь ласка, заповніть всі поля');
            return;
        }

        // Перевiрка email
        if (!isValidEmail(email)) {
            showError('Введіть коректний email');
            return;
        }

        // Перевiрка пароля
        if (!isValidPassword(password)) {
            showError('Пароль має бути не менше 6 символів');
            return;
        }

        // Якщо все ок - перенаправляємо на головну (поки без бекенду)
        window.location.href = '/';
    });

    // Захист вiд XSS при вводi (екрануємо на льоту)
});
