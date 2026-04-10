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
});