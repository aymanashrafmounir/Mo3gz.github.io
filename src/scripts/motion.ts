const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const ease = 'cubic-bezier(0.22, 1, 0.36, 1)';
const active = new Map<Element, Set<Animation>>();
const seen = new WeakSet<Element>();
const targets = [
  ...document.querySelectorAll<HTMLElement>(
    '.section-title, .selected-work > h2, .project-card, .career-role, .education, .skill-group, .certifications > li, .engineering-focus > div, .closing-contact, .site-footer, .project-case__section, .project-case__more, .contact-email, .contact-profiles, .about-introduction, .about-portrait',
  ),
];
let observer: IntersectionObserver | undefined;

function play(
  element: Element,
  keyframes: Keyframe[],
  options: KeyframeAnimationOptions,
) {
  if (reducedMotion.matches || typeof element.animate !== 'function') return;
  const animation = element.animate(keyframes, {
    easing: ease,
    ...options,
  });
  const animations = active.get(element) ?? new Set<Animation>();
  animations.add(animation);
  active.set(element, animations);
  const forget = () => {
    animations.delete(animation);
    if (!animations.size && active.get(element) === animations)
      active.delete(element);
  };
  void animation.finished.then(forget, forget);
}

function cancelAnimationsFor(target: Element) {
  for (const [element, animations] of active) {
    if (!element.contains(target) && !target.contains(element)) continue;
    for (const animation of animations) animation.cancel();
    active.delete(element);
  }
}

function cancelFor(target: Element) {
  cancelAnimationsFor(target);
  for (const element of targets) {
    if (!element.contains(target) && !target.contains(element)) continue;
    seen.add(element);
    observer?.unobserve(element);
  }
}

function cancelAll() {
  for (const animations of active.values())
    for (const animation of animations) animation.cancel();
  active.clear();
}

function isInViewport(element: Element) {
  const bounds = element.getBoundingClientRect();
  return bounds.top < window.innerHeight && bounds.bottom > 0;
}

function reveal(element: HTMLElement, index: number, duration = 480) {
  seen.add(element);
  observer?.unobserve(element);
  if (element.contains(document.activeElement)) return;
  play(
    element,
    [
      { opacity: 0, transform: 'translateY(18px)' },
      { opacity: 1, transform: 'translateY(0)' },
    ],
    { duration, delay: Math.min(index, 3) * 60, fill: 'backwards' },
  );
}

function observeSections() {
  if (reducedMotion.matches || !('IntersectionObserver' in window)) return;
  observer?.disconnect();
  observer = new IntersectionObserver(
    (entries) => {
      let index = 0;
      for (const entry of entries) {
        const element = entry.target as HTMLElement;
        if (entry.isIntersecting && !seen.has(element) && !element.hidden)
          reveal(element, index++);
      }
    },
    { threshold: 0.08, rootMargin: '0px 0px -40px 0px' },
  );
  for (const target of targets) {
    if (seen.has(target)) continue;
    if (target.getBoundingClientRect().top < window.innerHeight) {
      seen.add(target);
      continue;
    }
    observer.observe(target);
  }
}

function arrive() {
  if (
    reducedMotion.matches ||
    document.documentElement.classList.contains('intro-active')
  )
    return;
  if (window.location.hash || window.scrollY > 0) return;
  const lead = document.querySelector(
    '.hero-copy, .page-lead, .projects-heading, .project-case__intro',
  );
  if (lead)
    play(lead, [{ transform: 'translateY(12px)' }, { transform: 'none' }], {
      duration: 480,
    });
  const portrait = document.querySelector('.hero-portrait');
  if (portrait)
    play(portrait, [{ transform: 'scale(1.015)' }, { transform: 'scale(1)' }], {
      duration: 600,
    });
}

function revealHash() {
  if (!window.location.hash) return;
  const target = document.querySelector(':target');
  if (target) cancelFor(target);
}

document.addEventListener('focusin', (event) => {
  if (event.target instanceof Element) cancelFor(event.target);
});
window.addEventListener('hashchange', revealHash);
document.addEventListener('portfolio:filter-change', () => {
  let index = 0;
  for (const card of document.querySelectorAll<HTMLElement>(
    '[data-project-category]',
  )) {
    cancelAnimationsFor(card);
    if (!card.hidden && isInViewport(card)) reveal(card, index++, 260);
  }
});
reducedMotion.addEventListener('change', () => {
  cancelAll();
  observer?.disconnect();
  if (!reducedMotion.matches) observeSections();
});
window.addEventListener('pagehide', cancelAll);
window.addEventListener('pageshow', (event) => {
  if (!event.persisted) return;
  cancelAll();
  observer?.disconnect();
  for (const target of targets) seen.add(target);
});

arrive();
observeSections();
revealHash();
