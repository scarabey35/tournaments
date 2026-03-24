const body = document.body;
const roleDisplay = document.getElementById('roleDisplay');

const roleNames = {
    teacher: 'Учитель',
    jury: 'Журі',
    student: 'Учень',
    admin: 'Адмін',
    guest: 'Гість'
};

const renderRole = () => {
    const role = (body.dataset.role || 'guest').toLowerCase();

    if (roleDisplay) {
        roleDisplay.textContent = roleNames[role] || roleNames.guest;
    }
};

window.setRole = (role) => {
    if (!role) return;
    body.dataset.role = role;
    renderRole();
};

const roleObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-role') {
            renderRole();
        }
    }
});

roleObserver.observe(body, { attributes: true, attributeFilter: ['data-role'] });

renderRole();