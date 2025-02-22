const CACHE_NAME = 'meditation-app-v3';
const DYNAMIC_CACHE = 'meditation-dynamic-v3';
const S3_DOMAIN = 'meditation-app-storage.s3.eu-north-1.amazonaws.com';

// Ресурси для попереднього кешування
const PRECACHE_URLS = [
    '/',
    '/uk/',
    '/en/',
    '/fr/',
    '/manifest.json',
    '/static/meditation/css/styles.css',
    '/static/meditation/css/animations.css',
    '/static/meditation/js/main.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
];

// Встановлення Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        Promise.all([
            caches.open(CACHE_NAME).then(cache => {
                console.log('Відкрито кеш для попереднього завантаження');
                return cache.addAll(PRECACHE_URLS);
            }),
            caches.delete(DYNAMIC_CACHE) // Очищуємо динамічний кеш при оновленні
        ]).catch(error => {
            console.error('Помилка попереднього кешування:', error);
        })
    );
    self.skipWaiting();
});

// Активація Service Worker
self.addEventListener('activate', event => {
    event.waitUntil(
        Promise.all([
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== CACHE_NAME && cacheName !== DYNAMIC_CACHE) {
                            console.log('Видалення старого кешу:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            self.clients.claim() // Перехоплюємо керування одразу
        ])
    );
});

// Функція для перевірки чи URL вказує на S3
function isS3Request(url) {
    return url.hostname === S3_DOMAIN;
}

// Функція для перевірки чи запит потрібно пропустити
function shouldBypassCache(url) {
    const bypassPatterns = [
        '/admin/',
        '/api/',
        '/events/',
        '/i18n/setlang/',
        'ws://',
        'wss://'
    ];
    
    return bypassPatterns.some(pattern => url.pathname.includes(pattern));
}

// Перехоплення запитів
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);

    // Пропускаємо запити, які не потрібно кешувати
    if (shouldBypassCache(url) || request.method !== 'GET') {
        return;
    }

    // Особлива обробка для S3 ресурсів
    if (isS3Request(url)) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    // Кешуємо тільки успішні відповіді
                    const clonedResponse = response.clone();
                    caches.open(DYNAMIC_CACHE)
                        .then(cache => cache.put(request, clonedResponse))
                        .catch(error => console.error('Помилка кешування S3:', error));
                    return response;
                })
                .catch(error => {
                    console.error('Помилка отримання S3 ресурсу:', error);
                    return caches.match(request)
                        .then(cachedResponse => {
                            return cachedResponse || new Response('Resource not available', {
                                status: 404,
                                statusText: 'Not Found'
                            });
                        });
                })
        );
        return;
    }

    // Стратегія для HTML-сторінок: Network First
    if (request.mode === 'navigate' || 
        (request.method === 'GET' && 
         request.headers.get('accept')?.includes('text/html'))) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    const clonedResponse = response.clone();
                    caches.open(DYNAMIC_CACHE)
                        .then(cache => cache.put(request, clonedResponse))
                        .catch(error => console.error('Помилка кешування HTML:', error));
                    return response;
                })
                .catch(() => {
                    return caches.match(request)
                        .then(response => response || caches.match('/offline.html'));
                })
        );
        return;
    }

    // Стратегія для статичних ресурсів: Cache First, потім Network
    if (request.url.match(/\.(css|js|png|jpg|jpeg|gif|svg|ico|woff2?|webp|mp4)$/)) {
        event.respondWith(
            caches.match(request)
                .then(cachedResponse => {
                    const fetchPromise = fetch(request)
                        .then(networkResponse => {
                            if (!networkResponse.ok) throw new Error('Network response was not ok');
                            const clonedResponse = networkResponse.clone();
                            caches.open(DYNAMIC_CACHE)
                                .then(cache => cache.put(request, clonedResponse))
                                .catch(error => console.error('Помилка кешування ресурсу:', error));
                            return networkResponse;
                        })
                        .catch(error => {
                            console.error('Помилка отримання ресурсу:', error);
                            return cachedResponse;
                        });
                    
                    return cachedResponse || fetchPromise;
                })
        );
        return;
    }

    // Стратегія для інших запитів: Network First з fallback на кеш
    event.respondWith(
        fetch(request)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                const clonedResponse = response.clone();
                caches.open(DYNAMIC_CACHE)
                    .then(cache => cache.put(request, clonedResponse))
                    .catch(error => console.error('Помилка кешування:', error));
                return response;
            })
            .catch(() => {
                return caches.match(request)
                    .then(response => {
                        return response || new Response('Resource not available', {
                            status: 404,
                            statusText: 'Not Found'
                        });
                    });
            })
    );
}); 