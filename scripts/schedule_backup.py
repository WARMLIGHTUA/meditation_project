#!/usr/bin/env python
import schedule
import time
import subprocess
import logging
from pathlib import Path

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scheduler.log')
    ]
)
logger = logging.getLogger(__name__)

def run_backup():
    """Запуск скрипта бекапу"""
    try:
        backup_script = Path(__file__).parent / 'backup.py'
        subprocess.run(['python', str(backup_script)], check=True)
        logger.info("Бекап успішно виконано")
    except Exception as e:
        logger.error(f"Помилка при виконанні бекапу: {e}")

def main():
    """Головна функція планувальника"""
    # Запускаємо бекап щодня о 3:00 ранку
    schedule.every().day.at("03:00").do(run_backup)
    
    logger.info("Планувальник бекапів запущено")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main() 