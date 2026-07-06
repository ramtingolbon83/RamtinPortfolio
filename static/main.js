/* ============================================
   AuraCV - Main JavaScript
   Version: 1.0.0
   ============================================
   State classes toggled by this file (keep names in sync with tailwind.config.js):
   - active  → [data-nav], .testimonial-slide, .testimonial-dot, .portfolio-filter
   - open    → #sidebarOverlay, #sidebarMobile
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  
  // ---- Navigation (Desktop + Mobile) ----
  const mainContent = document.getElementById('mainContent');
  const sections = document.querySelectorAll('[data-section]');
  const navBtns = document.querySelectorAll('[data-nav]');

  function setActive(id) {
    navBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.nav === id);
    });
  }

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = document.querySelector(`[data-section="${btn.dataset.nav}"]`);
      if (target && mainContent) {
        mainContent.scrollTo({ top: target.offsetTop, behavior: 'smooth' });
      }
    });
  });

  if (mainContent) {
    mainContent.addEventListener('scroll', () => {
      const scrollTop = mainContent.scrollTop + 100;
      let current = 'home';
      sections.forEach(sec => {
        if (sec.offsetTop <= scrollTop) current = sec.dataset.section;
      });
      setActive(current);
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
    slides.forEach(s => s.classList.remove('active'));
    dots.forEach(d => d.classList.remove('active'));
    currentSlide = (i + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
    dots[currentSlide].classList.add('active');
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
