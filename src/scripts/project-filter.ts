type Category = 'all' | 'client' | 'public';

const collection = document.querySelector<HTMLElement>(
  '[data-project-collection]',
);

if (collection) {
  const cards = [
    ...collection.querySelectorAll<HTMLElement>('[data-project-category]'),
  ];
  const filters = [
    ...collection.querySelectorAll<HTMLAnchorElement>('[data-project-filter]'),
  ];
  const count = collection.querySelector<HTMLElement>('[data-project-count]')!;

  function categoryFromUrl(): Category {
    const category = new URL(window.location.href).searchParams.get('category');
    return category === 'client' || category === 'public' ? category : 'all';
  }

  function applyCategory() {
    const category = categoryFromUrl();
    for (const card of cards)
      card.hidden =
        category !== 'all' && card.dataset.projectCategory !== category;
    for (const filter of filters) {
      if (filter.dataset.projectFilter === category)
        filter.setAttribute('aria-current', 'true');
      else filter.removeAttribute('aria-current');
    }
    const visibleCount = cards.filter((card) => !card.hidden).length;
    count.textContent = `${visibleCount} ${visibleCount === 1 ? 'project' : 'projects'}`;
  }

  function chooseCategory(event: MouseEvent) {
    if (
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    )
      return;
    const filter = event.currentTarget as HTMLAnchorElement;
    event.preventDefault();
    const destination = new URL(filter.href);
    destination.hash = window.location.hash;
    if (destination.href !== window.location.href)
      window.history.pushState(null, '', destination);
    applyCategory();
  }

  for (const filter of filters)
    filter.addEventListener('click', chooseCategory);
  window.addEventListener('popstate', applyCategory);
  applyCategory();
}
