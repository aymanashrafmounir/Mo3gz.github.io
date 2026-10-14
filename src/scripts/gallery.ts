const viewer = document.querySelector<HTMLDialogElement>('#image-viewer')!;
const canvas = document.querySelector<HTMLDivElement>('#viewer-canvas')!;
const screenshot = document.querySelector<HTMLImageElement>('#viewer-image')!;
const caption =
  document.querySelector<HTMLParagraphElement>('#viewer-caption')!;
const closeButton = document.querySelector<HTMLButtonElement>('#viewer-close')!;
const zoomButtons = [
  ...document.querySelectorAll<HTMLButtonElement>('[data-zoom]'),
];
const pointers = new Map<number, { x: number; y: number }>();
let trigger: HTMLElement | null = null;
let zoom = 1;
let fittedWidth = 0;
let pinchDistance = 0;

function paintZoom() {
  screenshot.style.width = `${fittedWidth * zoom}px`;
  zoomButtons[0].disabled = zoom <= 1;
  zoomButtons[2].disabled = zoom >= 4;
  zoomButtons[1].textContent = `${Math.round(zoom * 100)}%`;
}

function changeZoom(factor: number) {
  zoom = Math.min(4, Math.max(1, factor));
  paintZoom();
}

function fitScreenshot() {
  if (!screenshot.naturalWidth) return;
  const scale = Math.min(
    canvas.clientWidth / screenshot.naturalWidth,
    canvas.clientHeight / screenshot.naturalHeight,
    1,
  );
  fittedWidth = screenshot.naturalWidth * scale;
  changeZoom(1);
}

function openScreenshot(link: HTMLAnchorElement) {
  trigger = link;
  caption.textContent = link.dataset.galleryCaption ?? 'Project screenshot';
  screenshot.alt = caption.textContent;
  screenshot.src = link.href;
  viewer.showModal();
  fitScreenshot();
  closeButton.focus();
}

document
  .querySelectorAll<HTMLAnchorElement>('[data-gallery-image]')
  .forEach((link) => {
    link.addEventListener('click', (event) => {
      if (
        event.ctrlKey ||
        event.metaKey ||
        event.shiftKey ||
        event.altKey ||
        event.button !== 0
      )
        return;
      event.preventDefault();
      openScreenshot(link);
    });
  });
screenshot.addEventListener('load', fitScreenshot);
closeButton.addEventListener('click', () => viewer.close());
viewer.addEventListener('click', (event) => {
  if (event.target === viewer) viewer.close();
});
viewer.addEventListener('close', () => {
  pointers.clear();
  trigger?.focus();
});
zoomButtons.forEach((button) =>
  button.addEventListener('click', () => {
    changeZoom(
      button.dataset.zoom === 'reset'
        ? 1
        : zoom + (button.dataset.zoom === 'in' ? 0.5 : -0.5),
    );
  }),
);
viewer.addEventListener('keydown', (event) => {
  if (event.key === '+' || event.key === '=') changeZoom(zoom + 0.5);
  if (event.key === '-') changeZoom(zoom - 0.5);
});
window.addEventListener('resize', () => {
  if (viewer.open) fitScreenshot();
});

function distanceBetweenPointers() {
  const [first, second] = [...pointers.values()];
  return Math.hypot(first.x - second.x, first.y - second.y);
}

canvas.addEventListener('pointerdown', (event) => {
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  canvas.setPointerCapture(event.pointerId);
  if (pointers.size === 2) pinchDistance = distanceBetweenPointers();
});
canvas.addEventListener('pointermove', (event) => {
  const previous = pointers.get(event.pointerId);
  if (!previous) return;
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  if (pointers.size === 2) {
    const distance = distanceBetweenPointers();
    if (pinchDistance > 0) changeZoom((zoom * distance) / pinchDistance);
    pinchDistance = distance;
  } else if (zoom > 1) {
    canvas.scrollBy(previous.x - event.clientX, previous.y - event.clientY);
  }
});
function releasePointer(event: PointerEvent) {
  pointers.delete(event.pointerId);
  pinchDistance = 0;
}
canvas.addEventListener('pointerup', releasePointer);
canvas.addEventListener('pointercancel', releasePointer);
