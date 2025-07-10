self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open('ofn-v1').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/Nep-Hub.svg',
        '/static/manifest.json',
      ]);
    })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});
