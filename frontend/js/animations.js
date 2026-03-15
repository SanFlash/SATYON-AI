/* ═══════════════════════════════════════════════
   SATYON-AI - GSAP Animations
   ═══════════════════════════════════════════════ */

const SatyonAnimations = {
    init() {
        this.initHeroAnimations();
        this.initScrollAnimations();
        this.initOrbAnimations();
    },

    /* ─── Hero Section Entrance ─── */
    initHeroAnimations() {
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        tl.from('#hero-title h1 span', {
            y: 80,
            opacity: 0,
            duration: 1,
            stagger: 0.15,
            ease: 'elastic.out(1, 0.5)',
        })
        .from('#hero-title p span', {
            y: 20,
            opacity: 0,
            duration: 0.6,
            stagger: 0.1,
        }, '-=0.5')
        .from('.search-box-wrapper', {
            y: 40,
            opacity: 0,
            scale: 0.95,
            duration: 0.8,
        }, '-=0.3')
        .from('.suggestion-chip', {
            y: 20,
            opacity: 0,
            duration: 0.4,
            stagger: 0.05,
        }, '-=0.3')
        .from('.source-badge', {
            y: 20,
            opacity: 0,
            scale: 0.8,
            duration: 0.4,
            stagger: 0.06,
        }, '-=0.2');
    },

    /* ─── Scroll-based Animations ─── */
    initScrollAnimations() {
        window.addEventListener('scroll', () => {
            const navbar = document.getElementById('navbar');
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    },

    /* ─── Background Orb Animations ─── */
    initOrbAnimations() {
        gsap.to('.orb-1', {
            x: 'random(-50, 50)',
            y: 'random(-50, 50)',
            duration: 15,
            repeat: -1,
            yoyo: true,
            ease: 'sine.inOut',
        });
        gsap.to('.orb-2', {
            x: 'random(-40, 40)',
            y: 'random(-40, 40)',
            duration: 18,
            repeat: -1,
            yoyo: true,
            ease: 'sine.inOut',
        });
        gsap.to('.orb-3', {
            x: 'random(-60, 60)',
            y: 'random(-60, 60)',
            duration: 20,
            repeat: -1,
            yoyo: true,
            ease: 'sine.inOut',
        });
    },

    /* ─── Transition from Home to Results ─── */
    animateToResults() {
        return new Promise((resolve) => {
            const tl = gsap.timeline({
                onComplete: resolve,
                defaults: { ease: 'power3.inOut' },
            });

            tl.to('#hero-title', {
                y: -30,
                opacity: 0,
                duration: 0.4,
            })
            .to('#suggestions', {
                y: -20,
                opacity: 0,
                duration: 0.3,
            }, '-=0.2')
            .to('#source-icons', {
                y: -20,
                opacity: 0,
                duration: 0.3,
            }, '-=0.2')
            .to('#search-container', {
                y: -20,
                duration: 0.3,
            }, '-=0.2');
        });
    },

    /* ─── Animate Results In ─── */
    animateResultsIn() {
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        tl.from('#results-header', {
            y: 30,
            opacity: 0,
            duration: 0.5,
        })
        .from('.source-tab', {
            y: 20,
            opacity: 0,
            duration: 0.3,
            stagger: 0.04,
        }, '-=0.2')
        .from('.ai-summary-card', {
            x: -30,
            opacity: 0,
            duration: 0.5,
        }, '-=0.1')
        .from('.result-card', {
            y: 30,
            opacity: 0,
            duration: 0.4,
            stagger: 0.06,
        }, '-=0.3');
    },

    /* ─── Transition Back to Home ─── */
    animateToHome() {
        return new Promise((resolve) => {
            const tl = gsap.timeline({
                onComplete: resolve,
                defaults: { ease: 'power3.inOut' },
            });

            tl.to('#results-section', {
                y: 30,
                opacity: 0,
                duration: 0.4,
            });
        });
    },

    /* ─── Animate Home Back In ─── */
    animateHomeIn() {
        gsap.set('#hero-title', { clearProps: 'all' });
        gsap.set('#suggestions', { clearProps: 'all' });
        gsap.set('#source-icons', { clearProps: 'all' });
        gsap.set('#search-container', { clearProps: 'all' });

        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

        tl.from('#hero-title', {
            y: 30,
            opacity: 0,
            duration: 0.5,
        })
        .from('#search-container', {
            y: 20,
            opacity: 0,
            duration: 0.4,
        }, '-=0.2')
        .from('#suggestions', {
            y: 15,
            opacity: 0,
            duration: 0.3,
        }, '-=0.1')
        .from('#source-icons', {
            y: 15,
            opacity: 0,
            duration: 0.3,
        }, '-=0.1');
    },

    /* ─── Loading Animation ─── */
    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.classList.remove('hidden');
        gsap.fromTo(overlay, {
            opacity: 0,
        }, {
            opacity: 1,
            duration: 0.3,
        });
    },

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        gsap.to(overlay, {
            opacity: 0,
            duration: 0.3,
            onComplete: () => overlay.classList.add('hidden'),
        });
    },

    /* ─── Pulse Effect on Search ─── */
    pulseSearch() {
        gsap.fromTo('.search-glow', {
            opacity: 0.8,
        }, {
            opacity: 0,
            duration: 1,
            ease: 'power2.out',
        });
    },

    /* ─── Card Hover Effect ─── */
    initCardHover(card) {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                scale: 1.01,
                duration: 0.3,
                ease: 'power2.out',
            });
        });
        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                scale: 1,
                duration: 0.3,
                ease: 'power2.out',
            });
        });
    },
};
