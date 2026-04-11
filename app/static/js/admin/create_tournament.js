document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#admin-create-tournament-form");

    if (!form) {
        return;
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const titleInput = form.querySelector("#title");
        const title = titleInput?.value?.trim() || "Турнір";

        alert(`"${title}" створено (заглушка)`);
        form.reset();
    });
});
