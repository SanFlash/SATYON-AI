/* ═══════════════════════════════════════════════
   SATYON-AI - Main Application Entry Point
   ═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all modules
    SatyonAnimations.init();
    SatyonUI.init();

    // ─── Search Input Handler ───
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            SatyonSearch.search(searchInput.value);
        }
    });

    searchBtn.addEventListener('click', () => {
        SatyonSearch.search(searchInput.value);
    });

    // ─── Suggestion Chips ───
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.dataset.query;
            searchInput.value = query;
            SatyonSearch.search(query);
        });
    });

    // ─── Keyboard Shortcuts ───
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
            searchInput.select();
        }

        // Escape to go home
        if (e.key === 'Escape') {
            const resultsSection = document.getElementById('results-section');
            if (!resultsSection.classList.contains('hidden')) {
                SatyonSearch.goHome();
            }
        }
    });

    // ─── Auto-focus search on load ───
    setTimeout(() => {
        searchInput.focus();
    }, 1500);

    // ─── Console branding ───
    console.log(
        '%c🧠 SATYON-AI %cv1.0.0',
        'color: #00fff5; font-size: 24px; font-weight: bold; text-shadow: 0 0 10px rgba(0,255,245,0.5);',
        'color: #a855f7; font-size: 14px; font-weight: normal; margin-left: 8px;'
    );
    console.log(
        '%cOne Search. One Answer. Multiple Sources.',
        'color: #909296; font-size: 12px; font-style: italic;'
    );
});
