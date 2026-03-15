/* ═══════════════════════════════════════════════
   SATYON-AI - Search Logic & API Communication
   ═══════════════════════════════════════════════ */

const SatyonSearch = {
    isSearching: false,

    /* ─── Get API Base URL ─── */
    getApiUrl() {
        const settings = JSON.parse(localStorage.getItem('satyon-settings') || '{}');
        // Use relative URL by default in production, or the saved setting if provided
        return settings.apiUrl || '';
    },

    /* ─── Perform Search ─── */
    async search(query) {
        if (!query.trim() || this.isSearching) return;

        this.isSearching = true;
        const searchInput = document.getElementById('search-input');
        const searchLoading = document.getElementById('search-loading');
        const searchBtn = document.getElementById('search-btn');

        // Show loading
        searchLoading.classList.remove('hidden');
        searchBtn.classList.add('hidden');
        SatyonAnimations.showLoading();
        SatyonAnimations.pulseSearch();

        // Update loading status messages
        this.animateLoadingStatus();

        try {
            // Determine sources based on mode
            let sources = null;
            const settings = JSON.parse(localStorage.getItem('satyon-settings') || '{}');

            if (SatyonUI.state.devMode) {
                sources = 'stackoverflow,github,google,youtube';
            } else if (SatyonUI.state.researchMode) {
                sources = 'arxiv,google,wikipedia,github';
            } else if (settings.activeSources) {
                sources = settings.activeSources.join(',');
            }

            // Build API URL
            const apiUrl = this.getApiUrl();
            const params = new URLSearchParams({ q: query });
            if (sources) params.set('sources', sources);
            params.set('summarize', 'true');

            const response = await fetch(`${apiUrl}/api/search?${params}`);

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            const data = await response.json();

            // Hide loading
            SatyonAnimations.hideLoading();
            searchLoading.classList.add('hidden');
            searchBtn.classList.remove('hidden');

            // Transition to results
            await this.showResults(data);

        } catch (error) {
            console.error('Search error:', error);
            SatyonAnimations.hideLoading();
            searchLoading.classList.add('hidden');
            searchBtn.classList.remove('hidden');

            // If API is not running, use fallback local search
            console.log('Backend not available, using client-side demo...');
            const demoData = this.generateDemoResults(query);
            await this.showResults(demoData);
        }

        this.isSearching = false;
    },

    /* ─── Show Results ─── */
    async showResults(data) {
        const hero = document.getElementById('hero-section');
        const results = document.getElementById('results-section');

        // Animate out hero
        await SatyonAnimations.animateToResults();

        // Switch sections
        hero.classList.add('hidden');
        results.classList.remove('hidden');

        // Reset results
        gsap.set('#results-section', { clearProps: 'all' });

        // Render results
        SatyonUI.renderResults(data);

        // Animate results in
        SatyonAnimations.animateResultsIn();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    /* ─── Go Back Home ─── */
    async goHome() {
        const hero = document.getElementById('hero-section');
        const results = document.getElementById('results-section');

        await SatyonAnimations.animateToHome();

        results.classList.add('hidden');
        hero.classList.remove('hidden');

        gsap.set('#hero-section', { clearProps: 'all' });
        SatyonAnimations.animateHomeIn();

        // Focus search input
        const input = document.getElementById('search-input');
        input.value = '';
        input.focus();

        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    /* ─── Animate Loading Status Text ─── */
    animateLoadingStatus() {
        const statusEl = document.getElementById('loading-status');
        const messages = [
            'Querying Google, GitHub, Wikipedia...',
            'Searching StackOverflow & ArXiv...',
            'Fetching Kaggle datasets...',
            'Aggregating results...',
            'AI is analyzing data...',
            'Preparing your answer...',
        ];

        let i = 0;
        const interval = setInterval(() => {
            if (!this.isSearching || i >= messages.length) {
                clearInterval(interval);
                return;
            }
            gsap.to(statusEl, {
                opacity: 0,
                y: -5,
                duration: 0.2,
                onComplete: () => {
                    statusEl.textContent = messages[i];
                    gsap.to(statusEl, { opacity: 1, y: 0, duration: 0.2 });
                    i++;
                }
            });
        }, 1200);
    },

    /* ─── Generate Demo Results (No Backend) ─── */
    generateDemoResults(query) {
        const allSources = ['google', 'wikipedia', 'stackoverflow', 'github', 'kaggle', 'arxiv', 'youtube'];
        const sourceIcons = { google: '🔍', wikipedia: '📚', stackoverflow: '💬', github: '🐙', kaggle: '📊', arxiv: '📄', youtube: '🎥' };
        const sourceUrls = {
            google: `https://www.google.com/search?q=${encodeURIComponent(query)}`,
            wikipedia: `https://en.wikipedia.org/wiki/Special:Search?search=${encodeURIComponent(query)}`,
            stackoverflow: `https://stackoverflow.com/search?q=${encodeURIComponent(query)}`,
            github: `https://github.com/search?q=${encodeURIComponent(query)}`,
            kaggle: `https://www.kaggle.com/search?q=${encodeURIComponent(query)}`,
            arxiv: `https://arxiv.org/search/?query=${encodeURIComponent(query)}`,
            youtube: `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`,
        };

        const resultsBySource = {};
        const combinedResults = [];

        allSources.forEach(src => {
            const results = this.generateSourceDemoResults(query, src, sourceIcons[src], sourceUrls[src]);
            resultsBySource[src] = results;
            combinedResults.push(...results);
        });

        // Classify query client-side
        const classification = this.classifyQueryLocal(query);
        const intent = { intent: 'explore', is_question: query.includes('?'), is_comparison: query.toLowerCase().includes(' vs '), entities: [] };

        // Generate fallback summary
        const summary = this.generateDemoSummary(query, combinedResults, classification);

        return {
            success: true,
            query: query,
            elapsed_seconds: (Math.random() * 2 + 0.5).toFixed(2),
            classification: classification,
            intent: intent,
            sources_searched: allSources,
            total_results: combinedResults.length,
            ai_summary: summary,
            results_by_source: resultsBySource,
            combined_results: combinedResults,
            cached: false,
        };
    },

    generateSourceDemoResults(query, source, icon, baseUrl) {
        const templates = {
            google: [
                { t: `${query} - Complete Guide & Overview`, s: `Comprehensive guide covering all aspects of ${query}. Learn from expert insights, tutorials, and practical examples.` },
                { t: `Understanding ${query}: A Deep Dive`, s: `Explore ${query} in depth with detailed explanations, use cases, and best practices from industry leaders.` },
                { t: `${query} - Latest Trends & Updates 2024`, s: `Stay current with the latest developments and innovations in ${query}. Breaking news, analysis, and expert opinions.` },
            ],
            wikipedia: [
                { t: `${query} - Wikipedia`, s: `${query} is a topic of significant importance. This article provides a detailed encyclopedia entry covering history, applications, and key concepts.` },
                { t: `History of ${query}`, s: `The evolution and historical development of ${query}, from its origins to modern applications.` },
            ],
            stackoverflow: [
                { t: `How to implement ${query}?`, s: `Score: 142 | Answers: 12 | Tags: programming, development`, extra: { score: 142, answer_count: 12, is_answered: true, view_count: 45230 } },
                { t: `Best practices for ${query}`, s: `Score: 89 | Answers: 8 | Tags: best-practices, architecture`, extra: { score: 89, answer_count: 8, is_answered: true, view_count: 23100 } },
                { t: `${query} - common issues and solutions`, s: `Score: 56 | Answers: 5 | Tags: debugging, troubleshooting`, extra: { score: 56, answer_count: 5, is_answered: true, view_count: 12800 } },
            ],
            github: [
                { t: `awesome-${query.toLowerCase().replace(/\s+/g, '-')}`, s: `⭐ 15,234 | 🔤 Python | A curated list of awesome ${query} resources, libraries, and tools.`, extra: { stars: 15234, language: 'Python', forks: 2341 } },
                { t: `${query.toLowerCase().replace(/\s+/g, '-')}-toolkit`, s: `⭐ 8,567 | 🔤 JavaScript | Production-ready toolkit for ${query} development.`, extra: { stars: 8567, language: 'JavaScript', forks: 1023 } },
            ],
            kaggle: [
                { t: `${query} Dataset - Comprehensive Collection`, s: `📊 High-quality dataset for ${query} research and analysis. Includes features, labels, and documentation.` },
                { t: `${query} - Competition Dataset`, s: `📊 Competition-grade dataset with ${query} data. Over 100K samples with annotations.` },
            ],
            arxiv: [
                { t: `A Survey on ${query}: Methods, Applications, and Challenges`, s: `📅 2024-01-15 | 👤 Smith, J., Chen, L. et al. | This comprehensive survey covers recent advances in ${query}...`, extra: { authors: ['Smith, J.', 'Chen, L.'], published: '2024-01-15' } },
                { t: `Deep Learning Approaches for ${query}`, s: `📅 2024-02-20 | 👤 Kumar, A., Wang, X. | We propose a novel deep learning framework for ${query}...`, extra: { authors: ['Kumar, A.', 'Wang, X.'], published: '2024-02-20' } },
            ],
            youtube: [
                { t: `${query} - Complete Tutorial for Beginners`, s: `Learn ${query} from scratch with this comprehensive step-by-step tutorial. Perfect for beginners and intermediate developers.` },
                { t: `${query} Crash Course - Full Tutorial`, s: `Master ${query} in one video. Covers all essential concepts with practical examples and projects.` },
            ],
        };

        const items = templates[source] || [];
        return items.map(item => ({
            title: item.t,
            url: baseUrl,
            snippet: item.s,
            source: source,
            source_icon: icon,
            extra: item.extra || {},
            relevance_score: Math.floor(Math.random() * 10) + 1,
        }));
    },

    classifyQueryLocal(query) {
        const q = query.toLowerCase();
        let category = 'general';
        let confidence = 0.3;

        if (/dataset|data|csv|kaggle|training data/i.test(q)) {
            category = 'dataset';
            confidence = 0.8;
        } else if (/code|implement|function|algorithm|python|javascript|api|how to code/i.test(q)) {
            category = 'code';
            confidence = 0.75;
        } else if (/research|paper|study|arxiv|survey|academic|thesis/i.test(q)) {
            category = 'research';
            confidence = 0.8;
        } else if (/tutorial|how to|guide|learn|beginner|course/i.test(q)) {
            category = 'tutorial';
            confidence = 0.7;
        }

        return {
            category: category,
            confidence: confidence,
            sources: ['google', 'wikipedia', 'stackoverflow', 'github', 'kaggle', 'arxiv', 'youtube'],
            keywords_matched: [],
        };
    },

    generateDemoSummary(query, results, classification) {
        const cat = classification.category;
        const sources = new Set(results.map(r => r.source));
        const sourcesList = Array.from(sources).map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(', ');

        let summaryText = `## Search Results for "${query}"\n\n`;
        summaryText += `Found **${results.length} results** across **${sources.size} sources** (${sourcesList}).\n\n`;
        summaryText += `Query was classified as **${cat}** with ${Math.round(classification.confidence * 100)}% confidence.\n\n`;

        // Add source-specific highlights
        sources.forEach(src => {
            const srcResults = results.filter(r => r.source === src);
            if (srcResults.length > 0) {
                summaryText += `### From ${src.charAt(0).toUpperCase() + src.slice(1)}\n`;
                srcResults.slice(0, 2).forEach(r => {
                    summaryText += `- **${r.title}**: ${r.snippet.substring(0, 120)}...\n`;
                });
                summaryText += '\n';
            }
        });

        return {
            summary: summaryText,
            key_insights: [
                `Query classified as '${cat}' category`,
                `Found results from ${sources.size} different sources`,
                `Total of ${results.length} relevant results aggregated`,
                'Start the FastAPI backend for live search results',
                'Add API keys in Settings for AI-powered summaries',
            ],
            recommendations: [
                'Review individual source tabs for detailed results',
                'Click on result links to access full content',
                'Configure API keys in Settings for real search data',
            ],
            confidence: 0.6,
            ai_powered: false,
        };
    },
};
