import os
import sys
import psycopg2
from urllib.parse import urlparse
from contextlib import contextmanager

def get_connection_params(url):
    """Отримання параметрів підключення з URL"""
    parsed = urlparse(url)
    return {
        'dbname': parsed.path[1:],
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port,
        'sslmode': 'require',
        'connect_timeout': 30
    }

@contextmanager
def get_db_connection(params):
    """Безпечне створення та закриття з'єднання"""
    conn = None
    try:
        print(f"Спроба підключення до {params['host']}:{params['port']}...")
        conn = psycopg2.connect(**params)
        yield conn
    finally:
        if conn is not None:
            conn.close()

def test_connection():
    # Перевірка наявності змінних середовища
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("✗ Помилка: DATABASE_URL не встановлено")
        return

    # Тестування підключення через DATABASE_URL
    print(f"\nТестування підключення через DATABASE_URL: {db_url}")
    try:
        params = get_connection_params(db_url)
        with get_db_connection(params) as conn:
            print("✓ Підключення через DATABASE_URL успішне!")
            
            # Перевіряємо версію PostgreSQL
            with conn.cursor() as cur:
                cur.execute('SELECT version();')
                version = cur.fetchone()[0]
                print(f"\nВерсія PostgreSQL: {version}")
                
                # Перевіряємо список таблиць
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cur.fetchall()
                print("\nСписок таблиць в базі даних:")
                for table in tables:
                    print(f"- {table[0]}")
    except psycopg2.OperationalError as e:
        print(f"✗ Помилка підключення: {str(e)}")
        print("\nМожливі причини:")
        print("1. Неправильні credentials")
        print("2. Сервер бази даних не доступний")
        print("3. Проблеми з мережею або брандмауером")
        print("4. SSL сертифікат не валідний")
        print("\nПоточні налаштування:")
        print(f"Host: {params['host']}")
        print(f"Port: {params['port']}")
        print(f"Database: {params['dbname']}")
        print(f"User: {params['user']}")
        print(f"SSL Mode: {params['sslmode']}")
    except Exception as e:
        print(f"✗ Неочікувана помилка: {str(e)}")

    # Тестування підключення через окремі змінні
    print("\nТестування підключення через окремі змінні...")
    required_vars = ['PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGHOST', 'PGPORT']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"✗ Відсутні необхідні змінні середовища: {', '.join(missing_vars)}")
        return

    try:
        params = {
            'dbname': os.getenv('PGDATABASE'),
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
            'host': os.getenv('PGHOST'),
            'port': os.getenv('PGPORT'),
            'sslmode': 'require',
            'connect_timeout': 10
        }
        
        with get_db_connection(params) as conn:
            print("✓ Підключення через окремі змінні успішне!")
            
            # Перевіряємо з'єднання
            with conn.cursor() as cur:
                cur.execute('SELECT 1;')
                if cur.fetchone()[0] == 1:
                    print("✓ З'єднання працює коректно")
    except psycopg2.OperationalError as e:
        print(f"✗ Помилка підключення: {str(e)}")
    except Exception as e:
        print(f"✗ Неочікувана помилка: {str(e)}")

if __name__ == "__main__":
    test_connection() 