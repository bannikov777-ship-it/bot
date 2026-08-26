# run.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import time
import traceback

async def run_with_retry():
    """Запуск с бесконечными попытками"""
    while True:
        try:
            print(f"🚀 Запуск бота в {time.strftime('%H:%M:%S')}")
            from main import main
            await main()
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            traceback.print_exc()
            print("🔄 Перезапуск через 10 секунд...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(run_with_retry())
