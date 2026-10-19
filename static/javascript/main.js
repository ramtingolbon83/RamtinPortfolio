/* ============================================
   AuraCV - Main JavaScript
   Version: 1.0.0
   ============================================
   State classes toggled by this file (keep names in sync with tailwind.config.js):
   - active  → [data-nav], .testimonial-slide, .testimonial-dot, .portfolio-filter
   - open    → #sidebarOverlay, #sidebarMobile
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {


  // ---- Navigation (Desktop + Mobile): one section visible at a time ----
  const mainContent = document.getElementById('mainContent');
  const sections = Array.from(document.querySelectorAll('[data-section]'));
  const navBtns = document.querySelectorAll('[data-nav]');

  function showSection(id, updateHash) {
    if (!sections.some(sec => sec.dataset.section === id)) id = 'home';
    sections.forEach(sec => {
      sec.style.display = sec.dataset.section === id ? '' : 'none';
    });
    navBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.nav === id);
    });
    if (mainContent) mainContent.scrollTo({ top: 0 });
    if (updateHash) history.replaceState(null, '', '#' + id);
  }

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => showSection(btn.dataset.nav, true));
  });

  // initial section: toast message -> contact, otherwise URL hash, otherwise home
  const hashId = decodeURIComponent(location.hash.replace('#', ''));
  showSection(document.querySelector('.toast') ? 'contact' : (hashId || 'home'), false);

  // ---- Scroll to move between sections (wheel + touch swipe) ----
  // At the end of a section, scrolling further goes to the next section;
  // at the start, scrolling back goes to the previous one.
  function currentIndex() {
    return sections.findIndex(sec => sec.style.display !== 'none');
  }
  function atTop() {
    return mainContent.scrollTop <= 1;
  }
  function atBottom() {
    return mainContent.scrollTop + mainContent.clientHeight >= mainContent.scrollHeight - 2;
  }
  function goRelative(step) {
    const target = sections[currentIndex() + step];
    if (!target) return false;
    showSection(target.dataset.section, true);
    if (step < 0) mainContent.scrollTo({ top: mainContent.scrollHeight });
    return true;
  }

  if (mainContent) {
    // wheel: one section change per gesture, and only if the gesture STARTED at the edge
    // (so a long scroll that reaches the end does not roll straight into the next section)
    let gestureActive = false;
    let gestureUsed = false;
    let edgeAtStart = { top: false, bottom: false };
    let wheelIdle;
    mainContent.addEventListener('wheel', e => {
      if (!gestureActive) {
        gestureActive = true;
        edgeAtStart = { top: atTop(), bottom: atBottom() };
      }
      clearTimeout(wheelIdle);
      wheelIdle = setTimeout(() => { gestureActive = false; gestureUsed = false; }, 250);
      if (gestureUsed || Math.abs(e.deltaY) < 20) return;
      if (e.deltaY > 0 && edgeAtStart.bottom && atBottom()) gestureUsed = goRelative(1);
      else if (e.deltaY < 0 && edgeAtStart.top && atTop()) gestureUsed = goRelative(-1);
    }, { passive: true });

    // touch: a swipe that starts at the edge of the section
    let touchY = null;
    let startAtTop = false;
    let startAtBottom = false;
    mainContent.addEventListener('touchstart', e => {
      touchY = e.touches[0].clientY;
      startAtTop = atTop();
      startAtBottom = atBottom();
    }, { passive: true });
    mainContent.addEventListener('touchend', e => {
      if (touchY === null) return;
      const dy = touchY - e.changedTouches[0].clientY;
      touchY = null;
      if (dy > 60 && startAtBottom) goRelative(1);
      else if (dy < -60 && startAtTop) goRelative(-1);
    }, { passive: true });
  }

  // ---- Mobile Sidebar ----
  const menuBtn = document.getElementById('menuBtn');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  const sidebarMobile = document.getElementById('sidebarMobile');
  const closeSidebar = document.getElementById('closeSidebar');

  function openSidebar() {
    sidebarOverlay.classList.add('open');
    sidebarMobile.classList.add('open');
  }
  function closeSidebarFn() {
    sidebarOverlay.classList.remove('open');
    sidebarMobile.classList.remove('open');
  }

  if (menuBtn) menuBtn.addEventListener('click', openSidebar);
  if (closeSidebar) closeSidebar.addEventListener('click', closeSidebarFn);
  if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebarFn);

  // ---- Testimonials Carousel ----
  const slides = document.querySelectorAll('.testimonial-slide');
  const dots = document.querySelectorAll('.testimonial-dot');
  const prevBtn = document.getElementById('testimonialPrev');
  const nextBtn = document.getElementById('testimonialNext');
  let currentSlide = 0;

  function showSlide(i) {
    if (!slides.length) return;
    slides.forEach(s => s.classList.remove('active'));
    dots.forEach(d => d.classList.remove('active'));
    currentSlide = (i + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
    if (dots[currentSlide]) dots[currentSlide].classList.add('active');
  }

  if (prevBtn) prevBtn.addEventListener('click', () => showSlide(currentSlide - 1));
  if (nextBtn) nextBtn.addEventListener('click', () => showSlide(currentSlide + 1));
  dots.forEach((dot, i) => dot.addEventListener('click', () => showSlide(i)));

  // ---- Portfolio Filters ----
  const filterBtns = document.querySelectorAll('.portfolio-filter');
  const portfolioCards = document.querySelectorAll('.portfolio-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      portfolioCards.forEach(card => {
        card.style.display = (filter === 'all' || card.dataset.category === filter) ? '' : 'none';
      });
    });
  });

  // ---- Blog Filters ----
  const blogFilterBtns = document.querySelectorAll('.blog-filter');
  const blogCards = document.querySelectorAll('.blog-card');

  blogFilterBtns.forEach(btn => {
    btn.addEventListener('click', () => {

      blogFilterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;

      blogCards.forEach(card => {
        card.style.display =
          filter === 'all' || card.dataset.category === filter
            ? ''
            : 'none';
      });
    });
  });


  // ---- Portfolio: image slider (on hover) + lightbox (click to enlarge) ----
  const SLIDE_INTERVAL = 2000; // milliseconds between images while the mouse is over a card
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Lightbox is appended to <body> (not inside the glass panels) so position:fixed covers the whole screen
  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.setAttribute('role', 'dialog');
  lightbox.setAttribute('aria-modal', 'true');
  lightbox.setAttribute('aria-label', 'نمایش بزرگ تصویر');
  lightbox.innerHTML =
    '<button type="button" class="lightbox__close" aria-label="بستن">&times;</button>' +
    '<button type="button" class="lightbox__nav lightbox__nav--prev" aria-label="تصویر قبلی">&#8250;</button>' +
    '<div class="lightbox__stage"><img class="lightbox__img" alt="" /></div>' +
    '<button type="button" class="lightbox__nav lightbox__nav--next" aria-label="تصویر بعدی">&#8249;</button>' +
    '<div class="lightbox__bar"><span class="lightbox__title"></span>' +
    '<div class="lightbox__dots"></div><span class="lightbox__count"></span></div>';
  document.body.appendChild(lightbox);

  const lbImg = lightbox.querySelector('.lightbox__img');
  const lbStage = lightbox.querySelector('.lightbox__stage');
  const lbTitle = lightbox.querySelector('.lightbox__title');
  const lbDots = lightbox.querySelector('.lightbox__dots');
  const lbCount = lightbox.querySelector('.lightbox__count');
  const lbPrev = lightbox.querySelector('.lightbox__nav--prev');
  const lbNext = lightbox.querySelector('.lightbox__nav--next');
  const lbClose = lightbox.querySelector('.lightbox__close');
  let lbItems = [];
  let lbIndex = 0;
  let lbOpener = null;

  function lbShow(i) {
    lbIndex = (i + lbItems.length) % lbItems.length;
    lightbox.classList.remove('zoomed');
    lbStage.scrollTo(0, 0);
    lbImg.src = lbItems[lbIndex].src;
    lbImg.alt = lbItems[lbIndex].alt;
    lbCount.textContent = (lbIndex + 1).toLocaleString('fa-IR') + ' / ' + lbItems.length.toLocaleString('fa-IR');
    lbDots.querySelectorAll('button').forEach((d, n) => d.classList.toggle('active', n === lbIndex));
    // preload neighbours so next/prev feel instant
    [lbIndex + 1, lbIndex - 1].forEach(n => {
      const item = lbItems[(n + lbItems.length) % lbItems.length];
      if (item) new Image().src = item.src;
    });
  }

  function lbOpen(items, index, title, opener) {
    lbItems = items;
    lbOpener = opener || null;
    lbTitle.textContent = title || '';
    const multiple = items.length > 1;
    lbPrev.hidden = lbNext.hidden = !multiple;
    lbDots.hidden = lbCount.hidden = !multiple;
    lbDots.innerHTML = '';
    if (multiple) {
      items.forEach((_, n) => {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'portfolio-dot';
        dot.setAttribute('aria-label', 'تصویر ' + (n + 1).toLocaleString('fa-IR'));
        dot.addEventListener('click', () => lbShow(n));
        lbDots.appendChild(dot);
      });
    }
    lbShow(index);
    lightbox.classList.add('open');
    lbClose.focus();
  }

  function lbHide() {
    lightbox.classList.remove('open', 'zoomed');
    lbImg.removeAttribute('src');
    if (lbOpener) lbOpener.focus({ preventScroll: true });
  }

  lbClose.addEventListener('click', lbHide);
  lbPrev.addEventListener('click', () => lbShow(lbIndex - 1));
  lbNext.addEventListener('click', () => lbShow(lbIndex + 1));
  // click the dark area (not the image / buttons) to close
  lightbox.addEventListener('click', e => {
    if (e.target === lightbox || e.target === lbStage) lbHide();
  });
  // click the image: toggle between "fit to screen" and "actual size"
  lbImg.addEventListener('click', () => lightbox.classList.toggle('zoomed'));

  // keyboard (page is RTL: right arrow = previous, left arrow = next)
  document.addEventListener('keydown', e => {
    if (!lightbox.classList.contains('open')) return;
    if (e.key === 'Escape') lbHide();
    else if (e.key === 'ArrowLeft') lbShow(lbIndex + 1);
    else if (e.key === 'ArrowRight') lbShow(lbIndex - 1);
  });

  // swipe on touch screens
  let lbTouchX = null;
  lbStage.addEventListener('touchstart', e => { lbTouchX = e.touches[0].clientX; }, { passive: true });
  lbStage.addEventListener('touchend', e => {
    if (lbTouchX === null || lightbox.classList.contains('zoomed')) { lbTouchX = null; return; }
    const dx = e.changedTouches[0].clientX - lbTouchX;
    lbTouchX = null;
    if (dx < -50) lbShow(lbIndex + 1);
    else if (dx > 50) lbShow(lbIndex - 1);
  }, { passive: true });

  document.querySelectorAll('.portfolio-card').forEach(card => {
    const wrap = card.querySelector('.portfolio-card__img-wrap');
    const slideEls = Array.from(card.querySelectorAll('.portfolio-slide'));
    const dotEls = card.querySelectorAll('.portfolio-dot');
    if (!wrap || !slideEls.length) return;

    let index = 0;
    let timer = null;

    function show(i) {
      index = (i + slideEls.length) % slideEls.length;
      slideEls.forEach((img, n) => img.classList.toggle('active', n === index));
      dotEls.forEach((dot, n) => dot.classList.toggle('active', n === index));
    }
    function stop() {
      clearInterval(timer);
      timer = null;
    }
    function start() {
      stop();
      if (reduceMotion || slideEls.length < 2) return;
      timer = setInterval(() => show(index + 1), SLIDE_INTERVAL);
    }

    // the images change only while a MOUSE is over the card; at rest the cover is shown
    card.addEventListener('pointerenter', e => { if (e.pointerType === 'mouse') start(); });
    card.addEventListener('pointerleave', () => { stop(); show(0); });

    dotEls.forEach((dot, n) => {
      dot.addEventListener('click', e => {
        e.stopPropagation();
        show(n);
        if (card.matches(':hover')) start(); // restart the timer after a manual choice
      });
    });

    // click on the image area (not the project link, not the dots) -> enlarge
    wrap.setAttribute('tabindex', '0');
    wrap.setAttribute('role', 'button');
    wrap.setAttribute('aria-label', 'بزرگ‌نمایی تصاویر');
    function openLightbox() {
      const items = slideEls.map(img => ({ src: img.currentSrc || img.src, alt: img.alt }));
      lbOpen(items, index, slideEls[0].alt, wrap);
    }
    wrap.addEventListener('click', e => {
      if (e.target.closest('a, .portfolio-dot')) return;
      openLightbox();
    });
    wrap.addEventListener('keydown', e => {
      if (e.target === wrap && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        openLightbox();
      }
    });
  });

  // ---- Skill Bar Animation (Intersection Observer) ----
  const skillBars = document.querySelectorAll('.skill__fill');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.width = entry.target.dataset.level + '%';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  skillBars.forEach(bar => observer.observe(bar));
});