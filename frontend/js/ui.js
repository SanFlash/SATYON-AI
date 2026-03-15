/* ═══════════════════════════════════════════════
   SATYON-AI - UI Interactions & Rendering
   ═══════════════════════════════════════════════ */

const SatyonUI = {
    state: {
        currentTab: 'all',
        searchResults: null,
        devMode: false,
        researchMode: false,
    },

    init() {
        this.initSourceTabs();
        this.initSettings();
        this.initModeButtons();
        this.initNewSearchButton();
    },

    /* ─── Source Tabs ─── */
    initSourceTabs() {
        document.querySelectorAll('.source-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchTab(tab.dataset.tab);
            });
        });
    },

    switchTab(tabId) {
        this.state.currentTab = tabId;

        // Update active state
        document.querySelectorAll('.source-tab').forEach(t => t.classList.remove('active'));
        document.querySelector(`.source-tab[data-tab="${tabId}"]`)?.classList.add('active');

        // Re-render results based on tab
        if (this.state.searchResults) {
            this.renderResults(this.state.searchResults, tabId);
        }
    },

    /* ─── Render Results ─── */
    renderResults(data, activeTab = 'all') {
        this.state.searchResults = data;

        // Update header
        document.getElementById('results-query-title').textContent = `Results for "${data.query}"`;
        document.getElementById('results-count').textContent = `${data.total_results} results`;
        document.getElementById('results-time').textContent = `in ${data.elapsed_seconds}s`;

        // Category badge
        const cat = data.classification?.category || 'general';
        const categoryBadge = document.getElementById('results-category');
        categoryBadge.textContent = cat;

        // Update tab counts
        this.updateTabCounts(data);

        // Render AI Summary Parts
        this.renderAISummary(data.ai_summary);
        this.renderAIReasoningTree(data.ai_summary?.reasoning_steps);
        
        // Data Explorer Banner
        this.renderDataExplorerBanner(cat);

        // Render result cards
        this.renderResultCards(data, activeTab);

        // Show/hide panels based on tab
        const summaryPanel = document.getElementById('ai-summary-panel');
        const resultsContainer = document.getElementById('results-list-container');

        if (activeTab === 'ai-summary') {
            summaryPanel.classList.remove('hidden');
            summaryPanel.classList.remove('lg:col-span-1');
            summaryPanel.classList.add('lg:col-span-3');
            resultsContainer.classList.add('hidden');
        } else {
            summaryPanel.classList.remove('hidden', 'lg:col-span-3');
            summaryPanel.classList.add('lg:col-span-1');
            resultsContainer.classList.remove('hidden');
        }
    },

    /* ─── Update Tab Counts ─── */
    updateTabCounts(data) {
        const bySource = data.results_by_source || {};

        document.querySelectorAll('.source-tab').forEach(tab => {
            const tabId = tab.dataset.tab;
            let count = 0;

            if (tabId === 'all') {
                count = data.total_results || 0;
            } else if (tabId === 'ai-summary') {
                count = data.ai_summary ? 1 : 0;
            } else {
                count = (bySource[tabId] || []).length;
            }

            // Remove existing count badge
            const existing = tab.querySelector('.count-badge');
            if (existing) existing.remove();

            // Add count badge
            if (count > 0) {
                const badge = document.createElement('span');
                badge.className = 'count-badge';
                badge.textContent = count;
                tab.appendChild(badge);
            }
        });
    },

    /* ─── Render AI Summary ─── */
    renderAISummary(summary) {
        const contentEl = document.getElementById('ai-summary-content');
        const reasoningSection = document.getElementById('ai-reasoning-section');
        const reasoningTree = document.getElementById('ai-reasoning-tree');
        const insightsSection = document.getElementById('ai-insights-section');
        const insightsList = document.getElementById('ai-insights-list');
        const recsSection = document.getElementById('ai-recommendations-section');
        const recsList = document.getElementById('ai-recommendations-list');
        const confidenceEl = document.getElementById('ai-confidence');

        if (!summary) {
            contentEl.innerHTML = '<p class="text-dark-200 italic">AI summary not available. Configure an API key in settings for AI-powered summaries.</p>';
            reasoningSection.classList.add('hidden');
            insightsSection.classList.add('hidden');
            recsSection.classList.add('hidden');
            return;
        }

        // Render summary markdown
        const summaryText = summary.summary || '';
        try {
            contentEl.innerHTML = marked.parse(summaryText);
        } catch (e) {
            contentEl.textContent = summaryText;
        }

        // AI Reasoning Tree
        const steps = summary.reasoning_steps || [];
        if (steps.length > 0) {
            reasoningSection.classList.remove('hidden');
            reasoningTree.innerHTML = steps.map((step, idx) => `
                <div class="relative flex items-start gap-4 group">
                    <div class="z-10 w-4 h-4 rounded-full bg-dark-800 border-2 border-neon-cyan flex items-center justify-center mt-1 scale-100 group-hover:scale-125 transition-transform duration-300">
                        <div class="w-1 h-1 bg-neon-cyan rounded-full"></div>
                    </div>
                    <div class="flex-1 text-[11px] leading-relaxed text-dark-100 group-hover:text-white transition-colors">
                        <span class="text-neon-cyan font-bold mr-1">STEP ${idx + 1}:</span>
                        ${this.escapeHtml(step)}
                    </div>
                </div>
            `).join('');
        } else {
            reasoningSection.classList.add('hidden');
        }

        // Confidence
        const conf = summary.confidence || 0;
        const confPercent = Math.round(conf * 100);
        const aiPowered = summary.ai_powered !== false;
        confidenceEl.textContent = aiPowered
            ? `AI Confidence: ${confPercent}%`
            : 'Aggregated Summary (No AI Key)';

        // Key Insights
        const insights = summary.key_insights || [];
        if (insights.length > 0) {
            insightsSection.classList.remove('hidden');
            insightsList.innerHTML = insights.map(i =>
                `<li>${this.escapeHtml(i)}</li>`
            ).join('');
        } else {
            insightsSection.classList.add('hidden');
        }

        // Recommendations
        const recs = summary.recommendations || [];
        if (recs.length > 0) {
            recsSection.classList.remove('hidden');
            recsList.innerHTML = recs.map(r =>
                `<li>${this.escapeHtml(r)}</li>`
            ).join('');
        } else {
            recsSection.classList.add('hidden');
        }
    },

    /* ─── Render AI Reasoning Tree ─── */
    renderAIReasoningTree(steps) {
        const section = document.getElementById('ai-reasoning-section');
        const treeContainer = document.getElementById('ai-reasoning-tree');

        if (!steps || steps.length === 0) {
            section.classList.add('hidden');
            return;
        }

        section.classList.remove('hidden');
        treeContainer.innerHTML = `
            <div class="absolute left-[7px] top-1 bottom-3 w-px bg-gradient-to-b from-neon-cyan/50 via-primary-500/30 to-transparent"></div>
        ` + steps.map((step, idx) => `
            <div class="reasoning-node group" style="--delay: ${idx * 0.2}s">
                <div class="node-dot absolute left-[-13px] top-1.5 w-2.5 h-2.5 rounded-full bg-dark-800 border-2 border-neon-cyan group-hover:bg-neon-cyan transition-all duration-300"></div>
                <p class="text-[13px] text-dark-100 group-hover:text-white transition-colors duration-300">${this.escapeHtml(step)}</p>
            </div>
        `).join('');

        // Animate the tree appearance
        gsap.from('#ai-reasoning-tree .reasoning-node', {
            x: -10,
            opacity: 0,
            duration: 0.5,
            stagger: 0.1,
            ease: 'power2.out'
        });
    },

    /* ─── Render Data Explorer Banner ─── */
    renderDataExplorerBanner(category) {
        const resultsHeader = document.getElementById('results-header');
        const existingBanner = document.getElementById('dataset-explorer-banner');
        if (existingBanner) existingBanner.remove();

        if (category === 'dataset') {
            const banner = document.createElement('div');
            banner.id = 'dataset-explorer-banner';
            banner.className = 'mt-4 p-4 rounded-2xl bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-500/30 flex items-center justify-between transition-all hover:border-blue-500/50';
            banner.innerHTML = `
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center text-2xl">📊</div>
                    <div>
                        <h4 class="text-sm font-bold text-white">Dataset explorer mode active</h4>
                        <p class="text-xs text-blue-200/70">Optimized search for CSV, JSON, and Kaggle collections.</p>
                    </div>
                </div>
                <button class="px-4 py-2 rounded-lg bg-blue-600/80 hover:bg-blue-600 text-xs font-bold text-white transition-all">
                    Open Insights
                </button>
            `;
            resultsHeader.appendChild(banner);
            gsap.from(banner, { y: 20, opacity: 0, duration: 0.5, ease: 'power3.out' });
        }
    },

    /* ─── Render Result Cards ─── */
    renderResultCards(data, activeTab = 'all') {
        const container = document.getElementById('results-list');
        container.innerHTML = '';

        let results = [];

        if (activeTab === 'all' || activeTab === 'ai-summary') {
            results = data.combined_results || [];
        } else {
            results = (data.results_by_source || {})[activeTab] || [];
        }

        if (results.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>No results found</h3>
                    <p>Try a different search term or check another source tab</p>
                </div>
            `;
            return;
        }

        results.forEach((result, index) => {
            const card = this.createResultCard(result, index);
            container.appendChild(card);
            SatyonAnimations.initCardHover(card);
        });
    },

    /* ─── Create Single Result Card ─── */
    createResultCard(result, index) {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.dataset.source = result.source || 'unknown';
        card.style.animationDelay = `${index * 0.05}s`;

        const sourceIcon = result.source_icon || '🔗';
        const sourceName = (result.source || 'unknown').replace(/^\w/, c => c.toUpperCase());
        const title = this.escapeHtml(result.title || 'Untitled');
        const url = result.url || '#';
        const displayUrl = url.length > 60 ? url.substring(0, 60) + '...' : url;
        const snippet = this.escapeHtml(result.snippet || '');

        // Extra info for specific sources
        let extraHtml = '';
        const extra = result.extra;
        if (extra) {
            if (result.source === 'github' && extra.stars !== undefined) {
                extraHtml = `
                    <div class="flex items-center gap-3 mt-2 text-xs text-dark-200">
                        <span>⭐ ${extra.stars?.toLocaleString()}</span>
                        <span>🍴 ${extra.forks?.toLocaleString()}</span>
                        <span>📝 ${extra.language || 'Unknown'}</span>
                    </div>
                `;
            } else if (result.source === 'stackoverflow' && extra.score !== undefined) {
                extraHtml = `
                    <div class="flex items-center gap-3 mt-2 text-xs text-dark-200">
                        <span>👍 Score: ${extra.score}</span>
                        <span>💬 ${extra.answer_count} answers</span>
                        <span>${extra.is_answered ? '✅ Answered' : '⏳ Open'}</span>
                        <span>👁️ ${extra.view_count?.toLocaleString()} views</span>
                    </div>
                `;
            } else if (result.source === 'arxiv' && extra.authors) {
                extraHtml = `
                    <div class="flex items-center gap-3 mt-2 text-xs text-dark-200">
                        <span>👤 ${extra.authors?.slice(0, 2).join(', ')}</span>
                        <span>📅 ${extra.published}</span>
                    </div>
                `;
            } else if (result.source === 'kaggle' && extra.downloads !== undefined) {
                extraHtml = `
                    <div class="flex items-center gap-3 mt-2 text-xs text-dark-200">
                        <span>📥 ${extra.downloads?.toLocaleString()} downloads</span>
                        <span>🗳️ ${extra.votes?.toLocaleString()} votes</span>
                        <span>💾 ${this.formatBytes(extra.size)}</span>
                    </div>
                `;
            } else if (result.source === 'youtube' && extra.channel) {
                extraHtml = `
                    <div class="flex items-center gap-3 mt-2 text-xs text-dark-200">
                        <span>📢 ${extra.channel}</span>
                        <span>📅 ${extra.published}</span>
                    </div>
                `;
            }
        }

        card.innerHTML = `
            <div class="flex items-start justify-between gap-3">
                <div class="result-source-tag">
                    <span>${sourceIcon}</span>
                    <span>${sourceName}</span>
                </div>
                <a href="${url}" target="_blank" rel="noopener" class="text-dark-300 hover:text-white transition-colors" onclick="event.stopPropagation()">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                </a>
            </div>
            <h3 class="result-title">${title}</h3>
            <p class="result-url">${this.escapeHtml(displayUrl)}</p>
            <p class="result-snippet">${snippet}</p>
            ${extraHtml}
        `;

        card.addEventListener('click', (e) => {
            if (e.target.closest('a')) return;
            window.open(url, '_blank');
        });

        return card;
    },

    /* ─── Mode Buttons ─── */
    initModeButtons() {
        const devBtn = document.getElementById('btn-dev-mode');
        const researchBtn = document.getElementById('btn-research-mode');

        devBtn.addEventListener('click', () => {
            this.state.devMode = !this.state.devMode;
            devBtn.classList.toggle('active', this.state.devMode);
            if (this.state.devMode) {
                this.state.researchMode = false;
                researchBtn.classList.remove('active');
            }
        });

        researchBtn.addEventListener('click', () => {
            this.state.researchMode = !this.state.researchMode;
            researchBtn.classList.toggle('active', this.state.researchMode);
            if (this.state.researchMode) {
                this.state.devMode = false;
                devBtn.classList.remove('active');
            }
        });
    },

    /* ─── New Search Button ─── */
    initNewSearchButton() {
        document.getElementById('btn-new-search').addEventListener('click', () => {
            SatyonSearch.goHome();
        });
    },

    /* ─── Settings Modal ─── */
    initSettings() {
        const modal = document.getElementById('settings-modal');
        const openBtn = document.getElementById('btn-settings');
        const closeBtn = document.getElementById('btn-close-settings');
        const saveBtn = document.getElementById('btn-save-settings');
        const resetBtn = document.getElementById('btn-reset-settings');

        openBtn.addEventListener('click', () => {
            modal.classList.remove('hidden');
            gsap.from('.settings-panel', { y: 30, opacity: 0, duration: 0.4, ease: 'power3.out' });
            this.loadSettings();
        });

        closeBtn.addEventListener('click', () => this.closeSettings());

        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeSettings();
        });

        saveBtn.addEventListener('click', () => this.saveSettings());
        resetBtn.addEventListener('click', () => this.resetSettings());

        // Populate source toggles
        this.populateSourceToggles();
    },

    closeSettings() {
        document.getElementById('settings-modal').classList.add('hidden');
    },

    populateSourceToggles() {
        const container = document.getElementById('source-toggles');
        const sources = [
            { id: 'google', name: 'Google', icon: '🔍' },
            { id: 'wikipedia', name: 'Wikipedia', icon: '📚' },
            { id: 'stackoverflow', name: 'StackOverflow', icon: '💬' },
            { id: 'github', name: 'GitHub', icon: '🐙' },
            { id: 'kaggle', name: 'Kaggle', icon: '📊' },
            { id: 'arxiv', name: 'ArXiv', icon: '📄' },
            { id: 'youtube', name: 'YouTube', icon: '🎥' },
        ];

        container.innerHTML = sources.map(s => `
            <div class="source-toggle active" data-source="${s.id}">
                <div class="toggle-dot"></div>
                <span class="text-sm">${s.icon}</span>
                <span class="text-xs font-medium text-dark-100">${s.name}</span>
            </div>
        `).join('');

        container.querySelectorAll('.source-toggle').forEach(toggle => {
            toggle.addEventListener('click', () => {
                toggle.classList.toggle('active');
            });
        });
    },

    loadSettings() {
        const settings = JSON.parse(localStorage.getItem('satyon-settings') || '{}');
        document.getElementById('setting-api-url').value = settings.apiUrl || 'http://localhost:8000';
        document.getElementById('setting-openai-key').value = settings.openaiKey || '';
        document.getElementById('setting-serpapi-key').value = settings.serpapiKey || '';
        document.getElementById('setting-github-token').value = settings.githubToken || '';

        // Load active sources
        const activeSources = settings.activeSources || ['google', 'wikipedia', 'stackoverflow', 'github', 'kaggle', 'arxiv', 'youtube'];
        document.querySelectorAll('.source-toggle').forEach(toggle => {
            const src = toggle.dataset.source;
            toggle.classList.toggle('active', activeSources.includes(src));
        });
    },

    saveSettings() {
        const activeSources = Array.from(document.querySelectorAll('.source-toggle.active'))
            .map(t => t.dataset.source);

        const settings = {
            apiUrl: document.getElementById('setting-api-url').value || 'http://localhost:8000',
            openaiKey: document.getElementById('setting-openai-key').value,
            serpapiKey: document.getElementById('setting-serpapi-key').value,
            githubToken: document.getElementById('setting-github-token').value,
            activeSources: activeSources,
        };

        localStorage.setItem('satyon-settings', JSON.stringify(settings));
        this.closeSettings();

        // Show save confirmation
        this.showToast('Settings saved successfully! ✅');
    },

    resetSettings() {
        localStorage.removeItem('satyon-settings');
        this.loadSettings();
        this.showToast('Settings reset to defaults 🔄');
    },

    /* ─── Toast Notification ─── */
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-6 right-6 z-[100] px-5 py-3 rounded-xl text-sm font-medium text-white';
        toast.style.background = 'linear-gradient(135deg, rgba(76, 110, 245, 0.9), rgba(112, 72, 232, 0.9))';
        toast.style.boxShadow = '0 8px 32px rgba(76, 110, 245, 0.3)';
        toast.style.backdropFilter = 'blur(10px)';
        toast.textContent = message;
        document.body.appendChild(toast);

        gsap.fromTo(toast, {
            y: 20, opacity: 0,
        }, {
            y: 0, opacity: 1, duration: 0.4, ease: 'power3.out',
        });

        setTimeout(() => {
            gsap.to(toast, {
                y: 20, opacity: 0, duration: 0.3, ease: 'power3.in',
                onComplete: () => toast.remove(),
            });
        }, 3000);
    },

    /* ─── Utility ─── */
    formatBytes(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
};
