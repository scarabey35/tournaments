document.addEventListener('DOMContentLoaded', () => {
    const list = document.querySelector('.tournament-list');
    if (!list) return;

    const cards = Array.from(list.querySelectorAll('.tournament-card'));
    const seriesFilters = Array.from(document.querySelectorAll('input[data-filter="series"]'));
    const formatFilters = Array.from(document.querySelectorAll('input[data-filter="format"]'));
    const searchInput = document.querySelector('#tournamentSearch');
    const searchButton = document.querySelector('#tournamentSearchBtn');
    let searchQuery = '';

    const applyFilters = () => {
        const selectedSeries = seriesFilters.filter((input) => input.checked).map((input) => input.value);
        const selectedFormats = formatFilters.filter((input) => input.checked).map((input) => input.value);

        const normalizedQuery = searchQuery.trim().toLowerCase();
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
});
