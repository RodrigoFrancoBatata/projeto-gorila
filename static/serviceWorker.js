
self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open("gorila-cache").then((cache) =>
      cache.addAll([
        "/",
        "/static/style.css",
        "/static/icon-192.png",
        "/static/icon-512.png"
      ])
    )
  );
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});
