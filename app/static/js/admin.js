
document.addEventListener("DOMContentLoaded", () => {
    const dashboard = document.querySelector(".admin-dashboard-grid");

    if (dashboard) {
        dashboard.addEventListener("click", (event) => {
            const button = event.target.closest("[data-admin-action]");
            if (!button) return;

            const card = button.closest(".tournament-card");
            const title = card?.querySelector("h3")?.textContent?.trim() || "Турнір";
            const action = button.dataset.adminAction;

            if (action === "edit") {
                alert(`Редагування "${title}" — заглушка`);
                return;
            }

            if (action === "delete") {
                const confirmed = confirm(`Видалити "${title}"? Це заглушка, нічого не зміниться.`);
                if (confirmed) {
                    alert(`"${title}" не видалено — це заглушка`);
                }
                return;
            }

            if (action === "view") {
                alert(`Перегляд "${title}" — заглушка`);
            }
        });
    }
});
