document.addEventListener('DOMContentLoaded', () => {
    const lists = Array.from(document.querySelectorAll('.tournament-list'));
    if (lists.length === 0) return;

    const seriesFilters = Array.from(document.querySelectorAll('input[data-filter="series"]'));
    const formatFilters = Array.from(document.querySelectorAll('input[data-filter="format"]'));
    const searchInput = document.querySelector('#tournamentSearch');
    const searchButton = document.querySelector('#tournamentSearchBtn');
    let searchQuery = '';

    const applyFilters = () => {
        const selectedSeries = seriesFilters.filter((input) => input.checked).map((input) => input.value);
        const selectedFormats = formatFilters.filter((input) => input.checked).map((input) => input.value);

        const normalizedQuery = searchQuery.trim().toLowerCase();

        lists.forEach((list) => {
            const cards = Array.from(list.querySelectorAll('.tournament-card'));
            let visibleCount = 0;

            cards.forEach((card) => {
                const cardSeries = card.dataset.series;
                const cardFormat = card.dataset.format;
                const title = (card.querySelector('h3')?.textContent || '').toLowerCase();

                const seriesMatch = selectedSeries.length === 0 || selectedSeries.includes(cardSeries);
                const formatMatch = selectedFormats.length === 0 || selectedFormats.includes(cardFormat);
                const searchMatch = normalizedQuery.length === 0 || title.includes(normalizedQuery);

                const isVisible = seriesMatch && formatMatch && searchMatch;
                card.hidden = !isVisible;
                if (isVisible) {
                    visibleCount += 1;
                }
            });

            list.classList.toggle('is-empty', visibleCount === 0);
        });
    };

    [...seriesFilters, ...formatFilters].forEach((input) => {
        input.addEventListener('change', applyFilters);
    });

    if (searchButton && searchInput) {
        searchButton.addEventListener('click', () => {
            searchQuery = searchInput.value;
            applyFilters();
        });

        searchInput.addEventListener('keydown', (event) => {
            if (event.key !== 'Enter') return;
            event.preventDefault();
            searchQuery = searchInput.value;
            applyFilters();
        });
    }

    applyFilters();

    // Переключаємо елементи дій залежно від участі користувача в турнірі
    const detailCards = Array.from(document.querySelectorAll('.tournament-detail'));
    detailCards.forEach((card) => {
        const isParticipant = card.dataset.participant === 'true';
        const submitBtn = card.querySelector('.participation-only');
        const participationNote = card.querySelector('.participation-note');

        if (submitBtn) {
            submitBtn.hidden = !isParticipant;
            submitBtn.disabled = !isParticipant;
            submitBtn.setAttribute('aria-disabled', String(!isParticipant));
        }

        if (participationNote) {
            participationNote.hidden = isParticipant;
        }
    });

    // Модалка здачі роботи
    const submitModal = document.getElementById('submitModal');
    const submissionButtons = Array.from(document.querySelectorAll('.submit-btn'));
    const modalCloseButtons = Array.from(document.querySelectorAll('.modal-close'));
    const modalTournament = document.getElementById('submitModalTournament');
    const modalDeadline = document.getElementById('submitModalDeadline');
    const submissionType = document.getElementById('submissionType');
    const fileGroup = document.getElementById('file-group');
    const linkGroup = document.getElementById('link-group');
    const imageGroup = document.getElementById('image-group');
    const submitForm = document.getElementById('submitForm');

    const toggleGroups = () => {
        if (!submissionType) return;
        const value = submissionType.value;
        fileGroup.hidden = value !== 'file';
        linkGroup.hidden = value !== 'link';
        imageGroup.hidden = value !== 'image';
    };

    const openModal = (btn) => {
        if (!submitModal) return;
        const title = btn?.dataset.tournamentTitle || 'Турнір';
        const deadline = btn?.dataset.deadline || '';
        if (modalTournament) modalTournament.textContent = title;
        if (modalDeadline) modalDeadline.textContent = deadline ? `Дедлайн: ${deadline}` : '';
        submitModal.classList.add('is-open');
        submitModal.setAttribute('aria-hidden', 'false');
        toggleGroups();
    };

    const closeModal = () => {
        if (!submitModal) return;
        submitModal.classList.remove('is-open');
        submitModal.setAttribute('aria-hidden', 'true');
    };

    submissionButtons.forEach((btn) => {
        btn.addEventListener('click', () => openModal(btn));
    });

    modalCloseButtons.forEach((btn) => btn.addEventListener('click', closeModal));

    if (submitModal) {
        submitModal.addEventListener('click', (event) => {
            if (event.target === submitModal) {
                closeModal();
            }
        });
    }

    if (submissionType) {
        submissionType.addEventListener('change', toggleGroups);
        toggleGroups();
    }

    if (submitForm) {
        submitForm.addEventListener('submit', (event) => {
            event.preventDefault();
            // Тут можна відправити форму через fetch; поки що показуємо підтвердження
            alert('Роботу надіслано! (демо-стан)');
            closeModal();
            submitForm.reset();
            toggleGroups();
        });
    }
});
