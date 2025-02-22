const CACHE_NAME = 'meditation-app-v2';
const DYNAMIC_CACHE = 'meditation-dynamic-v2';

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
                console.log('Відкрито кеш для попереднього завантаження');
                return cache.addAll(PRECACHE_URLS);
            })
            .catch(error => {
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
            // Очищення динамічного кешу при активації
            caches.open(DYNAMIC_CACHE).then(cache => {
                return cache.keys().then(requests => {
                    return Promise.all(
                        requests.map(request => {
                            // Перевіряємо час кешування
                            return cache.match(request).then(response => {
                                if (response) {
                                    const cachedTime = new Date(response.headers.get('sw-cache-time'));
                                    const now = new Date();
                                    // Видаляємо кеш старший за 1 годину
                                    if ((now - cachedTime) > 3600000) {
                                        return cache.delete(request);
                                    }
                                }
                            });
                        })
                    );
                });
            })
        ])
    );
    self.clients.claim();
});

// Перехоплення запитів
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);

    // Пропускаємо всі запити до адмін-панелі
    if (url.pathname.startsWith('/admin/') || 
        url.pathname.includes('/admin/') ||
        url.pathname.startsWith('/uk/admin/') ||
        url.pathname.startsWith('/en/admin/') ||
        url.pathname.startsWith('/fr/admin/')) {
        return;
    }

    // Пропускаємо запити до API
    if (url.pathname.startsWith('/api/')) {
        return;
    }

    // Пропускаємо POST-запити
    if (request.method !== 'GET') {
        return;
    }

    // Додаємо перевірку для запитів зміни мови
    if (url.pathname.includes('/i18n/setlang/')) {
        return;
    }

    // Стратегія для HTML-сторінок: Network First з розумним кешуванням
    if (request.mode === 'navigate' || 
        (request.method === 'GET' && 
         request.headers.get('accept').includes('text/html'))) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    const clonedResponse = response.clone();
                    caches.open(DYNAMIC_CACHE).then(cache => {
                        // Додаємо час кешування
                        const responseWithTime = new Response(clonedResponse.body, {
                            headers: new Headers({
                                ...Object.fromEntries(clonedResponse.headers.entries()),
                                'sw-cache-time': new Date().toISOString()
                            })
                        });
                        cache.put(request, responseWithTime);
                    });
                    return response;
                })
                .catch(() => {
                    return caches.match(request)
                        .then(response => {
                            if (response) {
                                return response;
                            }
                            return caches.match('/offline.html');
                        });
                })
        );
        return;
    }

    // Стратегія для статичних ресурсів: Cache First з оновленням
    if (request.url.match(/\.(css|js|png|jpg|jpeg|gif|svg|ico|woff2?)$/)) {
        event.respondWith(
            caches.match(request)
                .then(cachedResponse => {
                    const fetchPromise = fetch(request).then(networkResponse => {
                        if (networkResponse.ok) {
                            const clonedResponse = networkResponse.clone();
                            caches.open(DYNAMIC_CACHE).then(cache => {
                                cache.put(request, clonedResponse);
                            });
                        }
                        return networkResponse;
                    });

                    return cachedResponse || fetchPromise;
                })
        );
        return;
    }

    // Стратегія для інших запитів: Network First з таймаутом
    event.respondWith(
        Promise.race([
            fetch(request)
                .then(response => {
                    const clonedResponse = response.clone();
                    caches.open(DYNAMIC_CACHE).then(cache => {
                        cache.put(request, clonedResponse);
                    });
                    return response;
                }),
            new Promise((resolve, reject) => {
                setTimeout(() => {
                    caches.match(request)
                        .then(response => {
                            if (response) {
                                resolve(response);
                            } else {
                                reject(new Error('No cached response found'));
                            }
                        })
                        .catch(reject);
                }, 3000); // 3 секунди таймаут
            })
        ]).catch(() => {
            return caches.match(request);
        })
    );
}); 