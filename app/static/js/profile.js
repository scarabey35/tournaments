document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    const roleDisplay = document.getElementById('roleDisplay');

    const roleNames = {
        team: 'Учасник',
        jury: 'Журі',
        admin: 'Адмін'
    };

    const currentRole = (body.dataset.role || 'guest').toLowerCase();

    if (roleDisplay) {
        roleDisplay.textContent = roleNames[currentRole] || roleNames.guest;
    }

    const passwordToggles = document.querySelectorAll('.password-toggle');

    const showPassword = (btn) => {
        const targetName = btn.dataset.target;
        const input = document.querySelector(`input[name="${targetName}"]`);
        if (input) input.type = 'text';
    };

    const hidePassword = (btn) => {
        const targetName = btn.dataset.target;
        const input = document.querySelector(`input[name="${targetName}"]`);
        if (input) input.type = 'password';
    };

    passwordToggles.forEach((btn) => {
        btn.addEventListener('mousedown', () => showPassword(btn));
        btn.addEventListener('mouseup', () => hidePassword(btn));
        btn.addEventListener('mouseleave', () => hidePassword(btn));
        btn.addEventListener('touchstart', () => showPassword(btn), { passive: true });
        btn.addEventListener('touchend', () => hidePassword(btn));
        btn.addEventListener('touchcancel', () => hidePassword(btn));
    });

});