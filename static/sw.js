// Minimal service worker — enables PWA installability.
// We don't cache pages (data changes constantly) but the browser
// still requires a SW for the "Add to Home Screen" prompt.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(clients.claim()));
