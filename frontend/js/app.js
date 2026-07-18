/**
 * 🏥 App.js — Shared Utilities
 * Bệnh viện Tim Hà Nội
 * 
 * - Header scroll effect
 * - Mobile menu toggle
 * - Smooth scroll
 * - API config
 */

(function () {
  'use strict';

  // ========================
  // Global Config
  // ========================
  // Same-origin API. The browser never needs to know an internal AI service URL.
  window.AI_API_URL = '';

  // ========================
  // Header Scroll Effect
  // ========================
  const header = document.querySelector('.header');
  if (header) {
    window.addEventListener('scroll', () => {
      header.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }

  // ========================
  // Mobile Menu Toggle
  // ========================
  const menuBtn = document.querySelector('.mobile-menu-btn');
  const nav = document.querySelector('.nav');

  if (menuBtn && nav) {
    menuBtn.addEventListener('click', () => {
      nav.classList.toggle('mobile-open');
      menuBtn.textContent = nav.classList.contains('mobile-open') ? '✕' : '☰';
    });

    // Close menu on link click
    nav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        nav.classList.remove('mobile-open');
        menuBtn.textContent = '☰';
      });
    });
  }

  // ========================
  // Smooth Scroll for Anchor Links
  // ========================
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;

      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // ========================
  // Set Active Nav Link
  // ========================
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  // ========================
  // Intersection Observer — Animate on scroll
  // ========================
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Animate cards and sections
  document.querySelectorAll('.card, .section-title, .info-item').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });

})();
