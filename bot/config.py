# config.py
import os

TOKEN = 'vk1.a.C8YkpInT8BNfXpS3Y1nNq1d47R8OAwbmndKLjJyMSSXCC8OCxJ_Q373H1i2cXXkJZ-brzDjPSYox3ZMmJqJRCkyJUbIfomE0WMkMhwNI6acKj73jns7-vBr_-kVvcMOaewb3I4l-fDjPXka110iiinSx_oZlg9kc4aY144fQviIQy1JaZsNzLjs_WA34wFJIaQTyRHcwtPJci7_OptOutg'
GROUP_ID = 240828623

DATA_DIR = os.getenv('DATA_DIR', '/app/data')
DB_NAME = os.path.join(DATA_DIR, 'game.db')

print(f"📁 Путь к базе данных: {DB_NAME}")
