
document.addEventListener('DOMContentLoaded', () => {

    // ---- CURSOR GLOW ----
    const cursorGlow = document.getElementById('cursorGlow');
    if (cursorGlow) {
        document.addEventListener('mousemove', (e) => {
            cursorGlow.style.left = e.clientX + 'px';
            cursorGlow.style.top = e.clientY + 'px';
        });
    }

    // ---- NAVBAR: scroll effect ----
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

    // Observe all [data-aos] elements + specific card types
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

        // Real-time validation
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
                    error = 'Ingresá un email válido.';
                }
            } else if (field.tagName === 'SELECT' && field.required && !field.value) {
                error = 'Seleccioná una opción.';
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

        // Checkbox validation
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

        contactForm.addEventListener('submit', (e) => {
            let valid = true;

            contactForm.querySelectorAll('.form-input').forEach(input => {
                if (!validateField(input)) valid = false;
            });
            if (!validateCheckbox()) valid = false;

            if (!valid) {
                e.preventDefault();
                // Scroll to first error
                const firstError = contactForm.querySelector('.error');
                if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                // Animate submit button
                const btn = document.getElementById('submitBtn');
                const btnText = btn.querySelector('.btn-text');
                const btnLoading = btn.querySelector('.btn-loading');
                if (btnText && btnLoading) {
                    btnText.style.display = 'none';
                    btnLoading.style.display = 'inline';
                    btn.disabled = true;
                }
            }
        });
    contactForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // evita recargar

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

    // botón cargando
    const btn = document.getElementById('submitBtn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');

    btnText.style.display='none';
    btnLoading.style.display='inline';
    btn.disabled=true;

    try {

        const formData = new FormData(contactForm);

        const response = await fetch(contactForm.action,{
            method:'POST',
            body:formData,
            headers:{
                'X-Requested-With':'XMLHttpRequest'
            }
        });

        const data=await response.json();

        const contenedor=document.querySelector('.form-messages');

        if(data.success){

            contenedor.innerHTML=`
            <div class="success-message">
                <div class="success-icon">
                    ✓
                </div>

                <div class="success-content">
                    <h4>Mensaje enviado</h4>
                    <p>${data.message}</p>
                </div>
            </div>
            `;

            contactForm.reset();

        }else{

            contenedor.innerHTML=`
            <div class="alert alert-danger">
                ${data.message}
            </div>
            `;
        }

    } catch(error){

        console.log(error);

        document.querySelector('.form-messages').innerHTML=`
        <div class="alert alert-danger">
            Error al enviar el formulario
        </div>
        `;
    }

    btnText.style.display='inline';
    btnLoading.style.display='none';
    btn.disabled=false;
});

    }

    // ---- GLITCH EFFECT on hero title (subtle) ----
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
            }, Math.random() * 8000 + 4000);
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

    // ---- TYPING EFFECT on hero subtitle (optional, subtle) ----
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

    // ---- PARTICLES on hero (simple dots) ----
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