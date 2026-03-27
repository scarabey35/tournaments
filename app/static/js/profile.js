const body = document.body;
const roleDisplay = document.getElementById('roleDisplay');

const roleNames = {
    teacher: 'Вчитель',
    jury: 'Журі',
    student: 'Учень',
    admin: 'Адмін',
    guest: 'Гість'
};

const currentRole = (body.dataset.role || 'guest').toLowerCase();

if (roleDisplay) {
    roleDisplay.textContent = roleNames[currentRole] || roleNames.guest;
}
