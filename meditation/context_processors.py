from .models import PageBackground
from django.contrib.auth.models import User

def page_background(request):
    """
    Контекстний процесор для отримання налаштувань фону поточної сторінки
    """
    # Перевіряємо чи це адмін-панель або сторінка додавання/редагування медіа
    if (request.path.startswith('/admin/') or 
        'add' in request.path or 
        'change' in request.path or 
        'upload' in request.path):
        return {
            'page_background': {
                'image': None,
                'video': None,
                'color': '#FFFFFF',
                'opacity': 1
            }
        }
    
    # Визначаємо поточну сторінку з URL
    path = request.path.strip('/').split('/')
    
    # Видаляємо мовний префікс, якщо він є
    if path and path[0] in ['uk', 'en', 'fr']:
        path.pop(0)
    
    # Мапінг URL на сторінки
    url_to_page = {
        '': 'home',
        'tracks': 'tracks',
        'courses': 'courses',
        'workshops': 'workshops',
        'groups': 'groups',
        'events': 'events',
        'favorites': 'favorites',
    }
    
    # Визначаємо поточну сторінку
    current_page = url_to_page.get(path[0] if path else '', 'home')
    
    # Визначаємо поточну тему
    theme = request.COOKIES.get('theme', 'light')
    
    try:
        # Отримуємо налаштування фону для поточної сторінки
        background = PageBackground.objects.get(page=current_page, theme=theme)
        return {
            'page_background': {
                'image': background.background_image.url if background.background_image else None,
                'video': background.background_video.url if background.background_video else None,
                'color': background.background_color,
                'opacity': float(background.background_opacity)
            }
        }
    except PageBackground.DoesNotExist:
        # Якщо налаштування не знайдено, повертаємо значення за замовчуванням
        return {
            'page_background': {
                'image': None,
                'video': None,
                'color': '#FFFFFF',
                'opacity': 1
            }
        } 