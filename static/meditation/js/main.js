// Main JavaScript file

// Theme handling
document.addEventListener('DOMContentLoaded', function() {
    const html = document.documentElement;
    const themeSwitch = document.querySelector('.theme-switcher');
    const themeIcon = document.querySelector('.theme-icon i');

    // Function to set theme
    function setTheme(isDark) {
        const theme = isDark ? 'dark' : 'light';
        
        // Встановлюємо тему
        html.setAttribute('data-theme', theme);
        
        // Оновлюємо класи для body
        document.body.classList.remove('dark-theme', 'light-theme');
        document.body.classList.add(`${theme}-theme`);
        
        // Оновлюємо іконку
        if (themeIcon) {
            themeIcon.classList.remove('fa-sun', 'fa-moon');
            themeIcon.classList.add(isDark ? 'fa-sun' : 'fa-moon');
        }
        
        // Зберігаємо тему в localStorage та cookies
        localStorage.setItem('theme', theme);
        document.cookie = `theme=${theme}; path=/; max-age=31536000; SameSite=Lax`;
        
        // Оновлюємо CSS змінні для фону
        const root = document.documentElement;
        const backgroundColor = isDark ? '#121212' : '#ffffff';
        const contentBgRgb = isDark ? '18, 18, 18' : '255, 255, 255';
        
        // Плавно змінюємо фон
        const background = document.querySelector('.page-background');
        if (background) {
            background.style.transition = 'background-color 0.3s ease-in-out';
            background.style.backgroundColor = backgroundColor;
            
            // Додаємо специфічні стилі для мобільних пристроїв
            if (window.innerWidth <= 768) {
                background.style.position = 'fixed';
                background.style.height = `${window.innerHeight}px`;
                background.style.minHeight = '-webkit-fill-available';
            }
        }
        
        // Оновлюємо CSS змінні
        root.style.setProperty('--page-bg-color', backgroundColor);
        root.style.setProperty('--content-bg-rgb', contentBgRgb);
        
        console.log('Theme changed to:', theme);
    }

    // Check for saved theme preference or use system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme === 'dark');
    } else {
        // Use system preference if no saved theme
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setTheme(prefersDark);
    }

    // Theme switch handler
    if (themeSwitch) {
        themeSwitch.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const isDark = currentTheme === 'light';
            setTheme(isDark);
        });
    }

    // Listen for system theme changes if no saved preference
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches);
        }
    });

    // Handle favorite buttons
    document.querySelectorAll('.favorite-btn')?.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const trackId = this.dataset.trackId;
            const icon = this.querySelector('i');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(`/meditation/track/${trackId}/favorite/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    if (data.is_favorite) {
                        icon.classList.add('text-danger');
                        this.dataset.isFavorite = 'true';
                    } else {
                        icon.classList.remove('text-danger');
                        this.dataset.isFavorite = 'false';
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

// Handle audio player
document.addEventListener('DOMContentLoaded', function() {
    const audioPlayers = document.querySelectorAll('.audio-player');
    
    audioPlayers.forEach(player => {
        const audio = player.querySelector('audio');
        const playBtn = player.querySelector('.play-btn');
        const progressBar = player.querySelector('.progress');
        const timeDisplay = player.querySelector('.time');

        if (playBtn) {
            playBtn.addEventListener('click', () => {
                if (audio.paused) {
                    audio.play();
                    playBtn.textContent = 'Pause';
                } else {
                    audio.pause();
                    playBtn.textContent = 'Play';
                }
            });
        }

        if (audio && progressBar) {
            audio.addEventListener('timeupdate', () => {
                const progress = (audio.currentTime / audio.duration) * 100;
                progressBar.style.width = `${progress}%`;
                
                if (timeDisplay) {
                    const minutes = Math.floor(audio.currentTime / 60);
                    const seconds = Math.floor(audio.currentTime % 60);
                    timeDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                }
            });
        }
    });
});

// Handle mobile menu
document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.querySelector('.menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
            menuButton.classList.toggle('active');
        });
    }
});

// Handle search
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');

    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', (e) => {
            if (!searchInput.value.trim()) {
                e.preventDefault();
            }
        });
    }
});

// Handle form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
});

// Handle notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Mobile viewport height fix
function setAppHeight() {
    const doc = document.documentElement;
    const vh = window.innerHeight * 0.01;
    doc.style.setProperty('--vh', `${vh}px`);
    doc.style.setProperty('--app-height', `${window.innerHeight}px`);
    
    // Додаткова перевірка для iOS
    if (/iPhone|iPad|iPod/.test(navigator.platform)) {
        doc.style.setProperty('--safe-area-inset-top', `${window.screen.height - window.innerHeight}px`);
    }
}

// Викликаємо функцію при завантаженні
window.addEventListener('load', () => {
    setAppHeight();
    handleMobileBackground();
});

// Викликаємо функцію при зміні розміру та орієнтації
['resize', 'orientationchange'].forEach(event => {
    window.addEventListener(event, () => {
        // Затримка для iOS
        setTimeout(() => {
            setAppHeight();
            handleMobileBackground();
        }, 100);
    });
});

// Обробка видимості для складних пристроїв
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        setAppHeight();
        handleMobileBackground();
    }
});

// Обробка фону для мобільних пристроїв
function handleMobileBackground() {
    const background = document.querySelector('.page-background');
    if (background) {
        const isMobile = window.innerWidth <= 768;
        background.classList.toggle('mobile-background', isMobile);
        
        if (isMobile) {
            // Встановлюємо правильну висоту для мобільних пристроїв
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
            
            // Оптимізація для iOS
            if (/iPhone|iPad|iPod/.test(navigator.platform)) {
                background.style.height = `${window.innerHeight}px`;
                background.style.minHeight = '-webkit-fill-available';
            }
            
            // Оптимізація для Android
            if (/Android/.test(navigator.userAgent)) {
                background.style.height = `${window.innerHeight}px`;
                background.style.position = 'fixed';
            }
        } else {
            // Скидаємо стилі для десктопу
            background.style.height = '';
            background.style.minHeight = '';
            background.style.position = '';
        }
    }
}

// Оптимізація для мобільних пристроїв
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        const swUrl = `https://${window.location.hostname}/sw.js`;
        
        navigator.serviceWorker.register(swUrl, { 
            scope: '/',
            updateViaCache: 'none'
        })
        .then(registration => {
            console.log('ServiceWorker registration successful with scope:', registration.scope);
            
            // Оновлення Service Worker
            registration.update();
            
            // Періодичне оновлення
            setInterval(() => {
                registration.update();
            }, 3600000); // Кожну годину
        })
        .catch(err => {
            console.log('ServiceWorker registration failed:', err);
        });
    });
}

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(img => imageObserver.observe(img));
});

// Touch event optimizations
document.addEventListener('DOMContentLoaded', function() {
    const touchElements = document.querySelectorAll('.btn, .card, .feature-card, .meditation-card');
    
    touchElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        }, { passive: true });
        
        element.addEventListener('touchend', function() {
            this.style.transform = 'none';
        }, { passive: true });
    });
});

// Optimize scroll performance
let ticking = false;
window.addEventListener('scroll', function() {
    if (!ticking) {
        window.requestAnimationFrame(function() {
            // Update scroll-based animations here
            ticking = false;
        });
        ticking = true;
    }
}, { passive: true });

// Detect network conditions
function updateForNetworkCondition() {
    if (navigator.connection) {
        const connection = navigator.connection;
        if (connection.saveData || connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
            // Disable animations and effects for slow connections
            document.body.classList.add('reduced-motion');
            document.body.classList.add('save-data');
        }
    }
}

// Check network conditions on load and when they change
if (navigator.connection) {
    updateForNetworkCondition();
    navigator.connection.addEventListener('change', updateForNetworkCondition);
}

// Optimize audio player for mobile
const audioPlayer = document.querySelector('audio');
if (audioPlayer) {
    audioPlayer.addEventListener('play', function() {
        // Request wake lock to prevent screen from sleeping during meditation
        if ('wakeLock' in navigator) {
            navigator.wakeLock.request('screen')
                .catch(err => console.log('Wake Lock error:', err));
        }
    }, { passive: true });
    
    audioPlayer.addEventListener('pause', function() {
        // Release wake lock when audio is paused
        if ('wakeLock' in navigator && navigator.wakeLock) {
            navigator.wakeLock.release()
                .catch(err => console.log('Wake Lock release error:', err));
        }
    }, { passive: true });
}