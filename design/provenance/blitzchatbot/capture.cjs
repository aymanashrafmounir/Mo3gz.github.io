// Preview only: original app components, blank fixtures; no native asset replacement.
const { chromium } = require('D:/Helixtra/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const out = __dirname;
const origin = 'http://127.0.0.1:4187';
const conversation = {
  id: 1, contact_id: 1, phone_number: '', display_name: '',
  is_pinned: false, is_muted: false, is_archived: false, is_unread: false,
  unread_count: 0, last_message_at: null, last_message_body: '',
  last_message_direction: null, last_message_status: null,
  last_message_type: null, last_message_wa_id: null,
  window_open_until: new Date(Date.now() + 3600_000).toISOString(), labels: [],
};

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1,
    colorScheme: 'light', serviceWorkers: 'block',
  });
  const diagnostics = { pageErrors: [], api: [], blocked: [] };
  await context.route('**/*', async route => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname.startsWith('/api/')) {
      const key = url.pathname;
      diagnostics.api.push({ path: key, method: request.method(), mocked: true });
      let data;
      if (request.method() !== 'GET') {
        return route.fulfill({ status: 403, json: { success: false, message: 'Read-only preview' } });
      }
      if (key === '/api/me') data = { username: 'preview', tenant_id: 1 };
      else if (key === '/api/conversations') data = { conversations: [conversation] };
      else if (/^\/api\/conversations\/\d+\/messages$/.test(key)) data = { messages: [] };
      else if (/^\/api\/contacts\/\d+$/.test(key)) data = { id: 1, display_name: '', phone_number: '', labels: [] };
      else if (key === '/api/contacts') data = { contacts: [] };
      else if (key === '/api/labels') data = { labels: [] };
      else if (key === '/api/templates') data = { templates: [] };
      else if (key.startsWith('/api/search/')) data = { search_enabled: false };
      else data = {};
      return route.fulfill({ status: 200, json: { success: true, data } });
    }
    const staticFonts = ['fonts.googleapis.com', 'fonts.gstatic.com', 'cdnjs.cloudflare.com'];
    if (url.pathname.startsWith('/media/') ||
        (url.origin !== origin && !staticFonts.includes(url.hostname))) {
      diagnostics.blocked.push({ origin: url.origin, path: url.pathname });
      return route.abort();
    }
    return route.continue();
  });
  await context.addInitScript(() => {
    class ClosedWebSocket {
      static CONNECTING = 0; static OPEN = 1; static CLOSING = 2; static CLOSED = 3;
      readyState = 3;
      constructor(url) { this.url = String(url); }
      close() {} send() {} addEventListener() {} removeEventListener() {}
      dispatchEvent() { return false; }
    }
    window.WebSocket = ClosedWebSocket;
  });
  const page = await context.newPage();
  page.on('pageerror', error => diagnostics.pageErrors.push(error.message));
  try {
    await page.goto(origin, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForFunction(async () => {
      const { useConversationStore } = await import('/src/store/conversations/store.ts');
      return useConversationStore.getState().conversations.length === 1;
    });
    await page.evaluate(async () => {
      const { useConversationStore } = await import('/src/store/conversations/store.ts');
      useConversationStore.getState().setActiveId(1);
      await document.fonts.ready;
      await document.fonts.load('24px "Material Icons Outlined"');
    });
    await page.waitForTimeout(1800);
    const privacyState = await page.evaluate(async () => {
      const { useConversationStore } = await import('/src/store/conversations/store.ts');
      const { useMessageStore } = await import('/src/store/messages/store.ts');
      return {
        conversations: useConversationStore.getState().conversations,
        activeId: useConversationStore.getState().activeId,
        messages: Object.values(useMessageStore.getState().messagesByConversation).flat(),
        visibleText: document.body.innerText,
        iconFontLoaded: document.fonts.check('24px "Material Icons Outlined"'),
        inputs: [...document.querySelectorAll('input,textarea')].map(n => ({ placeholder: n.placeholder, value: n.value })),
      };
    });
    const safe = privacyState.conversations.every(c =>
      !c.phone_number && !c.display_name && !c.last_message_body && !c.last_message_at && !c.labels?.length);
    if (!safe || privacyState.messages.length || privacyState.inputs.some(n => n.value)) {
      throw new Error('Preview contains conversation data or populated inputs');
    }
    if (!privacyState.iconFontLoaded) throw new Error('Original icon font did not load');
    if (diagnostics.pageErrors.length) throw new Error(diagnostics.pageErrors.join('; '));
    const output = path.join(out, 'blitz-main-chats-desktop-1440.png');
    await page.screenshot({ path: output, fullPage: false, animations: 'disabled' });
    const provenance = {
      capturedAt: new Date().toISOString(), source: 'D:/AQ/BlitzChatbot/project-react',
      state: 'Original main chats layout with one blank synthetic selected conversation and zero messages.',
      method: 'Unmodified isolated frontend; API interception only; original Zustand selection action; no DOM, CSS or image edits.',
      privacy: 'No live backend; all API routes mocked, media blocked, WebSocket disabled, fresh browser profile. Names, numbers, timestamps, labels, previews, messages and input values empty.',
      limits: 'Shows original chat UI only; no delivery, messaging or account workflow verified.',
      viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1,
      output, sha256: crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex'),
      privacyState, diagnostics,
    };
    fs.writeFileSync(path.join(out, 'capture-provenance.json'), JSON.stringify(provenance, null, 2));
    console.log(JSON.stringify({ output, visibleText: privacyState.visibleText, diagnostics }));
  } finally {
    await context.close();
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
