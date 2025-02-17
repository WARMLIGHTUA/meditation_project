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
    # Отримуємо дані з .env
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("✗ Помилка: DATABASE_URL не встановлено")
        return False

    print(f"\nСпроба підключення через DATABASE_URL...")
    try:
        # Парсимо URL
        url = urlparse(db_url)
        conn = psycopg2.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            sslmode='require'
        )
        
        # Перевіряємо з'єднання
        with conn.cursor() as cur:
            cur.execute('SELECT version();')
            version = cur.fetchone()[0]
            print(f"✓ Підключення успішне!")
            print(f"✓ Версія PostgreSQL: {version}")
            
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
                
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"✗ Помилка підключення: {str(e)}")
        print("\nСпробуємо через окремі змінні...")
        
        # Спробуємо через окремі змінні
        try:
            conn = psycopg2.connect(
                dbname=os.getenv('PGDATABASE'),
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT'),
                sslmode='require'
            )
            
            with conn.cursor() as cur:
                cur.execute('SELECT version();')
                version = cur.fetchone()[0]
                print(f"✓ Підключення через окремі змінні успішне!")
                print(f"✓ Версія PostgreSQL: {version}")
                
            conn.close()
            return True
            
        except psycopg2.OperationalError as e:
            print(f"✗ Помилка підключення через окремі змінні: {str(e)}")
            return False

if __name__ == "__main__":
    test_connection() 