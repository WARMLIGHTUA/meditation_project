const CACHE_NAME = 'meditation-app-v1';
const DYNAMIC_CACHE = 'meditation-dynamic-v1';

// Ресурси для попереднього кешування
const PRECACHE_URLS = [
    '/',
    '/uk/',
    '/en/',
    '/fr/',
    '/manifest.json',
    '/static/meditation/css/styles.css',
    '/static/meditation/js/main.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
];

// Встановлення Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(PRECACHE_URLS);
            })
            .catch(error => {
                console.error('Pre-caching failed:', error);
            })
    );
    self.skipWaiting();
});

// Активація Service Worker
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME && cacheName !== DYNAMIC_CACHE) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Перехоплення запитів
self.addEventListener('fetch', event => {
    // Пропускаємо запити до API та адмін-панелі
    if (event.request.url.includes('/admin/') || 
        event.request.url.includes('/api/')) {
        return;
    }

    // Стратегія для HTML-сторінок: Network First
    if (event.request.mode === 'navigate' || 
        (event.request.method === 'GET' && 
         event.request.headers.get('accept').includes('text/html'))) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    const clonedResponse = response.clone();
                    caches.open(DYNAMIC_CACHE).then(cache => {
                        cache.put(event.request, clonedResponse);
                    });
                    return response;
                })
                .catch(() => {
                    return caches.match(event.request)
                        .then(response => {
                            if (response) {
                                return response;
                            }
                            // Якщо сторінка не знайдена в кеші, повертаємо офлайн-сторінку
                            return caches.match('/offline.html');
                        });
                })
        );
        return;
    }

    // Стратегія для статичних ресурсів: Cache First
    if (event.request.url.match(/\.(css|js|png|jpg|jpeg|gif|svg|ico|woff2?)$/)) {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    if (response) {
                        return response;
                    }
                    return fetch(event.request).then(response => {
                        const clonedResponse = response.clone();
                        caches.open(DYNAMIC_CACHE).then(cache => {
                            cache.put(event.request, clonedResponse);
                        });
                        return response;
                    });
                })
        );
        return;
    }

    // Стратегія для інших запитів: Network First
    event.respondWith(
        fetch(event.request)
            .then(response => {
                const clonedResponse = response.clone();
                caches.open(DYNAMIC_CACHE).then(cache => {
                    cache.put(event.request, clonedResponse);
                });
                return response;
            })
            .catch(() => {
                return caches.match(event.request);
            })
    );
}); 