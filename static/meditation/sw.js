const CACHE_NAME = 'meditation-app-v1';
const urlsToCache = [
    '/',
    '/static/meditation/css/styles.css',
    '/static/meditation/js/main.js',
    '/static/meditation/manifest.json',
    '/static/meditation/icons/icon-72x72.png',
    '/static/meditation/icons/icon-96x96.png',
    '/static/meditation/icons/icon-128x128.png',
    '/static/meditation/icons/icon-144x144.png',
    '/static/meditation/icons/icon-152x152.png',
    '/static/meditation/icons/icon-192x192.png',
    '/static/meditation/icons/icon-384x384.png',
    '/static/meditation/icons/icon-512x512.png'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
}); 