// Main JavaScript file

// Theme handling
document.addEventListener('DOMContentLoaded', function() {
    const html = document.documentElement;
    const themeSwitch = document.querySelector('.theme-switcher');
    const themeIcon = document.querySelector('.theme-icon i');

    // Function to set theme
    function setTheme(isDark) {
        const theme = isDark ? 'dark' : 'light';
        html.setAttribute('data-theme', theme);
        document.body.classList.toggle('dark-theme', isDark);
        document.body.classList.toggle('light-theme', !isDark);
        
        // Оновлення іконки
        if (themeIcon) {
            themeIcon.classList.remove('fa-sun', 'fa-moon');
            themeIcon.classList.add(isDark ? 'fa-sun' : 'fa-moon');
        }
        
        // Зберігаємо тему в localStorage та cookies
        localStorage.setItem('theme', theme);
        document.cookie = `theme=${theme}; path=/; max-age=31536000; SameSite=Lax`;
        
        // Перезавантажуємо сторінку для оновлення фону
        window.location.reload();
        
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
            console.log('Theme switch clicked, new theme:', isDark ? 'dark' : 'light');
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

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Використовуємо поточний домен
        const swUrl = `${window.location.origin}/static/meditation/sw.js`;
        
        navigator.serviceWorker.register(swUrl, {
            scope: '/' // Область дії - весь сайт
        })
        .then(registration => {
            console.log('ServiceWorker registration successful with scope:', registration.scope);
        })
        .catch(err => {
            console.log('ServiceWorker registration failed:', err);
        });
    });
}