const CACHE_NAME = 'meditation-app-v1';
const STATIC_CACHE_URLS = [
    '/static/meditation/css/styles.css',
    '/static/meditation/js/main.js',
    '/static/meditation/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
    '/manifest.json'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(STATIC_CACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(cacheName => cacheName !== CACHE_NAME)
                        .map(cacheName => caches.delete(cacheName))
                );
            })
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    // Ігноруємо запити до API та інші динамічні запити
    if (event.request.url.includes('/api/') || 
        event.request.url.includes('/admin/') ||
        event.request.method !== 'GET') {
        return;
    }

    // Перевіряємо, чи це запит на статичні файли
    if (event.request.url.includes('/static/') || 
        event.request.url.includes('/manifest.json') ||
        event.request.url.includes('s3.eu-north-1.amazonaws.com')) {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    // Повертаємо з кешу, якщо є
                    if (response) {
                        return response;
                    }
                    
                    // Якщо немає в кеші, завантажуємо з мережі
                    return fetch(event.request.clone())
                        .then(networkResponse => {
                            if (!networkResponse || networkResponse.status !== 200) {
                                return networkResponse;
                            }
                            
                            // Кешуємо новий ресурс
                            const responseToCache = networkResponse.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => {
                                    const headers = new Headers(responseToCache.headers);
                                    headers.append('sw-fetched-on', new Date().toISOString());
                                    return cache.put(event.request, new Response(
                                        responseToCache.body,
                                        {
                                            status: responseToCache.status,
                                            statusText: responseToCache.statusText,
                                            headers: headers
                                        }
                                    ));
                                });
                                
                            return networkResponse;
                        })
                        .catch(() => {
                            // Якщо немає з'єднання, повертаємо offline fallback
                            return caches.match('/static/meditation/offline.html');
                        });
                })
        );
        return;
    }

    // Для всіх інших запитів використовуємо стратегію "Network First"
    event.respondWith(
        fetch(event.request)
            .catch(() => {
                return caches.match(event.request);
            })
    );
}); 