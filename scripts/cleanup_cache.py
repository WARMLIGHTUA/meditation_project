import os
import shutil

def cleanup_pycache():
    """Очищення всіх __pycache__ директорій в проекті"""
    count = 0
    total_size = 0
    
    print("Початок очищення __pycache__ директорій...")
    
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                # Отримуємо розмір директорії
                dir_size = sum(os.path.getsize(os.path.join(pycache_path, f)) 
                             for f in os.listdir(pycache_path))
                total_size += dir_size
                
                # Видаляємо директорію
                shutil.rmtree(pycache_path)
                count += 1
                print(f"✓ Видалено: {pycache_path} (розмір: {dir_size/1024:.2f} KB)")
            except Exception as e:
                print(f"✗ Помилка при видаленні {pycache_path}: {str(e)}")
    
    print(f"\nОчищення завершено!")
    print(f"Видалено директорій: {count}")
    print(f"Звільнено місця: {total_size/1024:.2f} KB")

if __name__ == "__main__":
    cleanup_pycache() 