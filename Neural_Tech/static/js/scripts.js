
document.addEventListener('DOMContentLoaded', () => {

    // ---- CURSOR GLOW ( // efecto visual que hace que un glow siga al cursor) ----
    const cursorGlow = document.getElementById('cursorGlow');
    if (cursorGlow) {
        document.addEventListener('mousemove', (e) => {
            cursorGlow.style.left = e.clientX + 'px';
            cursorGlow.style.top = e.clientY + 'px';
        });
    }

    // ---- NAVBAR: scroll effect (cambia estilo del navbar cuando haces scroll)----
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // ---- NAVBAR: mobile toggle ----
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('open');
            // Animate hamburger icon
            const spans = navToggle.querySelectorAll('span');
            navToggle.classList.toggle('active');
            if (navToggle.classList.contains('active')) {
                spans[0].style.transform = 'translateY(7px) rotate(45deg)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
            } else {
                spans[0].style.transform = '';
                spans[1].style.opacity = '';
                spans[2].style.transform = '';
            }
        });
        // Close menu on link click
        navLinks.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('open');
                navToggle.classList.remove('active');
            });
        });
    }

    // ---- SCROLL ANIMATION (custom AOS) ----
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -60px 0px'
    };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Don't unobserve — keep it visible
            }
        });
    }, observerOptions);

    //animaciones de los elementos
    const animatedEls = document.querySelectorAll(
        '[data-aos], .feature-card, .product-card, .tech-category, .metric-card, .step'
    );
    animatedEls.forEach(el => observer.observe(el));

    // ---- COUNTER ANIMATION ----
    function animateCounter(el) {
        const target = parseInt(el.getAttribute('data-count'));
        const duration = 1800;
        const start = performance.now();
        const easeOutQuart = t => 1 - Math.pow(1 - t, 4);

        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = easeOutQuart(progress);
            el.textContent = Math.round(eased * target);
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.textContent = target;
            }
        }
        requestAnimationFrame(update);
    }

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counters = entry.target.querySelectorAll('[data-count], .counter[data-count]');
                counters.forEach(c => animateCounter(c));
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    // Observe sections containing counters
    document.querySelectorAll('.hero-stats, .metrics-grid').forEach(section => {
        counterObserver.observe(section);
    });

    // Also observe individual counters not in those sections
    document.querySelectorAll('[data-count]').forEach(el => {
        counterObserver.observe(el.closest('section') || el);
    });

    // ---- METRIC BARS ANIMATION ----
    const metricObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.querySelectorAll('.metric-fill').forEach(bar => {
                    bar.style.animation = 'barFill 1.5s ease forwards';
                });
            }
        });
    }, { threshold: 0.3 });
    document.querySelectorAll('.metrics-grid').forEach(el => metricObserver.observe(el));

    // ---- CONTACT FORM VALIDATION ----
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {

        //validaciones del formulario
        contactForm.querySelectorAll('.form-input').forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => {
                if (input.classList.contains('error')) validateField(input);
            });
        });

        function validateField(field) {
            const errorEl = document.getElementById('error-' + field.id);
            let error = '';

            if (field.required && !field.value.trim()) {
                error = 'Este campo es obligatorio.';
            } else if (field.type === 'email' && field.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(field.value)) {
                    error = 'Ingresá un email valido.';
                }
            } else if (field.tagName === 'SELECT' && field.required && !field.value) {
                error = 'Seleccioná una opcion.';
            } else if (field.tagName === 'TEXTAREA' && field.required && field.value.trim().length < 10) {
                error = 'El mensaje debe tener al menos 10 caracteres.';
            }

            if (errorEl) errorEl.textContent = error;
            if (error) {
                field.style.borderColor = '#ff4d4d';
                field.classList.add('error');
            } else {
                field.style.borderColor = '';
                field.classList.remove('error');
            }
            return !error;
        }

        // Cvalidacion
        function validateCheckbox() {
            const checkbox = document.getElementById('acepta');
            const errorEl = document.getElementById('error-acepta');
            if (!checkbox.checked) {
                if (errorEl) errorEl.textContent = 'Debés aceptar la política de privacidad.';
                return false;
            }
            if (errorEl) errorEl.textContent = '';
            return true;
        }

  contactForm.addEventListener('submit', async (e) => {

    e.preventDefault();

    let valid = true;

    contactForm.querySelectorAll('.form-input').forEach(input => {
        if (!validateField(input)) {
            valid = false;
        }
    });

    if (!validateCheckbox()) {
        valid = false;
    }

    if (!valid) return;

    const btn = document.getElementById("submitBtn");
    btn.disabled = true;

    const formData = new FormData(contactForm);

    try {

        console.log("Enviando formulario...");

        const response = await fetch(
            contactForm.action,
            {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With":"XMLHttpRequest"
                }
            }
        );

        console.log("Status:",response.status);

        const text = await response.text();

        console.log("Respuesta cruda:");
        console.log(text);

        const data = JSON.parse(text);

        let old=document.querySelector(".success-message");

        if(old){
            old.remove();
        }

        const div=document.createElement("div");

        div.className="success-message";

        if(data.success){

            div.innerHTML=`
            <div class="success-icon">✓</div>

            <div class="success-content">
                <h4>Mensaje enviado</h4>
                <p>${data.message}</p>
            </div>
            `;

            contactForm.reset();

        }else{

            div.innerHTML=`
            <div class="error-content">
                <h4>Error</h4>
                <p>${data.message}</p>
            </div>
            `;
        }

        contactForm.parentNode.insertBefore(
            div,
            contactForm
        );

    }

    catch(error){

        console.log("ERROR:");
        console.log(error);

    }

    btn.disabled=false;

});

    // ---- GLITCH EFFECT en el subtitulo----
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        let glitchTimeout;
        function scheduleGlitch() {
            glitchTimeout = setTimeout(() => {
                heroTitle.classList.add('glitch');
                setTimeout(() => {
                    heroTitle.classList.remove('glitch');
                    scheduleGlitch();
                }, 200);
            }, Math.random() * 3000 + 1000);
        }
        scheduleGlitch();
    }

    // ---- TILT EFFECT on cards ----
    document.querySelectorAll('.product-card, .feature-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `perspective(800px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg) translateY(-4px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });

    // ---- TYPING EFFECT en subtitutlo ) ----
    const heroSubtitle = document.querySelector('.hero-subtitle');
    if (heroSubtitle) {
        const text = heroSubtitle.textContent;
        heroSubtitle.textContent = '';
        heroSubtitle.style.opacity = '1';
        let i = 0;
        // Small delay before starting
        setTimeout(() => {
            const interval = setInterval(() => {
                heroSubtitle.textContent += text[i];
                i++;
                if (i >= text.length) clearInterval(interval);
            }, 18);
        }, 1000);
    }

    // ---- PARTICLES en HEro  ----
    const particlesContainer = document.getElementById('particles');
    if (particlesContainer) {
        for (let i = 0; i < 30; i++) {
            const dot = document.createElement('div');
            dot.style.cssText = `
                position: absolute;
                width: ${Math.random() * 3 + 1}px;
                height: ${Math.random() * 3 + 1}px;
                background: #00ADB5;
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                opacity: ${Math.random() * 0.5 + 0.1};
                animation: float ${Math.random() * 10 + 8}s ease-in-out infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            particlesContainer.appendChild(dot);
        }
        // Add float keyframe dynamically if not in CSS
        if (!document.querySelector('#float-keyframe')) {
            const style = document.createElement('style');
            style.id = 'float-keyframe';
            style.textContent = `
                @keyframes float {
                    0%, 100% { transform: translateY(0px) translateX(0px); }
                    33% { transform: translateY(-20px) translateX(10px); }
                    66% { transform: translateY(10px) translateX(-10px); }
                }
                .glitch {
                    animation: glitch 0.2s ease !important;
                }
                @keyframes glitch {
                    0% { transform: translate(0); }
                    20% { transform: translate(-2px, 1px); filter: hue-rotate(90deg); }
                    40% { transform: translate(2px, -1px); }
                    60% { transform: translate(-1px, 2px); filter: hue-rotate(-90deg); }
                    80% { transform: translate(1px, -2px); }
                    100% { transform: translate(0); filter: none; }
                }
            `;
            document.head.appendChild(style);
        }
    }
 }
    // ---- SMOOTH ACTIVE LINK on scroll (single page sections if any) ----
    // Marks current nav link based on URL
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.endsWith(href.split('/').pop())) {
            link.classList.add('active');
        }
    });

    console.log('%c[NEURALTECH] Systems online.', 'color: #00ADB5; font-family: monospace; font-size: 12px;');
});

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('mouseenter', () => {
        link.style.textShadow = '0 0 10px #00ADB5';
    });
    link.addEventListener('mouseleave', () => {
        link.style.textShadow = '';
    });
});


const navLinksAll = document.querySelectorAll('.nav-link');

navLinksAll.forEach(link => {
    link.addEventListener('mouseenter', () => {
        link.style.transform = 'translateY(-2px)';
    });
    link.addEventListener('mouseleave', () => {
        link.style.transform = '';
    });
});



// ________CONTRASEÑA Y REGISTRO DE USUARIOS__________________________________________
/**
 * NeuralTech — auth.js
 * SPA Tab system + Validación + Password strength + Toggle show/hide
 *
 * Cómo usarlo: <script src="{% static 'js/auth.js' %}" defer></script>
 * al final del base.html o dentro del bloque scripts de auth.html
 */

document.addEventListener('DOMContentLoaded', () => {

    /* ============================================================
       UTILIDADES
       ============================================================ */

    /**
     * Muestra un mensaje de alerta en un contenedor.
     * @param {HTMLElement} el - Elemento del alert
     * @param {string} msg - Mensaje a mostrar
     */
    function showAlert(el, msg) {
        if (!el) return;
        el.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            ${msg}
        `;
        el.style.display = 'flex';
    }

    /**
     * Oculta una alerta.
     * @param {HTMLElement} el
     */
    function hideAlert(el) {
        if (!el) return;
        el.style.display = 'none';
        el.innerHTML = '';
    }

    /**
     * Marca un input con error.
     * @param {HTMLElement} input
     * @param {string} msg
     * @param {HTMLElement|null} errorEl
     */
    function setError(input, msg, errorEl) {
        input.classList.add('nt-input--error');
        input.classList.remove('nt-input--success');
        if (errorEl) errorEl.textContent = msg;
    }

    /**
     * Marca un input como válido.
     * @param {HTMLElement} input
     * @param {HTMLElement|null} errorEl
     */
    function setSuccess(input, errorEl) {
        input.classList.remove('nt-input--error');
        input.classList.add('nt-input--success');
        if (errorEl) errorEl.textContent = '';
    }

    /**
     * Limpia estado de un input.
     * @param {HTMLElement} input
     * @param {HTMLElement|null} errorEl
     */
    function clearState(input, errorEl) {
        input.classList.remove('nt-input--error', 'nt-input--success');
        if (errorEl) errorEl.textContent = '';
    }

    /**
     * Animación de shake en la card.
     */
    function shakeCard() {
        const card = document.getElementById('authCard');
        if (!card) return;
        card.classList.add('nt-shake');
        card.addEventListener('animationend', () => card.classList.remove('nt-shake'), { once: true });
    }


    /* ============================================================
       PARTÍCULAS DEL AUTH HERO
       ============================================================ */
    const authParticles = document.getElementById('authParticles');
    if (authParticles) {
        for (let i = 0; i < 20; i++) {
            const dot = document.createElement('div');
            dot.style.cssText = `
                position: absolute;
                width: ${Math.random() * 2.5 + 1}px;
                height: ${Math.random() * 2.5 + 1}px;
                background: #00ADB5;
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                opacity: ${Math.random() * 0.4 + 0.05};
                animation: float ${Math.random() * 10 + 8}s ease-in-out infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            authParticles.appendChild(dot);
        }
    }


    /* ============================================================
       SISTEMA DE TABS (SPA)
       ============================================================ */

    const tabs = document.querySelectorAll('.auth-tab');
    const panels = document.querySelectorAll('.auth-panel');
    const tabIndicator = document.getElementById('tabIndicator');
    const heroTitleText = document.getElementById('heroTitleText');
    const heroSubtitle = document.getElementById('heroSubtitle');

    // Textos del hero para cada tab
    const heroContent = {
        login: {
            title: 'Iniciar <span class="accent">Sesión</span>',
            subtitle: 'Accedé a la plataforma NeuralTech y gestioná tus soluciones inteligentes desde un único lugar.'
        },
        register: {
            title: 'Crear <span class="accent">Cuenta</span>',
            subtitle: 'Registrate en NeuralTech y comenzá a transformar tu negocio con inteligencia artificial avanzada.'
        }
    };

    /**
     * Actualiza la posición del indicador de tab.
     * @param {HTMLElement} activeTab
     */
    function updateIndicator(activeTab) {
        if (!tabIndicator || !activeTab) return;
        tabIndicator.style.left   = activeTab.offsetLeft + 'px';
        tabIndicator.style.width  = activeTab.offsetWidth + 'px';
    }

    /**
     * Cambia la tab activa con animación.
     * @param {string} targetTab - 'login' | 'register'
     */
    function switchTab(targetTab) {
        const targetTabBtn = document.querySelector(`.auth-tab[data-tab="${targetTab}"]`);
        const targetPanel  = document.getElementById(`panel-${targetTab}`);
        const currentPanel = document.querySelector('.auth-panel.active');

        if (!targetPanel || (currentPanel && currentPanel.id === `panel-${targetTab}`)) return;

        // --- Tabs ---
        tabs.forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
        });
        targetTabBtn.classList.add('active');
        targetTabBtn.setAttribute('aria-selected', 'true');

        // --- Indicador ---
        updateIndicator(targetTabBtn);

        // --- Paneles: fade out → fade in ---
        if (currentPanel) {
            currentPanel.classList.add('exiting');
            currentPanel.classList.remove('active');
            setTimeout(() => {
                currentPanel.classList.remove('exiting');
            }, 200);
        }

        setTimeout(() => {
            targetPanel.classList.add('active');
        }, 150);

        // --- Hero text ---
        if (heroTitleText && heroContent[targetTab]) {
            heroTitleText.style.opacity = '0';
            setTimeout(() => {
                heroTitleText.innerHTML = heroContent[targetTab].title;
                heroTitleText.style.opacity = '1';
                heroTitleText.style.transition = 'opacity 0.4s ease';
            }, 200);
        }
        if (heroSubtitle && heroContent[targetTab]) {
            heroSubtitle.style.opacity = '0';
            setTimeout(() => {
                heroSubtitle.textContent = heroContent[targetTab].subtitle;
                heroSubtitle.style.opacity = '1';
                heroSubtitle.style.transition = 'opacity 0.4s ease';
            }, 250);
        }
    }

    // Click en tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Botones "switch" dentro de los paneles (ej: "¿No tenés cuenta? Registrarse →")
    document.querySelectorAll('.nt-tab-switch-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.switch));
    });

    // Inicializar indicador en la tab activa
    const activeTabOnLoad = document.querySelector('.auth-tab.active');
    if (activeTabOnLoad) updateIndicator(activeTabOnLoad);

    // Si Django redirige con ?tab=register (ej: error en registro)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('tab') === 'register') {
        switchTab('register');
    }

    // Si hay errores en el formulario de registro (Django los renderiza en el panel),
    // abrir automáticamente el panel de registro
    const registerPanel = document.getElementById('panel-register');
    if (registerPanel) {
        const djangoErrors = registerPanel.querySelectorAll('.errorlist, .nt-alert--error');
        if (djangoErrors.length > 0) {
            // Verificar que al menos uno tenga contenido
            const hasErrors = Array.from(djangoErrors).some(el => el.textContent.trim().length > 0);
            if (hasErrors) switchTab('register');
        }
    }

    // Recalcular indicador en resize
    window.addEventListener('resize', () => {
        const at = document.querySelector('.auth-tab.active');
        if (at) updateIndicator(at);
    });


    /* ============================================================
       TOGGLE MOSTRAR / OCULTAR CONTRASEÑA
       ============================================================ */
    document.querySelectorAll('.nt-toggle-pw').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const input = document.getElementById(targetId) || btn.closest('.nt-input-wrap')?.querySelector('input[type="password"], input[type="text"]');
            if (!input) return;

            const eyeOn  = btn.querySelector('.eye-icon');
            const eyeOff = btn.querySelector('.eye-off-icon');

            if (input.type === 'password') {
                input.type = 'text';
                if (eyeOn)  eyeOn.style.display  = 'none';
                if (eyeOff) eyeOff.style.display = '';
                btn.setAttribute('aria-label', 'Ocultar contraseña');
            } else {
                input.type = 'password';
                if (eyeOn)  eyeOn.style.display  = '';
                if (eyeOff) eyeOff.style.display = 'none';
                btn.setAttribute('aria-label', 'Mostrar contraseña');
            }
        });
    });


    /* ============================================================
       BARRA DE FORTALEZA DE CONTRASEÑA
       ============================================================ */
    const pw1 = document.getElementById('id_password1');
    const strengthBarWrap = document.getElementById('strengthBarWrap');
    const strengthFill    = document.getElementById('strengthFill');
    const strengthLabel   = document.getElementById('strengthLabel');

    const strengthLevels = [
        { label: 'Muy débil',  level: 1 },
        { label: 'Débil',      level: 1 },
        { label: 'Regular',    level: 2 },
        { label: 'Buena',      level: 3 },
        { label: 'Excelente',  level: 4 },
    ];

    function calcStrength(val) {
        if (!val) return 0;
        let score = 0;
        if (val.length >= 8)              score++;
        if (/[A-Z]/.test(val))            score++;
        if (/[0-9]/.test(val))            score++;
        if (/[^A-Za-z0-9]/.test(val))     score++;
        return score;
    }

    if (pw1) {
        pw1.addEventListener('input', () => {
            const val = pw1.value;

            if (!val) {
                if (strengthBarWrap) strengthBarWrap.style.display = 'none';
                return;
            }

            if (strengthBarWrap) strengthBarWrap.style.display = 'flex';
            const score = calcStrength(val);
            const lvl   = strengthLevels[score];

            if (strengthBarWrap) strengthBarWrap.dataset.level = lvl.level;
            if (strengthLabel)   strengthLabel.textContent     = lvl.label;
        });
    }


    /* ============================================================
       VALIDACIÓN FORMULARIO LOGIN
       ============================================================ */
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        const loginUsername = document.getElementById('login_username');
        const loginPassword = document.getElementById('login_password');
        const loginAlert    = document.getElementById('loginAlert');

        // Limpiar al escribir
        [loginUsername, loginPassword].forEach(input => {
            if (!input) return;
            input.addEventListener('input', () => {
                clearState(input, document.getElementById(`err-${input.id}`));
                hideAlert(loginAlert);
            });
        });

        loginForm.addEventListener('submit', function(e) {
            let valid = true;

            // Usuario
            if (loginUsername) {
                const errEl = document.getElementById('err-login_username');
                if (!loginUsername.value.trim()) {
                    setError(loginUsername, 'Ingresá tu usuario o email.', errEl);
                    valid = false;
                } else {
                    setSuccess(loginUsername, errEl);
                }
            }

            // Contraseña
            if (loginPassword) {
                const errEl = document.getElementById('err-login_password');
                if (!loginPassword.value) {
                    setError(loginPassword, 'Ingresá tu contraseña.', errEl);
                    valid = false;
                } else {
                    setSuccess(loginPassword, errEl);
                }
            }

            if (!valid) {
                e.preventDefault();
                shakeCard();
                showAlert(loginAlert, 'Completá todos los campos requeridos.');
                // Scroll al error
                const firstError = loginForm.querySelector('.nt-input--error');
                if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }

            // Animación de carga
            const btn      = document.getElementById('loginSubmitBtn');
            const btnText  = btn?.querySelector('.btn-text');
            const btnLoad  = btn?.querySelector('.btn-loading');
            if (btn && btnText && btnLoad) {
                btnText.style.display = 'none';
                btnLoad.style.display = 'flex';
                btn.disabled = true;
            }
        });
    }


    /* ============================================================
       VALIDACIÓN FORMULARIO REGISTRO
       ============================================================ */
    const registerForm = document.getElementById('registerForm');

    if (registerForm) {
        const pw2         = document.getElementById('id_password2');
        const termsCheck  = document.getElementById('termsCheck');
        const regAlert    = document.getElementById('registerAlert');

        // Validación en tiempo real: confirmar contraseña
        if (pw1 && pw2) {
            pw2.addEventListener('input', () => {
                const errEl = document.getElementById('err-password2');
                if (!pw2.value) {
                    clearState(pw2, errEl);
                    return;
                }
                if (pw1.value === pw2.value) {
                    setSuccess(pw2, errEl);
                } else {
                    setError(pw2, 'Las contraseñas no coinciden.', errEl);
                }
            });
        }

        // Limpiar errores al escribir en cualquier input del registro
        registerForm.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', () => {
                input.classList.remove('nt-input--error');
                hideAlert(regAlert);
            });
        });

        registerForm.addEventListener('submit', function(e) {
            let valid = true;
            hideAlert(regAlert);

            // Función helper de validación de campo
            function validateInput(inputId, errorId, validator) {
                const input  = document.getElementById(inputId);
                const errEl  = document.getElementById(errorId);
                if (!input) return;
                const msg = validator(input.value);
                if (msg) {
                    setError(input, msg, errEl);
                    valid = false;
                } else {
                    setSuccess(input, errEl);
                }
            }

            validateInput('id_first_name',  'err-first_name',   v => !v.trim() ? 'Ingresá tu nombre.'    : '');
            validateInput('id_last_name',   'err-last_name',    v => !v.trim() ? 'Ingresá tu apellido.'  : '');
            validateInput('id_email',       'err-email',        v => {
                if (!v.trim())                              return 'Ingresá tu email.';
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return 'Ingresá un email válido.';
                return '';
            });
            validateInput('id_username',    'err-reg-username', v => !v.trim() ? 'Ingresá un nombre de usuario.' : '');
            validateInput('id_password1',   'err-password1',    v => {
                if (!v)         return 'Ingresá una contraseña.';
                if (v.length < 8) return 'La contraseña debe tener al menos 8 caracteres.';
                return '';
            });
            validateInput('id_password2',   'err-password2',    v => {
                const p1 = document.getElementById('id_password1');
                if (!v)                     return 'Confirmá tu contraseña.';
                if (p1 && v !== p1.value)   return 'Las contraseñas no coinciden.';
                return '';
            });

            // Términos
            if (termsCheck && !termsCheck.checked) {
                const errEl = document.getElementById('err-terms');
                if (errEl) errEl.textContent = 'Debés aceptar los términos y condiciones.';
                valid = false;
            } else if (termsCheck) {
                const errEl = document.getElementById('err-terms');
                if (errEl) errEl.textContent = '';
            }

            if (!valid) {
                e.preventDefault();
                shakeCard();
                showAlert(regAlert, 'Revisá los campos marcados en rojo.');
                const firstError = registerForm.querySelector('.nt-input--error');
                if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }

            // Animación carga
            const btn     = document.getElementById('registerSubmitBtn');
            const btnText = btn?.querySelector('.btn-text');
            const btnLoad = btn?.querySelector('.btn-loading');
            if (btn && btnText && btnLoad) {
                btnText.style.display = 'none';
                btnLoad.style.display = 'flex';
                btn.disabled = true;
            }
        });
    }


    /* ============================================================
       POST-REGISTRO: si Django redirigió con ?registered=true,
       mostrar tab de login con mensaje de éxito
       ============================================================ */
    if (urlParams.get('registered') === 'true') {
        switchTab('login');
        const loginSuccess = document.getElementById('loginSuccess');
        if (loginSuccess) {
            loginSuccess.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
                ¡Cuenta creada con éxito! Podés iniciar sesión ahora.
            `;
            loginSuccess.style.display = 'flex';
        }
    }


    /* ============================================================
       APLICAR CLASES nt-input A WIDGETS DE DJANGO
       (por si Django genera inputs sin la clase)
       ============================================================ */
    document.querySelectorAll('.nt-input-wrap input').forEach(input => {
        if (!input.classList.contains('nt-input')) {
            input.classList.add('nt-input');
        }
    });

    console.log('%c[NEURALTECH] Auth module online.', 'color: #00ADB5; font-family: monospace; font-size: 12px;');

}); // END DOMContentLoaded

/**
 * NeuralTech — contacto_ajax.js
 * Integración dinámica con JavaScript / Fetch API (Unidad 3 - Punto 2)
 *
 * Ruta sugerida: mi_sitio / mi_app / static / mi_app / contacto_ajax.js
 *
 * Qué hace este script:
 *  1. Captura el submit del formulario #contactForm sin recargar la página.
 *  2. Valida los campos en el cliente antes de enviar.
 *  3. Envía los datos al servidor con Fetch API (POST asíncrono).
 *  4. Muestra el resultado (éxito o error) de forma dinámica en el DOM.
 *  5. Anima el botón de envío con un spinner mientras espera la respuesta.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Captura de elementos ────────────────────────────────────────────────
    const form      = document.getElementById('contactForm');
    const submitBtn = document.getElementById('submitBtn');

    // Si el formulario no existe en esta página, no hacemos nada
    if (!form) return;

    // Token CSRF (requerido por Django para peticiones POST)
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // ── Utilidades de UI ────────────────────────────────────────────────────

    /**
     * Muestra el spinner en el botón de envío y lo deshabilita.
     */
    function setBtnLoading() {
        const btnText    = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        const btnArrow   = submitBtn.querySelector('.btn-arrow');

        if (btnText)    btnText.style.display    = 'none';
        if (btnLoading) btnLoading.style.display = 'inline-flex';
        if (btnArrow)   btnArrow.style.display   = 'none';
        submitBtn.disabled = true;
    }

    /**
     * Restaura el botón de envío a su estado normal.
     */
    function setBtnReady() {
        const btnText    = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        const btnArrow   = submitBtn.querySelector('.btn-arrow');

        if (btnText)    btnText.style.display    = '';
        if (btnLoading) btnLoading.style.display = 'none';
        if (btnArrow)   btnArrow.style.display   = '';
        submitBtn.disabled = false;
    }

    /**
     * Elimina cualquier mensaje de resultado previo del DOM.
     */
    function clearResultMessage() {
        const prev = form.querySelector('.ajax-result-msg');
        if (prev) prev.remove();
    }

    /**
     * Inserta un mensaje de ÉXITO encima del formulario.
     * @param {string} nombre - Nombre del remitente para personalizar el mensaje.
     */
    function showSuccessMessage(nombre) {
        clearResultMessage();

        // Limpiamos y ocultamos el formulario para dar protagonismo al mensaje
        const formBody = form.querySelector('.contact-form') || form;

        const wrapper = document.createElement('div');
        wrapper.className = 'ajax-result-msg success-message';
        wrapper.innerHTML = `
            <div class="success-icon">
                <svg width="28" height="28" viewBox="0 0 24 24"
                     fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M20 6L9 17l-5-5"/>
                </svg>
            </div>
            <div class="success-content">
                <h4>¡Mensaje enviado con éxito!</h4>
                <p>Gracias <strong>${nombre}</strong>, recibimos tu consulta y nos comunicaremos a la brevedad.</p>
            </div>
        `;

        // Insertamos antes del formulario visible
        form.insertBefore(wrapper, form.firstChild);

        // Hacemos scroll suave al mensaje
        wrapper.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Reseteamos el formulario completo
        form.reset();

        // Limpiamos errores de validación previos
        form.querySelectorAll('.form-input').forEach(function (input) {
            input.style.borderColor = '';
            input.classList.remove('error');
        });
        form.querySelectorAll('.form-error').forEach(function (el) {
            el.textContent = '';
        });
    }

    /**
     * Inserta un mensaje de ERROR dentro del formulario.
     * @param {string} mensaje - Texto del error a mostrar.
     * @param {Object} [errores] - Objeto con errores por campo devuelto por Django.
     */
    function showErrorMessage(mensaje, errores) {
        clearResultMessage();

        const wrapper = document.createElement('div');
        wrapper.className = 'ajax-result-msg alert alert-error ajax-error-banner';

        let html = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2" style="flex-shrink:0; margin-right:8px;">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span>${mensaje}</span>
        `;

        wrapper.style.cssText = 'display:flex; align-items:center; margin-bottom:1rem;';
        wrapper.innerHTML = html;

        // Mostramos errores individuales por campo si los hay
        if (errores && typeof errores === 'object') {
            Object.keys(errores).forEach(function (campo) {
                const inputEl = form.querySelector('[name="' + campo + '"]');
                const errorEl = document.getElementById('error-' + campo);
                if (inputEl) {
                    inputEl.style.borderColor = '#ff4d4d';
                    inputEl.classList.add('error');
                }
                if (errorEl) {
                    errorEl.textContent = errores[campo].join
                        ? errores[campo].join(', ')
                        : errores[campo];
                }
            });

            // Scroll al primer campo con error
            const firstError = form.querySelector('.error');
            if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        form.insertBefore(wrapper, form.firstChild);
    }

    // ── Validación en el cliente ─────────────────────────────────────────────

    /**
     * Valida un campo individual y actualiza su estado visual.
     * @param {HTMLElement} field - Input o textarea a validar.
     * @returns {boolean} true si el campo es válido.
     */
    function validateField(field) {
        const errorEl = document.getElementById('error-' + field.id);
        let error = '';

        if (field.required && !field.value.trim()) {
            error = 'Este campo es obligatorio.';
        } else if (field.type === 'email' && field.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value.trim())) {
                error = 'Ingresá un email válido.';
            }
        } else if (field.tagName === 'TEXTAREA' && field.required && field.value.trim().length < 5) {
            error = 'El mensaje debe tener al menos 5 caracteres.';
        }

        if (errorEl) errorEl.textContent = error;

        if (error) {
            field.style.borderColor = '#ff4d4d';
            field.classList.add('error');
        } else {
            field.style.borderColor = '';
            field.classList.remove('error');
        }

        return !error;
    }

    /**
     * Valida el checkbox de política de privacidad.
     * @returns {boolean}
     */
    function validateCheckbox() {
        const checkbox = document.getElementById('acepta');
        const errorEl  = document.getElementById('error-acepta');
        if (checkbox && !checkbox.checked) {
            if (errorEl) errorEl.textContent = 'Debés aceptar la política de privacidad.';
            return false;
        }
        if (errorEl) errorEl.textContent = '';
        return true;
    }

    // Validación en tiempo real al salir de cada campo
    form.querySelectorAll('.form-input').forEach(function (input) {
        input.addEventListener('blur', function () { validateField(input); });
        input.addEventListener('input', function () {
            if (input.classList.contains('error')) validateField(input);
        });
    });

    // ── Interceptación del submit ────────────────────────────────────────────
    form.addEventListener('submit', function (e) {

        // Siempre prevenimos el comportamiento nativo
        e.preventDefault();
        clearResultMessage();

        // 1. Validación del lado del cliente
        let formValid = true;

        form.querySelectorAll('.form-input').forEach(function (input) {
            if (!validateField(input)) formValid = false;
        });

        if (!validateCheckbox()) formValid = false;

        if (!formValid) {
            const firstError = form.querySelector('.error');
            if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        // 2. Animación del botón
        setBtnLoading();

        // 3. Captura de datos del formulario
        const formData = new FormData(form);

        // 4. Petición asíncrona con Fetch API
        fetch(form.action || window.location.pathname, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'   // Django puede detectar AJAX con esto
            },
            body: formData
        })
        .then(function (response) {
            // Intentamos parsear JSON; si falla, el servidor devolvió HTML (fallback)
            const contentType = response.headers.get('Content-Type') || '';
            if (contentType.includes('application/json')) {
                return response.json();
            }
            // Si Django devuelve HTML (respuesta normal sin JsonResponse)
            // lo tratamos como éxito si el status es 200
            return { success: response.ok, html_response: true };
        })
        .then(function (data) {
            setBtnReady();

            if (data.success) {
                // Éxito: obtenemos el nombre del campo para personalizar el saludo
                const nombreInput = form.querySelector('[name="nombre"]');
                const nombre = nombreInput ? nombreInput.value.trim() : 'visitante';
                showSuccessMessage(data.nombre || nombre);

            } else if (data.html_response) {
                // La vista devolvió HTML normal (no JsonResponse) → recargamos
                // para que Django muestre mensaje_exito en el template
                window.location.reload();

            } else {
                // Error con detalle del servidor
                const msg = data.message || 'Hubo un problema al enviar el formulario. Revisá los campos.';
                showErrorMessage(msg, data.errors || null);
            }
        })
        .catch(function (error) {
            setBtnReady();
            console.error('[NeuralTech] Error en la solicitud de contacto:', error);
            showErrorMessage('No se pudo conectar con el servidor. Verificá tu conexión e intentá nuevamente.');
        });
    });

    // ── Limpiar errores al reescribir ────────────────────────────────────────
    const checkboxPrivacy = document.getElementById('acepta');
    if (checkboxPrivacy) {
        checkboxPrivacy.addEventListener('change', function () {
            const errorEl = document.getElementById('error-acepta');
            if (errorEl) errorEl.textContent = '';
        });
    }

    console.log('%c[NEURALTECH] Módulo contacto_ajax.js cargado.', 'color: #00ADB5; font-family: monospace; font-size: 11px;');

}); // END DOMContentLoaded