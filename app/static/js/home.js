(function () {
    const roleNames = {
        teacher: '\u0423\u0447\u0438\u0442\u0435\u043b\u044c',
        jury: '\u0416\u0443\u0440\u0456',
        student: '\u0423\u0447\u0435\u043d\u044c',
        admin: '\u0410\u0434\u043c\u0456\u043d',
        guest: '\u0413\u0456\u0441\u0442\u044c'
    };

    function normalizeRole(role) {
        const nextRole = String(role || '').toLowerCase();
        return Object.prototype.hasOwnProperty.call(roleNames, nextRole) ? nextRole : 'guest';
    }

    function renderRole() {
        const body = document.body;
        if (!body) return;

        const activeRole = normalizeRole(body.dataset.role);
        body.dataset.role = activeRole;

        const roleDisplay = document.getElementById('roleDisplay');
        if (roleDisplay) {
            roleDisplay.textContent = roleNames[activeRole];
        }
    }

    window.setRole = function setRole(role) {
        const body = document.body;
        if (!body) return;

        body.dataset.role = normalizeRole(role);
        renderRole();
    };

    document.addEventListener('click', function (event) {
        const button = event.target.closest('.role-switcher button[data-role]');
        if (!button) return;

        window.setRole(button.dataset.role);
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', renderRole, { once: true });
    } else {
        renderRole();
    }
})();
